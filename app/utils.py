import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture, folder):
    """Guarda una imagen subida por el usuario y devuelve el nombre del archivo"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Definir la ruta de destino según el tipo de imagen
    if folder == 'profile_pics':
        picture_path = os.path.join(current_app.root_path, 'static/images/profile_pics', picture_fn)
    elif folder == 'products':
        picture_path = os.path.join(current_app.root_path, 'static/images/products', picture_fn)
    elif folder == 'categories':
        picture_path = os.path.join(current_app.root_path, 'static/images/categories', picture_fn)
    else:
        picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Redimensionar la imagen
    output_size = (800, 800)  # Tamaño máximo
    i = Image.open(form_picture)
    
    # Mantener la relación de aspecto
    i.thumbnail(output_size)
    
    # Guardar la imagen
    i.save(picture_path)
    
    return picture_fn
