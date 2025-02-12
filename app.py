from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import paypalrestsdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Create instance folder and get absolute path
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Set database path
db_path = os.path.join(instance_path, 'ecommerce.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure PayPal
app.config['PAYPAL_CLIENT_ID'] = os.getenv('PAYPAL_CLIENT_ID')
app.config['PAYPAL_CLIENT_SECRET'] = os.getenv('PAYPAL_CLIENT_SECRET')

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": app.config['PAYPAL_CLIENT_ID'],
    "client_secret": app.config['PAYPAL_CLIENT_SECRET']
})

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200))
    category = db.Column(db.String(50))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return redirect(url_for('products'))

@app.route('/products')
def products():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.all()
    return render_template('products.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related_products = Product.query.filter_by(category=product.category).filter(Product.id != id).limit(4).all()
    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total = 0
    for product_id, quantity in cart_items.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return render_template('cart.html', cart_items=products, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash('Product added to cart!')
    return redirect(url_for('products'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    
    if str(product_id) in cart:
        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            del cart[str(product_id)]
    
    session['cart'] = cart
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.')
                return render_template('login.html')
            login_user(user)
            return redirect(url_for('products'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('products'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('products'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin panel.', 'error')
        return redirect(url_for('home'))
    
    products = Product.query.all()
    orders = Order.query.all()
    users = User.query.all()
    
    # Calculate total revenue
    total_revenue = sum(order.total for order in orders)
    
    return render_template('admin.html', 
                         products=products, 
                         orders=orders, 
                         users=users,
                         total_revenue=total_revenue)

@app.route('/accounts')
@login_required
def account():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('account.html', orders=orders)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        email = request.form.get('email')
        if email and email != current_user.email:
            # Check if email is already taken
            if User.query.filter_by(email=email).first() is None:
                current_user.email = email
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            else:
                flash('Email already exists!', 'error')
    return redirect(url_for('account'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required!', 'error')
        return redirect(url_for('account'))
        
    if not check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect!', 'error')
        return redirect(url_for('account'))
        
    if new_password != confirm_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('account'))
        
    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('account'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = []
    total = 0
    
    # Get cart items from session
    cart = session.get('cart', {})
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    if request.method == 'POST':
        if not cart_items:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('cart'))
            
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": url_for('payment_success', _external=True),
                "cancel_url": url_for('payment_cancel', _external=True)
            },
            "transactions": [{
                "amount": {
                    "total": "{:.2f}".format(total),
                    "currency": "USD"
                },
                "item_list": {
                    "items": [{
                        "name": item['product'].name[:127],  # PayPal has a 127 char limit
                        "sku": str(item['product'].id),
                        "price": "{:.2f}".format(item['product'].price),
                        "currency": "USD",
                        "quantity": item['quantity']
                    } for item in cart_items]
                },
                "description": "Purchase from Our E-commerce Store"
            }]
        })

        try:
            if payment.create():
                # Payment created successfully
                for link in payment.links:
                    if link.rel == "approval_url":
                        # Store payment ID in session
                        session['payment_id'] = payment.id
                        return redirect(link.href)
            else:
                # Log the error for debugging
                app.logger.error(f"Failed to create PayPal payment: {payment.error}")
                flash(f'Payment creation failed: {payment.error}', 'error')
        except Exception as e:
            # Log any exceptions
            app.logger.error(f"Exception in PayPal payment creation: {str(e)}")
            flash(f'Payment error: {str(e)}', 'error')
            
        return redirect(url_for('cart'))
            
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/checkout/success')
@login_required
def checkout_success():
    # Clear the cart after successful checkout
    session['cart'] = {}
    return render_template('checkout_success.html')

@app.route('/payment/success')
@login_required
def payment_success():
    payment_id = session.get('payment_id')
    if not payment_id:
        flash('No payment found!', 'error')
        return redirect(url_for('cart'))
        
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": request.args.get('PayerID')}):
        # Payment successful, create order
        cart_items = []
        total = 0
        cart = session.get('cart', {})
        
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
        
        # Create order
        order = Order(
            user_id=current_user.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            postal_code=request.form.get('postal_code'),
            country=request.form.get('country'),
            status='completed',
            total=total
        )
        db.session.add(order)
        
        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(order_item)
            
            # Update product stock
            product = item['product']
            product.stock -= item['quantity']
            
        # Clear cart
        session['cart'] = {}
        
        db.session.commit()
        flash('Payment successful! Your order has been placed.', 'success')
        return redirect(url_for('account'))
    else:
        app.logger.error(f"Failed to execute PayPal payment: {payment.error}")
        flash(f'Payment execution failed: {payment.error}', 'error')
        return redirect(url_for('cart'))

@app.route('/payment/cancel')
def payment_cancel():
    flash('Payment cancelled.', 'info')
    return redirect(url_for('cart'))

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('admin'))

    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    category = request.form['category']
    
    # Handle image upload
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        image=image_filename
    )
    
    db.session.add(product)
    db.session.commit()
    
    flash('Product added successfully!')
    return redirect(url_for('admin'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('You do not have permission to delete products.', 'error')
        return redirect(url_for('home'))
    
    product = Product.query.get_or_404(product_id)
    
    # Delete product image if it exists
    if product.image:
        image_path = os.path.join(app.root_path, product.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/toggle_user/<int:user_id>', methods=['POST'])
@login_required
def toggle_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('admin'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating admin accounts
    if user.is_admin:
        flash('Admin accounts cannot be deactivated.')
        return redirect(url_for('admin'))
        
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'User {user.username} has been {"activated" if user.is_active else "deactivated"}.')
    return redirect(url_for('admin'))

@app.route('/edit_product/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('admin'))

    product = Product.query.get_or_404(product_id)
    
    # Update basic information
    product.name = request.form['name']
    product.description = request.form['description']
    product.price = float(request.form['price'])
    product.stock = int(request.form['stock'])
    product.category = request.form['category']
    
    # Handle image upload
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        if file and allowed_file(file.filename):
            # Delete old image if it exists
            if product.image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(product.image))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename  # Store just the filename, not the full path
    
    db.session.commit()
    flash('Product updated successfully!')
    return redirect(url_for('admin'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    with app.app_context():
        # Only create tables if they don't exist
        if not os.path.exists(db_path):
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('root'),
                is_admin=True
            )
            db.session.add(admin)
            
            # Add sample products
            sample_products = [
                {
                    'name': 'Smartphone',
                    'description': 'Latest model smartphone with high-end features',
                    'price': 699.99,
                    'stock': 50,
                    'category': 'Electronics'
                },
                {
                    'name': 'Laptop',
                    'description': 'Powerful laptop for work and gaming',
                    'price': 1299.99,
                    'stock': 30,
                    'category': 'Electronics'
                },
                {
                    'name': 'Running Shoes',
                    'description': 'Comfortable running shoes for athletes',
                    'price': 89.99,
                    'stock': 100,
                    'category': 'Clothing'
                },
                {
                    'name': 'Coffee Maker',
                    'description': 'Automatic coffee maker with timer',
                    'price': 49.99,
                    'stock': 75,
                    'category': 'Home & Garden'
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
        
    app.run(debug=True)
