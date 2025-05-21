from flask import Blueprint, render_template, request, current_app
from app.models.product import Product, Category
from app.forms import SearchForm

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()
    sale_products = Product.query.filter(Product.sale_price.isnot(None)).limit(8).all()
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('home.html', 
                           title='Inicio', 
                           featured_products=featured_products,
                           sale_products=sale_products,
                           categories=categories)

@main.route('/about')
def about():
    return render_template('about.html', title='Acerca de Nosotros')

@main.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('query', '')
    category_id = request.args.get('category', 0, type=int)
    page = request.args.get('page', 1, type=int)
    
    # Configurar opciones de categoría para el formulario
    categories = Category.query.all()
    form.category.choices = [(0, 'Todas las categorías')] + [(c.id, c.name) for c in categories]
    form.query.data = query
    form.category.data = category_id
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            Product.name.ilike(f'%{query}%') | 
            Product.description.ilike(f'%{query}%') |
            Product.brand.ilike(f'%{query}%')
        )
    
    if category_id > 0:
        products_query = products_query.filter_by(category_id=category_id)
    
    products = products_query.paginate(page=page, per_page=current_app.config['ITEMS_PER_PAGE'])
    
    return render_template('search.html', 
                           title='Resultados de búsqueda', 
                           form=form, 
                           products=products,
                           query=query)
