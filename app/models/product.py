from app import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    image = db.Column(db.String(100), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Relaciones
    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __repr__(self):
        return f"Category('{self.name}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(100), nullable=False, default='default_product.jpg')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    brand = db.Column(db.String(50), nullable=True)
    sku = db.Column(db.String(20), unique=True, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relaciones
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    images = db.relationship('ProductImage', backref='product', lazy=True)
    
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price
    
    def current_price(self):
        return self.sale_price if self.is_on_sale() else self.price
    
    def discount_percentage(self):
        if self.is_on_sale():
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    def __repr__(self):
        return f"Product('{self.name}', ${self.price})"

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(100), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __repr__(self):
        return f"ProductImage('{self.image_file}', Product ID: {self.product_id})"
