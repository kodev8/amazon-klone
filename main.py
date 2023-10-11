from flask import Flask, render_template, url_for, redirect, session, request, flash, abort
from helper import htmx_redirect, htmx_request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import SECRET_KEY, SQL_LITE, client, products, carts, categories
from werkzeug.security import check_password_hash, generate_password_hash
from forms import LoginForm, RegisterForm, AccountForm,  ResetPasswordForm, AddressForm, CServForm
from models import *
from sub.Product import Product
from sub.Cart import Cart
from datetime import timedelta
import re
import locale
locale.setlocale( locale.LC_ALL, '' )
# is there a difference when requesting several small files vs 1 large file ?

# APP CONFIG
app = Flask(__name__, static_folder='./static')
app.secret_key = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = SQL_LITE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=5)


# CREATE INSTANCE OF FLASK_SQL_ALCHEMY and MARSHMALLOW
db.init_app(app)


cache = {}

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.login_message = ''

@login_manager.user_loader
def user_loader(user_id):
    return User.get_by_id(user_id)

# remove arguments from search filter so when a new search/filter is made it is updated correctly
@app.template_filter('filter_args')
def filter_args(args, *args_to_remove):
    args = dict(args)
    for arg in args_to_remove:
        if arg in args:
            del args[arg]
    return args

# ===================== MIDDLEWARE===========
# SESSION
@app.before_request
def manage_session():

    # session.clear()

    # maybe get location *
    # if not session.get('default_location'):
    #    print(request.remote_addr, request.headers.get('X-FORWARDED-FOR'))
        # session['default_location'] = get_location()
    
    # if the user is not authenticated they use a session cart rather than from the db
    if not session.get('cart') and current_user.is_anonymous:
        # array of Products
        session['cart']=  []

    # create a permanent session to persist even when the browser closes
    if not session.get('PERMANENT_SET'):
        app.logger.info('Permnanet session created')
        session['PERMANENT_SET'] = True
        session.permanent = True

# CACHE
def create_cache(request, template):
    cache_check = (request.url, request.method)
    if not cache.get(cache_check):
        app.logger.info(f'ADDDING {cache_check}TO CACHE')
        # cache[cache_check] = template
        
@app.before_request
def get_cache():
    cache_check = cache.get((request.url, request.method))
    if cache_check is not None:
        app.logger.info(f'GETTING : {request.url}  - {request.method} from CACHE')

        return cache_check
    
# prevent caching pages on logout
@app.after_request
def after_request(response):   
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# GLOBAL LOGGING
# @app.before_request
# def log_requests():
#     # app.logger.info(f'REQUEST HEADERS: {request.headers}\n')
#     app.logger.info(f'REQUEST METHOD: {request.method} - URL: { request.url}\n')

# @app.after_request
# def log_responses_global(response):
#     app.logger.info(f'RESPONSE STATUS: {response.status}')
#     return response

# @app.after_request
# def log_login_responses(response):
#     if request.endpoint == 'login':
#         app.logger.info(f'LOGIN REQUEST STATUS: {response.status}\n', request.method)

#     return response


# set up 404 page
@app.errorhandler(404)
def ab_not_found(e):
    return render_template('pages/404.html')

# allow htmx to redirect to this 404
@app.route('/404', methods=['GET'])
def not_found():
    return abort(404)

# =============== INDEX PAGE ===================== --working
@app.route('/', methods=['GET'])
def index():
    template = render_template('pages/index.html', categories=categories.find())
    if request.args.get('ref'):
        # initial index page might have a user specific notifaction
        create_cache(request, template)
    return template

# ================= REGISTER ===================== --working
@app.route('/register', methods=['GET'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    template = render_template('pages/register.html', form=form)
    create_cache(request, template)
    return template
    
@app.route('/register', methods=['POST'])
@htmx_request
def register_request():
    
    form = RegisterForm()

    if not form.validate_on_submit():
        return render_template('htmx/form-errors.html', errors=form.errors), 401

    email = form.email.data

    query = db.select(User).filter_by(email=email) 
    existing_user = db.session.scalars(query).first()

    if existing_user:
        return render_template('htmx/notif.html', message='A user with this email already exists', type='error')
    
    user_obj = User()
    
    form.populate_obj(user_obj)
    user_obj.password = generate_password_hash(user_obj.password)

    db.session.add(user_obj)
    db.session.commit()

    login_user(user_obj)

    # create a new mongo db cart for the user on registration
    carts.insert_one({
        'user_id': user_obj.id, 
        'products': []
        })
    
    flash(f'Welcome, {user_obj.fname} ', 'success')
    return htmx_redirect(url_for('index'))

# =====================LOGIN ============================= --working
@app.route('/login', methods=['GET'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    template = render_template('pages/login.html', form=form)
    create_cache(request, template)
    return template

@app.route('/login', methods=['POST'])
@htmx_request
def login_request():

    form = LoginForm()

    if not form.validate_on_submit():
        return render_template('htmx/form-errors.html', errors=form.errors), 401


    email= form.email.data
    password = form.password.data

    existing_user = User.get_by_email(email)
  
    if not existing_user or not check_password_hash(existing_user.password, password):
        return render_template('htmx/notif.html', message='Unable To Log in... Check your credentials', type='error'), 401
    
    login_user(existing_user)

    flash(f'Logged in successfully as {existing_user.fname}', 'success')
    red_url = request.args.get('next', url_for('index'))
    
    return htmx_redirect(red_url)
    
# ======================= LOGOUT VIA POST ========================== --working
@app.route('/logout', methods=['POST'])
@htmx_request
@login_required
def logout():

    logout_user()
    session.clear()

    return htmx_redirect(url_for('index', ref='sign-out'))


# =========================  PRODUCTS =====================================
@app.route("/products", methods=["GET"])
def get_products():

    # expected search params
    category = request.args.get('category')
    search = request.args.get('q')
    rating = request.args.get('rating_gt')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')

    # empty store to build the query
    query = {}

    # building the query
    if category:
        query.update({'category':category})

    if search:
        query.update({'title': {'$regex': search, '$options': 'i'}})

    if rating:
        try:
            r = int(rating)
            query.update({'rating':{'$gte':r}})
        except:
            pass

    if price_min and price_max:
        try:
            price_min = float(price_min)
            price_max = float(price_max)

            if price_min < 0 or price_max <  0:
                raise TypeError
            query.update({'$and':[{'price':{'$gte':price_min, '$lte':price_max}}]})
        except:
            print('error')
            pass

    elif price_min:
        try:
            price_min = float(price_min)

            if price_min < 0 :
                raise TypeError
            
            query.update({'price':{'$gte':price_min}})
        except:
            pass

    elif price_max:
        try:
            price_max = float(price_max)
            if price_max < 0 :
                raise TypeError
            query.update({'price':{'$lte':price_max}})
        except:
            pass

    price_ranges = [
        {
            'min':None,
            'max':25.0,
            'display':'$25 & under',
        },
         {
            'min':25.0,
            'max':50.0,
            'display':'$25 to $50'
        },
         {
            'min':50.0,
            'max':100.0,
            'display':'$50 to $100'
        },
         {
            'min':200.0,
            'max':None,
            'display':'$200 & Above'
        }
        ]
    
    # auto_fill is used to fill the left side form on the products page
    auto_fill=False

    # store for which price range should be highlighted based on the request
    highlight = None

    # store for which price range should be highlighted based on the request
    star_underline = None

    # check it this request is from htmx, if it isn't no highlighting etc should be done
    if 'hx-trigger' in request.headers:
        if (price_min or price_max):
                # price-f5 is the form on the products page
                if request.headers['hx-trigger'].strip().lower() =='price-f5':
                    auto_fill=True

                # set the highlighted price range to the trigger
                # else:
                #     highlight = request.headers['hx-trigger']
    if rating:
        star_underline = int(rating)

    for i, price_range in enumerate(price_ranges,1):
        print('')
        if (price_min==price_range['min']) and(price_max==price_range['max']):
            price_range['active'] = True
            print('ACTIVE: ', price_range['active'] )
            break
    
    # dump the products found to Product object
    res_products = [Product.dump(product) for product in products.find(query)]

    # CHANGE
    # convert Immutable Dict to regular dict which is updated for each filter link 
    current_args = dict(request.args)
    print('HIGHLIGHTT: ', highlight)

    template = render_template("pages/products/products.html", products=res_products, price_ranges=price_ranges,
                               auto_fill=auto_fill, highlight=highlight, star_underline=star_underline, current_args=current_args)
    
    # cache frequent search results
    create_cache(request, template)

    return template

# ======================= PRODUCT ===================================
@app.route("/product", methods=["GET"])
def product():
    product_id = request.args.get('product')

    if not id:
        return redirect(request.referrer)
    
    try:
        # using product class to instantiate a new product, raises an error if the product is not found
        product = Product(product_id)
        return render_template('pages/products/product.html', product=product)
    
    except Exception as e:
        # *** test if flash works here 
        flash(e, 'error')
        return redirect(abort(404))

# carts are just arrays of Product object/dicts, Cart class helps to retrieve cart info from session or db
# ====================== BREAK CART ===================================
@app.route("/cart", methods=['GET'])
def cart():

    cart = Cart.load_cart()

    suggested = set()

    # these should be instances of the Product object or dict in the case of anonymous
    exclude_ids =[product.get('_id') for product in cart]
    
    # generate 3 random products to display on suggested tab -- these are products that are not in the users cart already
    # not sure if mongo db sample returns unqiue values
    count = 0 # for max 10 checks
    while len(suggested) < 3 and count < 10:
        count+=1
        random_product = list(products.aggregate([
        { '$match': { '_id': { '$nin': exclude_ids } } }, 
        { '$sample': { 'size': 1 } } 
        ]))

        # check if any product is remaining to be selected, index it since aggregation returns lists
        if not random_product:
            continue
        
        random_product = random_product[0]

        # skip products w no stock left or already found
        if random_product['stock'] <=0:
            continue

        exclude_ids.append(random_product['_id'])
        suggested.add(Product.dump(random_product))

    return render_template('pages/actions/cart.html', cart_products=cart, suggested=suggested)


@app.route("/cart/add/suggested", methods=['POST'])
@htmx_request
def cart_add_suggested():

    product_id = request.form.get('product')
    # set default quantiry to one since 
    quantity = 1

    if not product_id:
        return render_template('htmx/update-cart.html', message='Unable to add product to cart', type='error')

    try:
        product = Product(product_id)
    except:
        return render_template('htmx/update-cart.html', message='Product not found', type='error')
            
    cart = Cart.load_cart()
    cart = Cart.add_product(cart, product, quantity)

    return htmx_redirect(url_for('cart'))

@app.route("/checkout-s", methods=['POST', 'GET'],endpoint='checkout-single')
@app.route("/cart/add", methods=['POST'])
@htmx_request
def cart_add():

    if 'checkout' in request.url and request.method=='GET':
        return htmx_redirect(url_for('cart'))

    """ adds an item to the respective cart"""
    product_id = request.form.get('product')
    quantity = request.form.get('qty')

    if not product_id or not quantity:
        return render_template('htmx/update-cart.html', message='Unable to prcoess this product.', type='error')

    try:
        quantity = int(quantity)
        product = Product(product_id)
    except:
      return render_template('htmx/update-cart.html', message='Unable to prcoess this product.', type='error')

    cart = Cart.load_cart()
    Cart.add_product(cart, product, quantity, how='new')
    cart_count = Cart.count(cart)

    if 'checkout' in request.url:
        temp_prod = product
        temp_prod.qty = quantity
        temp_cart = [temp_prod]
        return checkout(temp_cart=temp_cart)

    return render_template('htmx/update-cart.html', cart_count=cart_count, 
                           as_oob=True, with_banner=True, product=product,quantity=quantity)


@app.route("/cart/delete", methods=['DELETE'])
@htmx_request
def cart_delete():
    """ removes item from a relevent cart """
    try:
        product_id = request.args.get('product')
        
        product = Product(product_id)

        cart = Cart.load_cart()
        Cart.remove_product(cart, product)
        
    except Exception as e:
        flash(e, 'error')
    finally:
        return htmx_redirect(url_for('cart'))

@app.route('/cart-count')
@htmx_request
def cart_count():
    """ returns count of items in a cart whether from session or db"""
    return render_template('htmx/update-cart.html', cart_count=Cart.count(Cart.load_cart()), cart_only=True)

@app.route("/input-cart", methods=['GET'])
@htmx_request
def input_cart():
    """ returns html for swapping max input 10+ to an input field with update button
      NB: js handles sending custom trigger for returned button since event Listener is removed when swapping """
    return render_template('htmx/subtotal.html', input_cart=True)

# *** needs to be cleaned up
@app.route('/cart/update/<string:how>', methods=['POST'])
@app.route('/cart/update', methods=['POST'])
@htmx_request
def selected_subtotal(how=None):
    cart = Cart.load_cart()
    product_id = request.form.get('product')

    if how=='update':
        selected = request.form.get('selected')
        qty = request.form.get('qty')

        target_product = None
        for product in cart:
            if product_id == str(product.get('_id')):
                target_product = product
 
        if target_product:

            if isinstance(target_product, Product):
                target_product.selected = bool(selected)
            else:
                target_product['selected'] = bool(selected)


            if qty:
                try:
                    conv_qty = int(qty)
                    # get prod againt to chec kcurrent stock
                    prod = Product(product_id)
                    
                    if conv_qty > prod.get('stock') or 1 > conv_qty > 30:
                        raise ValueError("Invalid quanty: maximum wholse sale bundles is 30 items per purchase (minimum 1)")
                    
                    Cart.add_product(cart, target_product, conv_qty)

                except Exception as e:
                    return render_template('htmx/subtotal.html', error_message=e)

    elif how == 'all':
        for product in cart:
            if isinstance(product, Product):
                product.selected = True
            else:
                product['selected'] = True
            if current_user.is_authenticated:
                Cart.update_selected_auth(product, True)

    elif how =='none':
        for product in cart:
            if isinstance(product, Product):
                product.selected = False
            else:
                product['selected'] = False
            if current_user.is_authenticated:
                Cart.update_selected_auth(product, False)

    sub_total = locale.currency(Cart.sub_total(cart), grouping=True)
    cart_count = Cart.count(cart)
    return render_template('htmx/subtotal.html', sub_total=sub_total, cart_count=cart_count)

# ===============CHECKOUT=========================
@app.route('/checkout', methods=['GET'])
@login_required
def checkout(temp_cart=None):
    
    cart = temp_cart if temp_cart else Cart.load_cart()

    sub_count = sum(product.get('qty') for product in cart if product.get('selected'))

    # guard against empty cart with checkout
    if sub_count == 0:
        flash('Ensure that you have selected the items you wish to checkout', 'warning')
        return redirect(url_for('cart'))
    
    sub_total = Cart.sub_total(cart)
    shipping = float(sub_total) * Product.SHIPPING
    tax = float(sub_total) * Product.TAX
    pre_tax = float(sub_total) + shipping
    with_tax = pre_tax + tax

    prices={
        'sub_total':float(sub_total),
    'shipping':shipping,
    'pre_tax':pre_tax,
    'tax':tax,
    'with_tax': with_tax
    }

    for price in prices:
        prices[price] = locale.currency(prices[price], grouping=True )

    return render_template('/pages/actions/checkout.html', products=products,sub_count=sub_count,prices=prices )  


@app.route('/pay-method', methods=['GET'])
@htmx_request
@login_required
def pay_method():

    # cannot cache because there is info unique to each user
    return render_template('/pages/actions/pay-method.html')

# ===========================OTHER

@app.route('/search', methods=['GET'])
def search(): 
    """ uses result from search bar to return any matching products"""

    search_query = request.args.get('q')
    if not search_query or search_query.strip() == '':
        return ''

    # escape strings with regexe after noticing errror with searching '('
    search_query = re.escape(search_query.lower().strip())
    db_query = {'title': {'$regex': search_query, '$options': 'i'}}

    # add category to query
    search_category = request.args.get('category')
    if search_category:
        db_query = {'$and':[db_query, {'category':re.escape(search_category)}]}

    # limited to top 10 results and dump them to Product insatnce
    results = [Product.dump(prod) for prod in products.find(db_query).limit(10)]

    template = render_template('htmx/search-results.html', results=results)
    print(template)
    # cache freq search results
    return template

# =============================================================================================
@app.route('/categories')
@htmx_request
def get_categories():
    res_cats = [*categories.find({}, {'title': 1, 'key': 1})]
    
    # only set active category when coming from /product or /products
    pattern = re.compile(f"^{url_for('product', _external=True)}s?")
    active_category = request.args.get('active_category') if re.search(pattern, request.referrer) else None
    template = render_template('htmx/search-categories.html', categories=res_cats, active_category=active_category)

    # we can cache since the url would change for each active category and it is nto expected to change
    create_cache(request, template)
    return template

# ACCOUNT ==========================
@app.route("/account", methods=["GET"])
def account():
    return render_template('pages/account/account.html')

@app.route('/account/update', methods=['GET'])
@login_required
def account_update(): 

    form = AccountForm(obj=current_user)
    return render_template('pages/account/update.html', form=form, title='Login & Security')
        

@app.route('/account/update', methods=['PATCH'])
@login_required
@htmx_request
def account_update_submit():
    form = AccountForm()
    
    if not form.validate_on_submit():
        return render_template('htmx/form-errors.html', errors=form.errors)

    existing_user = User.get_by_email(username=form.email.data)
    
    if existing_user and existing_user.id != current_user.id:
        return render_template('htmx/notif.html', message='A user with this username already exists', type='error')

    change = False
    message = 'No changes made'
    for field in form:
        att = getattr(current_user, field.id, None)
        if  att and field.data != att:
            change=True

    if not change:
        return render_template('htmx/notif.html', message='No changes made', type='success')
    form.populate_obj(current_user)
    db.session.commit()
    message='Profile updated'

    # flash(message, 'success')
    # return htmx_redirect(url_for('account_update'))
    return render_template('pages/account/update.html', form=form, title='Login & Security', message=message, type='success')

@app.route('/account/customer-service', methods=['GET'])
@login_required
def account_cserv(): 

    form = CServForm(obj=current_user)
    return render_template('pages/account/cserv.html', form=form, title='Customer Service')

@app.route('/account/customer-service', methods=['POST'])
@htmx_request
@login_required
def account_cserv_submit(): 
    form = CServForm()
    
    if not form.validate_on_submit():
        return render_template('htmx/form-errors.html', errors=form.errors)

    # some sort of mail sending here
    # ...
    return render_template('htmx/notif.html', message='Your message has been sent, thank you for sharing your concerns', type='success')


# ACCOUNT PAGE
@app.route('/account/address', methods=['GET'])
@login_required
def account_address(): 
    template = render_template('pages/account/address.html', title='Address',)
    return template

# OPENS MODALS
@app.route('/address/<string:update>', methods=['GET', 'POST'])
@htmx_request
def account_address_anon(update):

    # TODO: allow change  
    form=AddressForm()
    if request.method=='GET':
        if current_user.is_anonymous and update=='add':
            template = render_template('htmx/modals/address-modals.html',update=update, title="Choose your location", form=form) 
            # create_cache(request.url, template)
            return template
        return redirect(url_for('index'))
    
    # testing
    zip = request.form.get('zip_code')
    country = request.form.get('country')
    if zip and zip.strip() != '':
        session['address'] = {
            'city':'',
            'zip_code': zip
        }
    elif country and country.strip().lower() not in ('' ,'choose a country'):
        session['address']= {
            'city':country,
            'zip_code': ''
        }
    return render_template('htmx/update-anon-address.html', address=session.get('address'))

@app.route('/account/address/auth/<string:update>', methods=['GET'])
@htmx_request
@login_required
def account_address_get(update): 
    address_form = AddressForm()

    form_addr = request.args.get('address')
    if update not in ('add', 'edit', 'remove'):
        return htmx_redirect(url_for('account_address'))
    
    if update != 'add':
        if not form_addr:
            return htmx_redirect(url_for('account_address'))

        else:
            query  = db.select(Address).where(db.and_(Address.user==current_user,Address.id == form_addr))
            address = db.session.scalars(query).first() 
            if not address:
                return htmx_redirect(url_for('account_address'))
            
            if update == 'edit':
                address_form = AddressForm(obj=address)
                address_form.address_id = address.id

    template =  render_template('htmx/modals/address-modals.html',update=update, address=address_form if update in('add', 'edit') else address, title=f"{update.title()} an Address")
    # create_cache(request.url, template)
    return template

# HANDLING REQUESTS FOR AN ACCOUNT
@app.route('/account/address/<string:update>', methods=['POST', 'PATCH', 'DELETE'])
@htmx_request
@login_required
def account_address_crud(update): 

    form_addr = request.form.get('address')

    if update not in ('add', 'edit', 'remove', 'default'):
        print('fail by type')
        return htmx_redirect(url_for('account_address'))
    
    form = AddressForm()
    if request.method == 'POST':

        if not form.validate_on_submit():
            return render_template('htmx/form-errors.html', errors=form.errors)
        addr = Address()

        form.populate_obj(addr)
        current_user.addresses.append(addr)
        db.session.commit()
        red_url = request.args.get('next', url_for('account_address'))
        return htmx_redirect(red_url)
               
    query  = db.select(Address).where(db.and_(Address.user==current_user,Address.id == form_addr))
    address = db.session.scalars(query).first()
    if not address:
        print('fail by db search id')
        return htmx_redirect(url_for('account_address'))

    if request.method == 'DELETE':
        db.session.delete(address)
        db.session.commit()
    # pathc
    elif request.method == 'PATCH':
        if update == 'default':
            def_query  = db.select(Address).where(db.and_(Address.user==current_user,Address.is_default))
            def_addr = db.session.scalars(def_query).first()
            if def_addr:
                def_addr.is_default = False
            address.is_default = True
            db.session.commit()

            return htmx_redirect(url_for('account_address'))

        if not form.validate_on_submit():
            return render_template('htmx/form-errors.html', errors=form.errors)
        form.populate_obj(address)
        db.session.commit()

    flash('Addresses updated', 'success')
    return htmx_redirect(url_for('account_address'))



@app.route('/account/orders', methods=['GET'])
@login_required
def account_orders(): 
    cart_count = Cart.count(Cart.load_cart())
    return render_template('pages/account/orders.html', title='Orders', cart_count=cart_count)

@app.route('/account/orders', methods=['POST'])
@htmx_request
@login_required
def create_order(): 
    # do some processing
    
    flash('Your order has been sent successfully', 'success')
    return htmx_redirect(url_for('account_orders'))


@app.route('/account/lists/favourites', methods=['GET', 'DELETE', 'POST'])
@login_required
def account_favourites(): 
    for fave in current_user.favourites:
        fave.get_product()
    

    if request.method == 'GET':
        return render_template('pages/account/favourites.html', title='Favourites')
    
    product_id = request.form.get('product')
    if not product_id:
        print('fail by pid')
        return render_template('pages/account/favourites.html', message_only='Could not process the product', type='error')

    product = Product(product_id)
    existing_fave = db.session.scalars(db.select(Favourite).where(db.and_(Favourite.user==current_user, Favourite.product_id==product_id))).first()
        
    
    if request.method == 'POST':
        if existing_fave:
            print('fail by exiting fave post')
            return render_template('pages/account/favourites.html', message_only='This product is already in your favouriites', 
                                   type='error', link= {'url': url_for('account_favourites'), 'text': 'View Your products here'})

        fave = Favourite(product_id=product_id)
        current_user.favourites.append(fave)
        db.session.commit()
        return render_template('pages/account/favourites.html', title='Favourites', message_only='Product added to favouties', 
                               type='success', link= {'url': url_for('account_favourites'), 'text': 'View Your products here'})

    elif request.method =='DELETE':
        if not existing_fave:
            return render_template('pages/account/favourites.html', message_only='There was an issue removieng this item from your favourites', type='error')
        
        db.session.delete(existing_fave)
        db.session.commit()
        return render_template('pages/account/favourites.html', title='Favourites', message='This prodcut has been removed', type='success')

    
@app.route('/close-modal', methods=['GET'])
@htmx_request
# @login_required
def close_modal():
         
    template = render_template('htmx/modals/closed-modal.html')
    # create_cache(request.url, template)

    return template

# RESET PASSWORD
@app.route('/reset-password', methods=['GET', "POST"])
@htmx_request
@login_required
def reset_password(): 

    if request.method=='GET':
        form = ResetPasswordForm()
       
        template = render_template('htmx/modals/reset-password.html',  form=form)
        # create_cache(request.url, template)
        return template

    form = ResetPasswordForm()
    if not form.validate_on_submit():
       
        return render_template('htmx/form-errors.html', errors=form.errors)
        
    if not check_password_hash(current_user.password, form.old_password.data):
        return render_template('htmx/notif.html', message='Old Password is incorrect', type='error')
    
    if check_password_hash(current_user.password, form.password.data):
        return render_template('htmx/notif.html', message='Old Password cannot be the same as new password', type='error')
        
    current_user.password = generate_password_hash(form.password.data)
    db.session.commit()

    flash('Password Updataed Succesfully', 'success')
    return htmx_redirect(request.referrer)

@app.route('/dev-not-imp', methods=['GET','POST'])
@htmx_request
def not_implemented():
    
    template = render_template('htmx/notif.html', message ="Not implemented yet" , type='info')
    # create_cache(request.url, template)
    return template

@app.route('/clear', methods=['GET'])
@htmx_request
def clear():
    return ' '

if __name__ == '__main__':
    app.run(debug=True)

    client.close()
    
    with app.app_context():
        db.session.close()
