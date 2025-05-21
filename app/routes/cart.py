from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from app.models.product import Product
from app.models.order import CartItem, Order, OrderItem
from app.models.user import Address
from app.forms import CheckoutForm
from flask_login import current_user, login_required
from app import db

cart = Blueprint('cart', __name__)

@cart.route('/cart')
def view_cart():
    cart_items = []
    total = 0
    
    if current_user.is_authenticated:
        # Usuario autenticado: obtener items del carrito desde la base de datos
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            total += item.product.current_price() * item.quantity
    else:
        # Usuario anu00f3nimo: obtener items del carrito desde la sesiu00f3n
        if 'cart' in session:
            for item_id, quantity in session['cart'].items():
                product = Product.query.get(int(item_id))
                if product:
                    cart_items.append({'product': product, 'quantity': quantity})
                    total += product.current_price() * quantity
    
    return render_template('cart.html', title='Carrito de Compras', cart_items=cart_items, total=total)

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0 or quantity > product.stock:
        flash('Cantidad no vu00e1lida', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))
    
    if current_user.is_authenticated:
        # Usuario autenticado: guardar en la base de datos
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        
        if cart_item:
            # Actualizar cantidad si el producto ya estu00e1 en el carrito
            cart_item.quantity += quantity
        else:
            # Agregar nuevo item al carrito
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
    else:
        # Usuario anu00f3nimo: guardar en la sesiu00f3n
        if 'cart' not in session:
            session['cart'] = {}
        
        if str(product_id) in session['cart']:
            session['cart'][str(product_id)] += quantity
        else:
            session['cart'][str(product_id)] = quantity
        
        session.modified = True
    
    flash(f'{product.name} agregado al carrito!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    
    if quantity <= 0 or quantity > product.stock:
        flash('Cantidad no vu00e1lida', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        cart_item.quantity = quantity
        db.session.commit()
    else:
        if 'cart' in session and str(product_id) in session['cart']:
            session['cart'][str(product_id)] = quantity
            session.modified = True
    
    flash('Carrito actualizado', 'success')
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
    else:
        if 'cart' in session and str(product_id) in session['cart']:
            del session['cart'][str(product_id)]
            session.modified = True
    
    flash('Producto eliminado del carrito', 'success')
    return redirect(url_for('cart.view_cart'))

@cart.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Verificar si hay items en el carrito
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Tu carrito estu00e1 vacu00edo', 'info')
        return redirect(url_for('cart.view_cart'))
    
    # Calcular total
    total = sum(item.product.current_price() * item.quantity for item in cart_items)
    
    # Obtener direcciones del usuario para el formulario
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    if not addresses:
        flash('Necesitas agregar una direcciu00f3n de envu00edo', 'info')
        return redirect(url_for('auth.new_address'))
    
    form = CheckoutForm()
    form.address_id.choices = [(a.id, f"{a.street}, {a.city}, {a.state}, CP: {a.zipcode}") for a in addresses]
    
    # Establecer la direcciu00f3n predeterminada como seleccionada
    default_address = next((a for a in addresses if a.is_default), addresses[0])
    form.address_id.data = default_address.id
    
    if form.validate_on_submit():
        address = Address.query.get(form.address_id.data)
        address_str = f"{address.street}, {address.city}, {address.state}, CP: {address.zipcode}"
        
        # Crear orden
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            shipping_address=address_str,
            payment_method=form.payment_method.data
        )
        db.session.add(order)
        db.session.flush()  # Para obtener el ID de la orden
        
        # Crear items de la orden
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.current_price()
            )
            db.session.add(order_item)
            
            # Actualizar stock del producto
            product = cart_item.product
            product.stock -= cart_item.quantity
            
            # Eliminar item del carrito
            db.session.delete(cart_item)
        
        db.session.commit()
        flash('u00a1Pedido realizado con u00e9xito!', 'success')
        return redirect(url_for('cart.order_confirmation', order_id=order.id))
    
    return render_template('checkout.html', title='Finalizar Compra', form=form, cart_items=cart_items, total=total)

@cart.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_confirmation.html', title='Confirmaciu00f3n de Pedido', order=order)

@cart.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('orders.html', title='Mis Pedidos', orders=orders)

@cart.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('order_detail.html', title=f'Pedido #{order.id}', order=order)
