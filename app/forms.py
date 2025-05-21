from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models.user import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado. Por favor, utiliza otro.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Actualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Actualizar')
    
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email ya está registrado. Por favor, utiliza otro.')

class AddressForm(FlaskForm):
    street = StringField('Calle y Número', validators=[DataRequired()])
    city = StringField('Ciudad', validators=[DataRequired()])
    state = StringField('Estado', validators=[DataRequired()])
    zipcode = StringField('Código Postal', validators=[DataRequired(), Length(min=5, max=10)])
    is_default = BooleanField('Establecer como dirección predeterminada')
    submit = SubmitField('Guardar Dirección')

class ProductForm(FlaskForm):
    name = StringField('Nombre del Producto', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    price = FloatField('Precio Regular', validators=[DataRequired(), NumberRange(min=0.01)])
    sale_price = FloatField('Precio de Oferta', validators=[])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    brand = StringField('Marca')
    sku = StringField('SKU')
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    image = FileField('Imagen del Producto', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Guardar Producto')

class CategoryForm(FlaskForm):
    name = StringField('Nombre de la Categoría', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    parent_id = SelectField('Categoría Padre', coerce=int, validators=[])
    image = FileField('Imagen de la Categoría', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Guardar Categoría')

class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[DataRequired()])
    category = SelectField('Categoría', coerce=int)
    submit = SubmitField('Buscar')

class CheckoutForm(FlaskForm):
    address_id = SelectField('Dirección de Envío', coerce=int, validators=[DataRequired()])
    payment_method = SelectField('Método de Pago', 
                                choices=[('tarjeta', 'Tarjeta de Crédito/Débito'), 
                                         ('paypal', 'PayPal'), 
                                         ('oxxo', 'OXXO')], 
                                validators=[DataRequired()])
    submit = SubmitField('Completar Compra')
