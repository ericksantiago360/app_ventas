from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddressForm
from app.models.user import User, Address
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets
from PIL import Image
from app.utils import save_picture

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Registro', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Error al iniciar sesión. Verifica tu email y contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('¡Tu cuenta ha sido actualizada!', 'success')
        return redirect(url_for('auth.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Mi Cuenta', image_file=image_file, form=form)

@auth.route('/addresses')
@login_required
def addresses():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('addresses.html', title='Mis Direcciones', addresses=addresses)

@auth.route('/address/new', methods=['GET', 'POST'])
@login_required
def new_address():
    form = AddressForm()
    if form.validate_on_submit():
        address = Address(
            street=form.street.data,
            city=form.city.data,
            state=form.state.data,
            zipcode=form.zipcode.data,
            is_default=form.is_default.data,
            user_id=current_user.id
        )
        
        # Si esta dirección se marca como predeterminada, desmarcar las demás
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        
        db.session.add(address)
        db.session.commit()
        flash('¡Dirección agregada exitosamente!', 'success')
        return redirect(url_for('auth.addresses'))
    return render_template('create_address.html', title='Nueva Dirección', form=form, legend='Nueva Dirección')

@auth.route('/address/<int:address_id>/update', methods=['GET', 'POST'])
@login_required
def update_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != current_user.id:
        abort(403)
    form = AddressForm()
    if form.validate_on_submit():
        address.street = form.street.data
        address.city = form.city.data
        address.state = form.state.data
        address.zipcode = form.zipcode.data
        
        # Si esta dirección se marca como predeterminada, desmarcar las demás
        if form.is_default.data and not address.is_default:
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        address.is_default = form.is_default.data
        
        db.session.commit()
        flash('¡Dirección actualizada exitosamente!', 'success')
        return redirect(url_for('auth.addresses'))
    elif request.method == 'GET':
        form.street.data = address.street
        form.city.data = address.city
        form.state.data = address.state
        form.zipcode.data = address.zipcode
        form.is_default.data = address.is_default
    return render_template('create_address.html', title='Actualizar Dirección', form=form, legend='Actualizar Dirección')

@auth.route('/address/<int:address_id>/delete', methods=['POST'])
@login_required
def delete_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != current_user.id:
        abort(403)
    db.session.delete(address)
    db.session.commit()
    flash('¡Dirección eliminada exitosamente!', 'success')
    return redirect(url_for('auth.addresses'))
