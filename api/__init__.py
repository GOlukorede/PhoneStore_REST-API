from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from .config.config import config_dict
from .utils import db, jwt
from .models.carts import Cart
from .models.cartItems import CartItem
from .models.orderItems import OrderItem
from .models.orders import Order
from .models.products import Product
from .models.users import User, Admin
from .auth.views import auth_namespace
from .admin.views import admin_user_namespace
from .carts.views import cart_namespace
from .products.views import product_namespace
from .cartItems.views import cartItems_namespace
from .orders.views import order_namespace
from .orderItems.views import orderItems_namespace
from .tokenBlockList.views import logout_namespace
from .admin.auth import admin_auth_namespace
from .models.logout import TokenBlockList




def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    
    app.config.from_object(config)
    
    authorizations = {
        "Bearer Auth": {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add a JWT with *** Bearer &lt;JWT&gt; *** to authenticate'
        }
    }
    
    api = Api(app, version='1.0.0', title='Phone Brands Shopping API', 
              description='A RESTful API for shopping phone brands, \
                  providing endpoints for, managing products(admin privileges), \
                      browsing products, managing carts, and processing orders.',
              terms_url='/terms', contact='samsongreats@gmail.com', license='MIT',
              authorizations=authorizations, security='Bearer Auth'
              )
    
    db.init_app(app)
    jwt.init_app(app)
    
    migrate = Migrate(app, db)
    
    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(cart_namespace, path='/carts')
    api.add_namespace(product_namespace, path='/products')
    api.add_namespace(cartItems_namespace, path='/cartItems')
    api.add_namespace(order_namespace, path='/orders')
    api.add_namespace(orderItems_namespace, path='/orderItems')
    api.add_namespace(logout_namespace, path='/logout')
    api.add_namespace(admin_auth_namespace, path='/admin/auth')
    api.add_namespace(admin_user_namespace, path='/admin')
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_data):
	    jti = jwt_data['jti']
	
	    token = db.session.query(TokenBlockList).filter(TokenBlockList.jti == jti).scalar()
	
	    return token is not None
 
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        user = Admin.query.filter_by(email=identity).first()
        if user:
            return {
                'role': 'admin',
            }
        return {}
        
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Order': Order,
            'OrderItem': OrderItem,
            'User': User,
            'Product': Product,
            'Cart': Cart,
            'CartItem': CartItem,
            'Admin': Admin,
        }
    
    return app