"""Cálculo de impuestos mexicanos (IVA e IEPS) para App Ventas.

Los precios del catálogo se capturan con impuestos incluidos, como exige la
venta al público en México. Este módulo descompone cada precio en:

    base (valor antes de impuestos) + IEPS + IVA = precio al público

Reglas que se aplican:

* El IEPS se calcula primero, sobre la base.
* La base del IVA incluye el IEPS (art. 18 LIVA).
* El IEPS puede ser ad valorem (porcentaje), cuota fija por unidad de medida
  (pesos por litro o por cigarro) o ambos (cigarros).

Las tasas y cuotas viven en TAX_PROFILES para poder actualizarlas cada año
cuando cambie la Ley de Ingresos / LIEPS. Valores vigentes en 2026: confirmar
con el contador antes de usarlos en producción.
"""

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal('0.01')
SIX = Decimal('0.000001')

IVA_GENERAL = Decimal('0.16')
IVA_FRONTERA = Decimal('0.08')
IVA_CERO = Decimal('0')

# Tipos de IVA que puede tener un perfil
IVA_TASA_GENERAL = 'general'   # 16%, o 8% en región fronteriza
IVA_TASA_CERO = 'cero'         # alimentos básicos, medicinas (art. 2-A LIVA)
IVA_EXENTO = 'exento'          # sin IVA trasladado (art. 9 y 15 LIVA)


@dataclass(frozen=True)
class TaxProfile:
    """Perfil fiscal que se asigna a cada producto."""
    key: str
    label: str
    iva: str = IVA_TASA_GENERAL
    ieps_rate: Decimal = Decimal('0')      # tasa ad valorem, p. ej. 0.08
    ieps_quota: Decimal = Decimal('0')     # pesos por unidad de medida
    ieps_quota_unit: str = ''              # 'litro' o 'cigarro'
    sat_objeto_imp: str = '02'             # c_ObjetoImp del CFDI 4.0
    notes: str = ''


# Catálogo de perfiles fiscales (2026)
TAX_PROFILES = {
    p.key: p for p in [
        TaxProfile('general', 'General (IVA 16%)'),
        TaxProfile('iva_cero', 'Alimentos básicos y medicinas (IVA 0%)',
                   iva=IVA_TASA_CERO,
                   notes='Pan, leche, huevo, frutas, agua natural, enlatados.'),
        TaxProfile('exento', 'Exento de IVA', iva=IVA_EXENTO,
                   sat_objeto_imp='01',
                   notes='Libros, revistas, servicios exentos.'),
        TaxProfile('bebida_azucarada', 'Bebida saborizada con azúcar (IEPS por litro)',
                   ieps_quota=Decimal('3.0818'), ieps_quota_unit='litro',
                   notes='Cuota 2026 por litro.'),
        TaxProfile('bebida_edulcorante', 'Bebida con edulcorantes no calóricos (IEPS por litro)',
                   ieps_quota=Decimal('1.50'), ieps_quota_unit='litro',
                   notes='Nueva en 2026.'),
        TaxProfile('bebida_energizante', 'Bebida energizante (IEPS 25%)',
                   ieps_rate=Decimal('0.25')),
        TaxProfile('alta_densidad', 'Botanas, dulces y alimentos con ≥275 kcal/100 g (IEPS 8%)',
                   ieps_rate=Decimal('0.08')),
        TaxProfile('alcohol_14', 'Cerveza y bebidas hasta 14° GL (IEPS 26.5%)',
                   ieps_rate=Decimal('0.265')),
        TaxProfile('alcohol_20', 'Bebidas de 14° a 20° GL (IEPS 30%)',
                   ieps_rate=Decimal('0.30')),
        TaxProfile('alcohol_mas_20', 'Bebidas de más de 20° GL (IEPS 53%)',
                   ieps_rate=Decimal('0.53')),
        TaxProfile('cigarros', 'Cigarros (IEPS 200% + cuota por cigarro)',
                   ieps_rate=Decimal('2.00'), ieps_quota=Decimal('0.8516'),
                   ieps_quota_unit='cigarro', notes='Tasa y cuota 2026.'),
        TaxProfile('puros_mano', 'Puros hechos a mano (IEPS 32%)',
                   ieps_rate=Decimal('0.32')),
    ]
}

DEFAULT_PROFILE = 'general'


def profile_choices():
    """Opciones para un SelectField de WTForms."""
    return [(p.key, p.label) for p in TAX_PROFILES.values()]


def get_profile(key):
    return TAX_PROFILES.get(key or DEFAULT_PROFILE, TAX_PROFILES[DEFAULT_PROFILE])


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _dec(value):
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value or 0))


def iva_rate_for(profile, frontera=False):
    if profile.iva == IVA_TASA_GENERAL:
        return IVA_FRONTERA if frontera else IVA_GENERAL
    return IVA_CERO


@dataclass
class LineTaxes:
    """Desglose de una línea (precio unitario × cantidad)."""
    profile: str
    quantity: int
    total: Decimal          # precio con impuestos de la línea
    base: Decimal           # valor antes de impuestos
    ieps: Decimal
    iva: Decimal
    iva_rate: Decimal
    ieps_rate: Decimal
    ieps_quota: Decimal     # cuota total de la línea

    def as_dict(self):
        return {
            'profile': self.profile,
            'quantity': self.quantity,
            'total': float(self.total),
            'base': float(self.base),
            'ieps': float(self.ieps),
            'iva': float(self.iva),
            'iva_rate': float(self.iva_rate),
            'ieps_rate': float(self.ieps_rate),
        }


def breakdown_line(unit_price, quantity=1, profile_key=None,
                   units_per_item=None, frontera=False):
    """Descompone el precio con impuestos de una línea en base, IEPS e IVA.

    unit_price      precio unitario al público, con impuestos incluidos
    quantity        piezas
    profile_key     clave de TAX_PROFILES
    units_per_item  litros por pieza (bebidas) o cigarros por cajetilla;
                    sólo se usa si el perfil tiene cuota de IEPS
    frontera        aplica IVA de 8% en región fronteriza
    """
    profile = get_profile(profile_key)
    qty = int(quantity or 0)
    total = _money(_dec(unit_price) * qty)
    iva_rate = iva_rate_for(profile, frontera)
    ieps_rate = profile.ieps_rate

    quota_total = Decimal('0')
    if profile.ieps_quota:
        units = _dec(units_per_item) if units_per_item else Decimal('1')
        quota_total = profile.ieps_quota * units * qty

    # total = (base * (1 + tasa_ieps) + cuota) * (1 + iva)
    before_iva = total / (1 + iva_rate)
    base = (before_iva - quota_total) / (1 + ieps_rate)
    if base < 0:
        # Precio menor que la propia cuota: no hay base gravable que repartir.
        base = Decimal('0')
        quota_total = before_iva

    base = _money(base)
    ieps = _money(base * ieps_rate + quota_total)
    # El IVA absorbe el redondeo para que la suma cuadre con el precio.
    iva = total - base - ieps

    return LineTaxes(profile=profile.key, quantity=qty, total=total,
                     base=base, ieps=ieps, iva=iva, iva_rate=iva_rate,
                     ieps_rate=ieps_rate, ieps_quota=_money(quota_total))


@dataclass
class OrderTaxes:
    lines: list = field(default_factory=list)
    shipping: LineTaxes = None

    @property
    def subtotal(self):
        """Suma de bases (valor antes de impuestos), incluido el envío."""
        return sum((l.base for l in self._all()), Decimal('0'))

    @property
    def ieps(self):
        return sum((l.ieps for l in self._all()), Decimal('0'))

    @property
    def iva(self):
        return sum((l.iva for l in self._all()), Decimal('0'))

    @property
    def products_total(self):
        return sum((l.total for l in self.lines), Decimal('0'))

    @property
    def shipping_total(self):
        return self.shipping.total if self.shipping else Decimal('0')

    @property
    def total(self):
        return self.products_total + self.shipping_total

    def iva_by_rate(self):
        """IVA agrupado por tasa, como lo pide el CFDI y la declaración."""
        result = {}
        for line in self._all():
            key = line.iva_rate
            base, iva = result.get(key, (Decimal('0'), Decimal('0')))
            result[key] = (base + line.base + line.ieps, iva + line.iva)
        return result

    def _all(self):
        return self.lines + ([self.shipping] if self.shipping else [])


def breakdown_order(items, shipping_cost=0, frontera=False):
    """items: iterable de (producto, cantidad). El envío causa IVA general."""
    order = OrderTaxes()
    for product, quantity in items:
        order.lines.append(breakdown_line(
            product.current_price(), quantity,
            getattr(product, 'tax_profile', None),
            getattr(product, 'ieps_units', None),
            frontera=frontera))
    if shipping_cost:
        order.shipping = breakdown_line(shipping_cost, 1, 'general',
                                        frontera=frontera)
    return order
