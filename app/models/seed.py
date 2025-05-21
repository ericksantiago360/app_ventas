from app import db, bcrypt
from app.models.user import User
from app.models.product import Category, Product
import os

def seed_database():
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
