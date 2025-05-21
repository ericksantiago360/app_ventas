from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from app.models.product import Product, Category
from flask_login import current_user, login_required
from app import db

products = Blueprint('products', __name__)

@products.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product_id).limit(4).all()
    return render_template('product_detail.html', title=product.name, product=product, related_products=related_products)

@products.route('/category/<int:category_id>')
def category(category_id):
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(category_id)
    
    # Obtener subcategorías si las hay
    subcategories = Category.query.filter_by(parent_id=category_id).all()
    
    # Obtener productos de esta categoría
    products = Product.query.filter_by(category_id=category_id).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    
    return render_template('category.html', 
                           title=category.name, 
                           category=category, 
                           subcategories=subcategories, 
                           products=products)

@products.route('/offers')
def offers():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.sale_price.isnot(None)).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    return render_template('offers.html', title='Ofertas', products=products)

@products.route('/featured')
def featured():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(is_featured=True).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    return render_template('featured.html', title='Productos Destacados', products=products)
