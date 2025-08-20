import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime

current_dir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_dir,"shooping.sqlite3")
secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)
app.app_context().push()

#-----------------------------------------------Login user Database----------------------------------------
#-------------------------------------------------------------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

db.create_all()

#----------------------------------------------------Section Database----------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section_type = db.Column(db.String(50), nullable=False) 


#---------------------------------------------------------Product Database-------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacture_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, nullable=False)
    rate_per_unit = db.Column(db.Float, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('products', lazy=True))




db.create_all()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function


#---------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------Login Module-------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('display_products_by_category'))

    return render_template('user_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '54321':
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            #Username already exists
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_login'))

    return render_template('register.html')


@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    return redirect(url_for('user_login'))


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

#-----------------------------------------------------------------------------------------------
#---------------------------------------------Admin Module --------------------------------------
#----------------------------------------------------------------------------------------------

#from your_models_module import Section, Product
@app.route('/admin_dashboard',methods=['GET','POST'])
@admin_required
def admin_dashboard():
    sections = Section.query.all()  
    products = Product.query.all()  
    return render_template('admin_dashboard.html', sections=sections, products=products)

@app.route('/create_section', methods=['GET', 'POST'])
@admin_required
def create_section():
    if request.method == 'POST':
        name = request.form['name']
        section_type = request.form['type']
        section = Section(name=name, section_type=section_type)
        db.session.add(section)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('create_section.html')



@app.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
@admin_required
def edit_section(section_id):
    #Retrive
    section = Section.query.get_or_404(section_id) 

    if request.method == 'POST':
        section.name = request.form['name']
        section.section_type = request.form['type']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_section.html', section=section)




@app.route('/remove_section/<int:section_id>', methods=['GET', 'POST'])
@admin_required
def remove_section(section_id):
    section = Section.query.get_or_404(section_id) 

    if request.method == 'POST':
        db.session.delete(section)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('remove_section.html', section=section)



@app.route('/create_product', methods=['GET', 'POST'])
@admin_required
def create_product():
    sections = Section.query.all()    # Retrieve the list of sections/categories from the database
    if request.method == 'POST':
        name = request.form['name']
        section_id = int(request.form['section'])
        rate_per_unit = float(request.form['rate_per_unit'])

        # Convert manufacture_date and expiry_date strings to Python datetime objects
        manufacture_date_str = request.form['manufacture_date']
        expiry_date_str = request.form['expiry_date']
        manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%dT%H:%M')
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
        quantity = int(request.form['quantity'])

        product = Product(name=name, manufacture_date=manufacture_date, expiry_date=expiry_date, rate_per_unit=rate_per_unit, section_id=section_id,quantity=quantity)
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('create_product.html', sections=sections)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)  
    sections = Section.query.all() 

    if request.method == 'POST':
        product.name = request.form['name']
        product.rate_per_unit = float(request.form['price'])  
        product.quantity = int(request.form['quantity'])
        manufacture_date_str = request.form['manufacture_date']
        expiry_date_str = request.form['expiry_date']
        product.manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%dT%H:%M')
        product.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')

        section_id = int(request.form['section'])

        if any(section.id == section_id for section in sections):
            product.section_id = section_id


        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product, sections=sections)


@app.route('/remove_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def remove_product(product_id):
    product = Product.query.get_or_404(product_id) 

    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('remove_product.html', product=product)



#-----------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------User section Module --------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------


@app.route('/sections')
@user_required
def display_products_by_category():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    sections = Section.query.all()
    products = Product.query.all()
    return render_template('sections.html', sections=sections, products=products,user=user)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@user_required
def add_to_cart(product_id):
    quantity = int(request.form['quantity'])  

    product = Product.query.get_or_404(product_id)
    free_prod=quantity

    cart = session.get('cart', {})
 
    cart = dict((int(key), value) for key, value in cart.items())

    if quantity:
        cart[product_id] = cart.get(product_id, 0) + quantity
        cart[product_id]+=free_prod
    session['cart'] = cart

    return redirect(url_for('display_products_by_category', category_id=product.section_id))
 

@app.route('/cart')
@user_required
def view_cart():
    cart = session.get('cart', {})
    products_in_cart = []

    total_amount = 0
    for product_id, quantity in cart.items():
        product = Product.query.get_or_404(product_id)
        if product.quantity >= quantity:
            total_amount += (product.rate_per_unit//2) * quantity
            products_in_cart.append((product, quantity))


    return render_template('cart.html', products_in_cart=products_in_cart, total_amount=total_amount)

@app.route('/buy', methods=['POST'])
@user_required
def buy_products():
    cart = session.get('cart', {})
    products_in_cart = []
    total_amount = 0

    for product_id, quantity in cart.items():
        product = Product.query.get_or_404(product_id)
        if product.quantity >= quantity:
            product.quantity -= quantity
            total_amount += product.rate_per_unit * quantity
            products_in_cart.append((product, quantity))
            db.session.commit()

    session['cart'] = {}

    return render_template('thankyou.html', products_in_cart=products_in_cart, total_amount=total_amount)

@app.route('/clear', methods=['POST'])
@user_required
def clear_products():
    session['cart'] = {}
    return render_template('cart.html')


@app.route('/search_sections', methods=['GET', 'POST'])
@user_required
def search_sections():
    search_query = request.form.get('search_query')
    if search_query:
       
        sections = Section.query.filter(Section.name.ilike(f"%{search_query}%")).all()
    else:
        sections = []  

    return render_template('search_section.html', sections=sections, search_query=search_query)
@app.route('/add_to_carts/<int:product_id>', methods=['POST'])
@user_required
def add_to_carts(product_id):
    quantity = int(request.form['quantity'])  

    product = Product.query.get_or_404(product_id)

    
    cart = session.get('cart', {})
    
    cart = dict((int(key), value) for key, value in cart.items())

    cart[product_id] = quantity

    session['cart'] = cart


    return redirect(url_for('display_products_by_category'))


@app.route('/search_products', methods=['GET', 'POST'])
@user_required
def search_products():
    search_price = request.form.get('price',)
    search_manufacture_date_str = request.form.get('manufacture_date', '')
    search_expiry_date_str = request.form.get('expiry_date', '')
    search_quantity = request.form.get('quantity')
    search_name = request.form.get('name')
    if search_price:
        search_price=float(search_price)
    else:
        search_price=None
    try:
        search_quantity = int(search_quantity) if search_quantity else None
    except ValueError:
        search_quantity = None

    if search_manufacture_date_str:
        try:
            search_manufacture_date = datetime.strptime(search_manufacture_date_str, '%Y-%m-%d')
        except ValueError:
            search_manufacture_date = None
    else:
        search_manufacture_date = None

    
    
    if search_expiry_date_str:
        try:
            search_expiry_date = datetime.strptime(search_expiry_date_str, '%Y-%m-%d')
        except ValueError:
            search_expiry_date = None
    else:
        search_expiry_date = None


    products = Product.query

    if search_price :
        products = products.filter(Product.rate_per_unit == search_price)
    if search_manufacture_date:
        products = products.filter(Product.manufacture_date >= search_manufacture_date)
    if search_expiry_date:
        products = products.filter(Product.expiry_date >= search_expiry_date)




    if search_quantity is not None:
        products = products.filter(Product.quantity == search_quantity)

    if search_name:
        products = products.filter(Product.name.ilike(f"%{search_name}%"))
    products = products.all()

    return render_template('search_product.html', products=products)

@app.route('/add_to_cartss/<int:product_id>', methods=['POST'])
@user_required
def add_to_cartss(product_id):
    quantity = int(request.form['quantity']) 

    product = Product.query.get_or_404(product_id)

    
    cart = session.get('cart', {})
    
    cart = dict((int(key), value) for key, value in cart.items())

    cart[product_id] =  quantity

    session['cart'] = cart

    return redirect(url_for('search_products'))



if __name__ == '__main__':
    app.run(debug=True)
