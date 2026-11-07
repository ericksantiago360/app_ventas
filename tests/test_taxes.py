import unittest
from decimal import Decimal as D

from app.taxes import breakdown_line, breakdown_order, TAX_PROFILES


class FakeProduct:
    def __init__(self, price, profile='general', units=None):
        self.price = price
        self.tax_profile = profile
        self.ieps_units = units

    def current_price(self):
        return self.price


class BreakdownLineTest(unittest.TestCase):
    def assertAddsUp(self, line):
        self.assertEqual(line.base + line.ieps + line.iva, line.total)

    def test_iva_general_16(self):
        line = breakdown_line(116, 1, 'general')
        self.assertEqual(line.base, D('100.00'))
        self.assertEqual(line.iva, D('16.00'))
        self.assertEqual(line.ieps, D('0'))

    def test_iva_frontera_8(self):
        line = breakdown_line(108, 1, 'general', frontera=True)
        self.assertEqual(line.base, D('100.00'))
        self.assertEqual(line.iva, D('8.00'))

    def test_iva_cero_alimentos(self):
        line = breakdown_line(30, 2, 'iva_cero', frontera=True)
        self.assertEqual(line.base, D('60.00'))
        self.assertEqual(line.iva, D('0.00'))

    def test_exento(self):
        line = breakdown_line(250, 1, 'exento')
        self.assertEqual(line.base, D('250.00'))
        self.assertEqual(line.iva, D('0.00'))

    def test_ieps_tasa_botanas_8(self):
        # 100 * 1.08 * 1.16 = 125.28
        line = breakdown_line(D('125.28'), 1, 'alta_densidad')
        self.assertEqual(line.base, D('100.00'))
        self.assertEqual(line.ieps, D('8.00'))
        self.assertEqual(line.iva, D('17.28'))

    def test_ieps_cerveza(self):
        line = breakdown_line(D('146.74'), 1, 'alcohol_14')  # 100 * 1.265 * 1.16
        self.assertEqual(line.base, D('100.00'))
        self.assertEqual(line.ieps, D('26.50'))
        self.assertAddsUp(line)

    def test_ieps_cuota_refresco_por_litro(self):
        # Refresco de 600 ml a $20: cuota 3.0818 * 0.6 = 1.849
        line = breakdown_line(20, 1, 'bebida_azucarada', units_per_item=0.6)
        self.assertEqual(line.ieps, D('1.85'))
        self.assertEqual(line.base, D('15.39'))
        self.assertEqual(line.iva, D('2.76'))
        self.assertAddsUp(line)

    def test_ieps_cuota_multiplica_por_cantidad(self):
        # 3 botellas de 2 litros: 3.0818 * 2 * 3 = 18.4908
        three = breakdown_line(40, 3, 'bebida_azucarada', units_per_item=2)
        self.assertEqual(three.ieps_quota, D('18.49'))

    def test_cigarros_tasa_mas_cuota(self):
        # Cajetilla de 20: (base * 3 + 20 * 0.8516) * 1.16 = 95
        line = breakdown_line(95, 1, 'cigarros', units_per_item=20)
        expected_base = ((D(95) / D('1.16')) - D('17.032')) / 3
        self.assertEqual(line.base, expected_base.quantize(D('0.01')))
        self.assertAddsUp(line)

    def test_cuota_mayor_que_precio_no_da_base_negativa(self):
        line = breakdown_line(1, 1, 'bebida_azucarada', units_per_item=3)
        self.assertEqual(line.base, D('0'))
        self.assertAddsUp(line)

    def test_perfil_desconocido_usa_general(self):
        line = breakdown_line(116, 1, 'no-existe')
        self.assertEqual(line.profile, 'general')
        self.assertEqual(line.iva, D('16.00'))

    def test_todos_los_perfiles_cuadran(self):
        for key in TAX_PROFILES:
            for price in (D('0.99'), D('17.50'), D('1234.56')):
                with self.subTest(profile=key, price=price):
                    line = breakdown_line(price, 3, key, units_per_item=1)
                    self.assertAddsUp(line)
                    self.assertGreaterEqual(line.iva, 0)


class BreakdownOrderTest(unittest.TestCase):
    def test_pedido_mixto_con_envio(self):
        items = [
            (FakeProduct(116), 1),                         # IVA 16%
            (FakeProduct(30, 'iva_cero'), 2),              # IVA 0%
            (FakeProduct(D('125.28'), 'alta_densidad'), 1)  # IEPS 8%
        ]
        order = breakdown_order(items, shipping_cost=99)
        self.assertEqual(order.products_total, D('301.28'))
        self.assertEqual(order.shipping_total, D('99.00'))
        self.assertEqual(order.total, D('400.28'))
        self.assertEqual(order.subtotal + order.ieps + order.iva, order.total)
        self.assertEqual(order.ieps, D('8.00'))
        by_rate = order.iva_by_rate()
        self.assertEqual(by_rate[D('0')][1], D('0.00'))
        self.assertEqual(by_rate[D('0.16')][1], order.iva)


if __name__ == '__main__':
    unittest.main()
