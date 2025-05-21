from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Asegurar que existe el directorio para subir imágenes
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Registrar blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.products import products
    from app.routes.cart import cart
    from app.routes.admin import admin
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(cart)
    app.register_blueprint(admin)
    
    # Crear base de datos si no existe
    with app.app_context():
        db.create_all()
        from app.models.seed import seed_database
        seed_database()
    
    return app
