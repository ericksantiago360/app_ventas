import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ITEMS_PER_PAGE = 12
    # Envío: gratis a partir de FREE_SHIPPING_MIN (precio con impuestos)
    SHIPPING_COST = 99.0
    FREE_SHIPPING_MIN = 499.0
    # IVA de 8% para emisores inscritos en el estímulo de región fronteriza
    IVA_REGION_FRONTERIZA = os.environ.get('IVA_REGION_FRONTERIZA', '').lower() in ('1', 'true', 'si', 'sí')
