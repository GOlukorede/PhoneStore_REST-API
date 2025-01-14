from flask_restx import Namespace, Resource, fields
from ..models.carts import Cart
from ..models.cartItems import CartItem
from ..models.products import Product
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt
import logging

# Create a logger instance
logger = logging.getLogger(__name__)

cartItems_namespace = Namespace('cartItems', description='Add products to a cart')

cartItems_model = cartItems_namespace.model('CartItem', {
    "id": fields.Integer(description='The cart item unique identifier'),
    "cart_id": fields.Integer(description='ID of the cart to add the product to'),
    # "price": fields.Float(description='Price of the product'),
    "product_id": fields.Integer(required=True, description='ID of the product to add to the cart'),
    "quantity": fields.Integer(required=True, description='Quantity of the product to add to the cart')
})

@cartItems_namespace.route('/add')
class cartItemsResource(Resource):
    @cartItems_namespace.expect(cartItems_model)
    @jwt_required()
    @cartItems_namespace.doc(description="Add a product to a cart before placing an order")
    def post(self):
        """
            Add a product to a cart
        """
        
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            cartItems_namespace.abort(401, {'message': 'Invalid or missing authorization token'})
        user = User.query.filter_by(email=user_email).first()
        if not user:
            cartItems_namespace.abort(404, {'message': 'User not found'})
        user_id = user.id
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            try:
                cart.save()
            except Exception as e:
                logger.error(f"An error occurred while trying to create a cart: {str(e)}")
                cartItems_namespace.abort(500, {'message': 'An unexpected error occurred while trying to create a cart'})

        cart_id = cart.id
        
        data = cartItems_namespace.payload
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id or not quantity:
            cartItems_namespace.abort(400, {'message': 'Product ID and quantity are required'})
        if quantity <= 0:
            cartItems_namespace.abort(400, {'message': 'Quantity must be greater than 0'})
        if not isinstance(quantity, int):
            cartItems_namespace.abort(400, {'message': 'Quantity must be an integer'})
        
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            cartItems_namespace.abort(404, {'message':'Product not found'})
        if product.stock < quantity:
            cartItems_namespace.abort(400, {'message': 'Quantity exceeds available stock or stock is empty'})
        
        #  Calculate the total price of the product
        price = product.price * quantity
        if price <= 0:
            cartItems_namespace.abort(400, {'message': 'Price must be greater than 0'})
        
        # Check if the cart item already exists
        existing_item = CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()
        if existing_item:
            # Update the existing item's quantity
            existing_item.quantity += quantity
            existing_item.price = existing_item.quantity * product.price
            try:
                existing_item.save()
                return {'message': 'Product quantity updated in cart'}, 200
            except Exception as e:
                logger.error(f"An error occurred while trying update product quantity : {str(e)}")
                cartItems_namespace.abort(500, {'message':'An unexpected error occurred while trying to update product quantity'})
        else:
            # Create a new cart item
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, price=price)
            try:
                item.save()
                return {'message': 'Product added to cart'}, 201
            except Exception as e:
                logger.error(f"An error occurred while trying to add product to cart: {str(e)}")
                db.session.rollback()
                cartItems_namespace.abort(500, {'message': 'An unexpected error occurred while trying to add product to cart'})
        
        
        