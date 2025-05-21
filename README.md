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
 