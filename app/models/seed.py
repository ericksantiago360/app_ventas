from app import db, bcrypt
from app.models.user import User
from app.models.product import Category, Product
import os

def seed_database():
    seed_base_data()
    seed_convenience_store()


def seed_base_data():
    # Verificar si ya hay datos en la base de datos
    if User.query.first() is not None:
        return  # La base de datos ya tiene datos
    
    # Crear usuario administrador
    admin = User(
        username='admin',
        email='admin@example.com',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Crear categorías principales
    categories = [
        {'name': 'Electrónica', 'description': 'Productos electrónicos y gadgets'},
        {'name': 'Hogar', 'description': 'Artículos para el hogar y decoración'},
        {'name': 'Ropa', 'description': 'Moda para toda la familia'},
        {'name': 'Calzado', 'description': 'Zapatos, tenis y sandalias'},
        {'name': 'Deportes', 'description': 'Artículos deportivos y fitness'},
        {'name': 'Muebles', 'description': 'Muebles para el hogar y oficina'}
    ]
    
    for cat_data in categories:
        category = Category(**cat_data)
        db.session.add(category)
    
    db.session.commit()
    
    # Crear subcategorías
    subcategories = [
        {'name': 'Smartphones', 'description': 'Teléfonos inteligentes', 'parent_id': 1},
        {'name': 'Laptops', 'description': 'Computadoras portátiles', 'parent_id': 1},
        {'name': 'Televisores', 'description': 'Smart TVs y pantallas', 'parent_id': 1},
        {'name': 'Cocina', 'description': 'Artículos para cocina', 'parent_id': 2},
        {'name': 'Baño', 'description': 'Artículos para baño', 'parent_id': 2},
        {'name': 'Hombres', 'description': 'Ropa para hombre', 'parent_id': 3},
        {'name': 'Mujeres', 'description': 'Ropa para mujer', 'parent_id': 3},
        {'name': 'Niños', 'description': 'Ropa para niños', 'parent_id': 3},
        {'name': 'Tenis', 'description': 'Tenis deportivos y casuales', 'parent_id': 4},
        {'name': 'Sandalias', 'description': 'Sandalias y chanclas', 'parent_id': 4},
        {'name': 'Zapatos formales', 'description': 'Calzado formal', 'parent_id': 4}
    ]
    
    for subcat_data in subcategories:
        subcategory = Category(**subcat_data)
        db.session.add(subcategory)
    
    db.session.commit()
    
    # Crear productos de ejemplo
    products = [
        {
            'name': 'Smartphone XYZ Pro',
            'description': 'Smartphone de última generación con cámara de 108MP y pantalla AMOLED de 6.7"',
            'price': 12999.99,
            'sale_price': 10999.99,
            'stock': 50,
            'brand': 'XYZ',
            'sku': 'SP-XYZ-001',
            'category_id': 7  # Subcategoría Smartphones
        },
        {
            'name': 'Laptop UltraBook',
            'description': 'Laptop ultradelgada con procesador i7, 16GB RAM y SSD de 512GB',
            'price': 18999.99,
            'stock': 25,
            'brand': 'TechPro',
            'sku': 'LT-TP-002',
            'category_id': 8  # Subcategoría Laptops
        },
        {
            'name': 'Smart TV 55"',
            'description': 'Televisor Smart TV 4K de 55 pulgadas con HDR y sistema operativo Android TV',
            'price': 9999.99,
            'sale_price': 8499.99,
            'stock': 30,
            'brand': 'ViewMax',
            'sku': 'TV-VM-003',
            'category_id': 9  # Subcategoría Televisores
        },
        {
            'name': 'Tenis Deportivos Runner',
            'description': 'Tenis para correr con tecnología de amortiguación avanzada',
            'price': 1299.99,
            'sale_price': 999.99,
            'stock': 100,
            'brand': 'SportFlex',
            'sku': 'TN-SF-004',
            'category_id': 15  # Subcategoría Tenis
        },
        {
            'name': 'Sandalias Comfort',
            'description': 'Sandalias cómodas para uso diario con plantilla acolchada',
            'price': 599.99,
            'stock': 80,
            'brand': 'StepEasy',
            'sku': 'SN-SE-005',
            'category_id': 16  # Subcategoría Sandalias
        },
        {
            'name': 'Batería de Cocina 12 piezas',
            'description': 'Juego de ollas y sartenes antiadherentes de alta calidad',
            'price': 2499.99,
            'sale_price': 1999.99,
            'stock': 40,
            'brand': 'KitchenPro',
            'sku': 'KC-KP-006',
            'category_id': 10  # Subcategoría Cocina
        }
    ]
    
    for prod_data in products:
        product = Product(**prod_data)
        db.session.add(product)
    
    db.session.commit()
    
    print('Base de datos inicializada con datos de ejemplo')


# Productos tipo tienda de conveniencia, uno o más por perfil fiscal
# (ver app/taxes.py). Precios al público con impuestos incluidos.
CONVENIENCE_CATEGORIES = {
    'Abarrotes': 'Alimentos básicos con IVA 0%',
    'Bebidas': 'Refrescos, agua, jugos y energizantes',
    'Botanas y dulces': 'Botanas, galletas, dulces y chocolates',
    'Cerveza y licores': 'Cerveza, vinos y destilados',
    'Cigarros': 'Cigarros y tabaco',
    'Revistas y libros': 'Publicaciones exentas de IVA',
    'Higiene y cuidado personal': 'Artículos de higiene con IVA 16%',
}

CONVENIENCE_PRODUCTS = [
    # (sku, nombre, categoría, precio, perfil fiscal, ieps_units, clave SAT, unidad, marca)
    ('CV-LECHE-1L', 'Leche entera 1 L', 'Abarrotes', 29.50, 'iva_cero', None, '50131700', 'H87', 'Lala'),
    ('CV-PAN-680', 'Pan blanco grande 680 g', 'Abarrotes', 52.00, 'iva_cero', None, '50181900', 'H87', 'Bimbo'),
    ('CV-HUEVO-12', 'Huevo blanco 12 piezas', 'Abarrotes', 48.00, 'iva_cero', None, '50131600', 'H87', 'San Juan'),
    ('CV-AGUA-1L', 'Agua natural 1 L', 'Bebidas', 14.00, 'iva_cero', None, '50202301', 'H87', 'Ciel'),
    ('CV-REFRESCO-600', 'Refresco de cola 600 ml', 'Bebidas', 20.00, 'bebida_azucarada', 0.6, '50202306', 'H87', 'Coca-Cola'),
    ('CV-REFRESCO-2L', 'Refresco de cola 2 L', 'Bebidas', 42.00, 'bebida_azucarada', 2.0, '50202306', 'H87', 'Coca-Cola'),
    ('CV-LIGHT-600', 'Refresco sin azúcar 600 ml', 'Bebidas', 20.00, 'bebida_edulcorante', 0.6, '50202306', 'H87', 'Coca-Cola'),
    ('CV-ENERGY-473', 'Bebida energizante 473 ml', 'Bebidas', 42.00, 'bebida_energizante', None, '50202306', 'H87', 'Monster'),
    ('CV-PAPAS-45', 'Papas fritas 45 g', 'Botanas y dulces', 21.00, 'alta_densidad', None, '50192100', 'H87', 'Sabritas'),
    ('CV-CHOCO-40', 'Chocolate con leche 40 g', 'Botanas y dulces', 22.00, 'alta_densidad', None, '50161800', 'H87', 'Carlos V'),
    ('CV-GALLETAS-90', 'Galletas con chispas 90 g', 'Botanas y dulces', 19.00, 'alta_densidad', None, '50181900', 'H87', 'Gamesa'),
    ('CV-CERVEZA-355', 'Cerveza clara lata 355 ml', 'Cerveza y licores', 23.00, 'alcohol_14', None, '50202201', 'H87', 'Tecate'),
    ('CV-CERVEZA-6', 'Cerveza clara six pack 355 ml', 'Cerveza y licores', 128.00, 'alcohol_14', None, '50202201', 'H87', 'Corona'),
    ('CV-VINO-750', 'Vino tinto 750 ml', 'Cerveza y licores', 189.00, 'alcohol_20', None, '50202203', 'H87', 'Casa Madero'),
    ('CV-TEQUILA-750', 'Tequila blanco 750 ml', 'Cerveza y licores', 329.00, 'alcohol_mas_20', None, '50202206', 'H87', 'Jimador'),
    ('CV-CIGARROS-20', 'Cigarros cajetilla 20 piezas', 'Cigarros', 95.00, 'cigarros', 20, '50211500', 'H87', 'Marlboro'),
    ('CV-REVISTA', 'Revista de espectáculos', 'Revistas y libros', 45.00, 'exento', None, '55101500', 'H87', 'TVNotas'),
    ('CV-JABON-150', 'Jabón de tocador 150 g', 'Higiene y cuidado personal', 24.00, 'general', None, '53131608', 'H87', 'Palmolive'),
    ('CV-PANALES-14', 'Pañales etapa 3, 14 piezas', 'Higiene y cuidado personal', 119.00, 'general', None, '53102305', 'H87', 'Huggies'),
]


def seed_convenience_store():
    """Agrega los productos de conveniencia que falten (busca por SKU).

    Se puede correr varias veces sin duplicar datos.
    """
    parent = Category.query.filter_by(name='Tienda de conveniencia').first()
    if parent is None:
        parent = Category(name='Tienda de conveniencia',
                          description='Productos tipo tienda de conveniencia con IVA e IEPS')
        db.session.add(parent)
        db.session.flush()

    categories = {}
    for name, description in CONVENIENCE_CATEGORIES.items():
        category = Category.query.filter_by(name=name).first()
        if category is None:
            category = Category(name=name, description=description, parent_id=parent.id)
            db.session.add(category)
            db.session.flush()
        categories[name] = category

    added = 0
    for sku, name, cat, price, profile, units, sat_key, unit_key, brand in CONVENIENCE_PRODUCTS:
        if Product.query.filter_by(sku=sku).first() is not None:
            continue
        db.session.add(Product(
            sku=sku, name=name, description=f'{name}. Precio con impuestos incluidos.',
            price=price, stock=100, brand=brand, category_id=categories[cat].id,
            tax_profile=profile, ieps_units=units,
            sat_product_key=sat_key, sat_unit_key=unit_key,
        ))
        added += 1

    db.session.commit()
    if added:
        print(f'Seed de tienda de conveniencia: {added} productos agregados')
    return added
