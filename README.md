# E-Commerce App (Inspirado en e-commerce)

Esta es una aplicación de comercio electrónico desarrollada con Python y Flask, inspirada en el diseño y funcionalidad de e-commerce.

## Características

- Catálogo de productos con categorías
- Carrito de compras
- Registro y autenticación de usuarios
- Panel de administración para gestionar productos
- Búsqueda de productos
- Procesamiento de pedidos

## Requisitos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno (crear archivo .env)
6. Inicializar la base de datos: `flask db init`
7. Ejecutar migraciones: `flask db migrate` y `flask db upgrade`
8. Ejecutar la aplicación: `flask run`

## Estructura del Proyecto

- `/app` - Código principal de la aplicación
  - `/static` - Archivos estáticos (CSS, JS, imágenes)
  - `/templates` - Plantillas HTML
  - `/models` - Modelos de datos
  - `/routes` - Rutas y controladores
- `/migrations` - Archivos de migración de la base de datos
- `config.py` - Configuración de la aplicación
- `run.py` - Punto de entrada para ejecutar la aplicación
 
## Impuestos (IVA e IEPS)

Los precios se capturan con impuestos incluidos. `app/taxes.py` los desglosa en
base, IEPS e IVA para el carrito, el checkout y los pedidos.

- Cada producto tiene un **perfil fiscal** (`tax_profile`): IVA 16%, IVA 0%,
  exento, o IEPS (bebidas azucaradas por litro, edulcorantes, energizantes,
  botanas 8%, alcohol por graduación, cigarros con tasa y cuota por cigarro).
- Para IEPS por cuota se captura `ieps_units`: litros por pieza o cigarros por cajetilla.
- `IVA_REGION_FRONTERIZA=1` en `.env` aplica el IVA de 8% de región fronteriza.
- Las tasas y cuotas 2026 están en `TAX_PROFILES`; hay que revisarlas cada año.
- Datos de ejemplo: `flask --app run.py seed` agrega 19 productos de tienda de conveniencia, uno por cada perfil fiscal, sin duplicar los existentes.
- Pruebas: `python -m unittest discover -s tests -t .`
