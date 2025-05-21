from app import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pendiente')
    shipping_address = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    items = db.relationship('OrderItem', backref='order', lazy=True)
    
    def __repr__(self):
        return f"Order(ID: {self.id}, Amount: ${self.total_amount}, Status: {self.status})"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __repr__(self):
        return f"OrderItem(Order ID: {self.order_id}, Product ID: {self.product_id}, Quantity: {self.quantity})"

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __repr__(self):
        return f"CartItem(User ID: {self.user_id}, Product ID: {self.product_id}, Quantity: {self.quantity})"
