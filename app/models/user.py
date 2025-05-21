from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart_items = db.relationship('CartItem', backref='customer', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Address('{self.street}', '{self.city}', '{self.state}')"    
