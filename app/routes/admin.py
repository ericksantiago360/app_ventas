from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from app.models.product import Product, Category, ProductImage
from app.models.user import User
from app.models.order import Order
from app.forms import ProductForm, CategoryForm
from flask_login import current_user, login_required
from app import db
from app.utils import save_picture
import os

admin = Blueprint('admin', __name__)

# Decorador para verificar si el usuario es administrador
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    products_count = Product.query.count()
    users_count = User.query.count()
    orders_count = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pendiente').count()
    
    # Últimos 5 pedidos
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    # Productos con bajo stock
    low_stock_products = Product.query.filter(Product.stock < 10).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           title='Panel de Administración', 
                           products_count=products_count,
                           users_count=users_count,
                           orders_count=orders_count,
                           pending_orders=pending_orders,
                           recent_orders=recent_orders,
                           low_stock_products=low_stock_products)

# Gestión de Productos
@admin.route('/admin/products')
@login_required
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.date_added.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    return render_template('admin/products.html', title='Administrar Productos', products=products)

@admin.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    form = ProductForm()
    
    # Configurar opciones de categoría para el formulario
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            sale_price=form.sale_price.data if form.sale_price.data else None,
            stock=form.stock.data,
            brand=form.brand.data,
            sku=form.sku.data,
            category_id=form.category_id.data
        )
        
        if form.image.data:
            image_file = save_picture(form.image.data, 'products')
            product.image_file = image_file
        
        db.session.add(product)
        db.session.commit()
        flash('¡Producto creado exitosamente!', 'success')
        return redirect(url_for('admin.admin_products'))
    
    return render_template('admin/create_product.html', 
                           title='Nuevo Producto', 
                           form=form, 
                           legend='Nuevo Producto')

@admin.route('/admin/product/<int:product_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    
    # Configurar opciones de categoría para el formulario
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.sale_price = form.sale_price.data if form.sale_price.data else None
        product.stock = form.stock.data
        product.brand = form.brand.data
        product.sku = form.sku.data
        product.category_id = form.category_id.data
        
        if form.image.data:
            image_file = save_picture(form.image.data, 'products')
            product.image_file = image_file
        
        db.session.commit()
        flash('¡Producto actualizado exitosamente!', 'success')
        return redirect(url_for('admin.admin_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.sale_price.data = product.sale_price
        form.stock.data = product.stock
        form.brand.data = product.brand
        form.sku.data = product.sku
        form.category_id.data = product.category_id
    
    return render_template('admin/create_product.html', 
                           title='Actualizar Producto', 
                           form=form, 
                           legend='Actualizar Producto')

@admin.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('¡Producto eliminado exitosamente!', 'success')
    return redirect(url_for('admin.admin_products'))

# Gestión de Categorías
@admin.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', title='Administrar Categorías', categories=categories)

@admin.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    form = CategoryForm()
    
    # Configurar opciones de categoría padre para el formulario
    categories = Category.query.all()
    form.parent_id.choices = [(0, 'Ninguna (Categoría Principal)')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data > 0 else None
        )
        
        if form.image.data:
            image_file = save_picture(form.image.data, 'categories')
            category.image = image_file
        
        db.session.add(category)
        db.session.commit()
        flash('¡Categoría creada exitosamente!', 'success')
        return redirect(url_for('admin.admin_categories'))
    
    return render_template('admin/create_category.html', 
                           title='Nueva Categoría', 
                           form=form, 
                           legend='Nueva Categoría')

@admin.route('/admin/category/<int:category_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    
    # Configurar opciones de categoría padre para el formulario
    categories = Category.query.filter(Category.id != category_id).all()  # Excluir la categoría actual
    form.parent_id.choices = [(0, 'Ninguna (Categoría Principal)')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data > 0 else None
        
        if form.image.data:
            image_file = save_picture(form.image.data, 'categories')
            category.image = image_file
        
        db.session.commit()
        flash('¡Categoría actualizada exitosamente!', 'success')
        return redirect(url_for('admin.admin_categories'))
    elif request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
        form.parent_id.data = category.parent_id if category.parent_id else 0
    
    return render_template('admin/create_category.html', 
                           title='Actualizar Categoría', 
                           form=form, 
                           legend='Actualizar Categoría')

@admin.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Verificar si hay productos o subcategorías asociadas
    if category.products or category.subcategories:
        flash('No se puede eliminar esta categoría porque tiene productos o subcategorías asociadas.', 'danger')
        return redirect(url_for('admin.admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('¡Categoría eliminada exitosamente!', 'success')
    return redirect(url_for('admin.admin_categories'))

# Gestión de Pedidos
@admin.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    orders_query = Order.query
    
    if status_filter:
        orders_query = orders_query.filter_by(status=status_filter)
    
    orders = orders_query.order_by(Order.order_date.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    
    return render_template('admin/orders.html', 
                           title='Administrar Pedidos', 
                           orders=orders, 
                           status_filter=status_filter)

@admin.route('/admin/order/<int:order_id>')
@login_required
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', 
                           title=f'Pedido #{order.id}', 
                           order=order)

@admin.route('/admin/order/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    
    if status in ['Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado']:
        order.status = status
        db.session.commit()
        flash(f'Estado del pedido actualizado a: {status}', 'success')
    else:
        flash('Estado no válido', 'danger')
    
    return redirect(url_for('admin.admin_order_detail', order_id=order.id))

# Gestión de Usuarios
@admin.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.date_joined.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    return render_template('admin/users.html', title='Administrar Usuarios', users=users)
