from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..models.carts import Cart
from ..models.users import User
from ..models.cartItems import CartItem
import logging

# Create a logger instance
logger = logging.getLogger(__name__)


cart_namespace = Namespace('carts', description='Cart related operations')

cart_model = cart_namespace.model('Cart',
{
    "user_id": fields.Integer(description="The ID of the user that owns the cart", required=True)
})

cart_status_model = cart_namespace.model('Cart Status', {
    'id': fields.Integer(),
    'user_id': fields.Integer(required=True, description='ID of the user that owns the cart'),
    'created_at': fields.DateTime(),
    'updated_at': fields.DateTime()
})

cart_item_model = cart_namespace.model('CartItem', {
    "id": fields.Integer(readOnly=True, description='The cart item unique identifier'),
    "cart_id": fields.Integer(required=True, description='ID of the cart to add the product to'),
    "product_id": fields.Integer(required=True, description='ID of the product to add to the cart'),
    "quantity": fields.Integer(required=True, description='Quantity of the product to add to the cart')
})

pagination_model = cart_namespace.model('Pagination', {
    'page': fields.Integer(description='Page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages'),
    'next_page': fields.String(description='Next page URL'),
    'prev_page': fields.String(description='Previous page URL')
})

cart_items_model = cart_namespace.model('CartItems', {
    'cart_items': fields.List(fields.Nested(cart_item_model)),
    'pagination': fields.Nested(pagination_model)
})

@cart_namespace.route('/create_cart')
class CreateCart(Resource):
    # @cart_namespace.expect(cart_model)
    @cart_namespace.marshal_with(cart_status_model)
    @jwt_required()
    @cart_namespace.doc(description="Create a cart for a user")
    def post(self):
        """
            Create a cart for a user
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        user = User.query.filter_by(email=user_email).first()
        if not user:
            cart_namespace.abort(404, f"User not found")
        existing_cart = Cart.query.filter_by(user_id=user.id).first()
        if existing_cart:
            cart_namespace.abort(400, f"Cart already exists for this user with id {user.id}")
        cart = Cart(user_id=user.id)
        if not cart:
            cart_namespace.abort(400, "Failed to create cart. Please try again")
        try:
            cart.save()
            return cart, 201
        except Exception as e:
            logger.error(f"An error occurred while saving created cart for id {user.id}: {str(e)}")
            cart_namespace.abort(500, "An unexpected error occurred while trying to save created cart")
    
@cart_namespace.route('/delete_cart')
class DeleteCart(Resource):
    @jwt_required()
    @cart_namespace.doc(description="Delete a cart for a user with all its items")
    def delete(self):
        """
            Delete a cart for a user
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            cart_namespace.abort(401, "Invalid or missing authorization token")
        user = User.query.filter_by(email=user_email).first()
        if not user:
            cart_namespace.abort(404, f"User not found")
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart_namespace.abort(404, f"Cart not found for user with ID {user.id}")
        try:
            cart.delete()
            return {"message": f"Cart for user with ID {user.id} deleted successfully"}, 200
        except Exception as e:
            logger.error(f"An error occurred while trying to delete cart for user {user_email}: {str(e)}")
            cart_namespace.abort(500, "An unexpected error occurred while trying to delete cart")
        
@cart_namespace.route('/cart_items/all')
class GetAllCartItems(Resource):
    @cart_namespace.marshal_with(cart_items_model)
    @jwt_required()
    @cart_namespace.doc(description="Retrieve all items in a user's cart")
    def get(self):
        """
            Get all items in a cart for a user
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            cart_namespace.abort(401, "Invalid or missing authorization token")
        user = User.query.filter_by(email=user_email).first()
        if not user:
            cart_namespace.abort(404, "User not found")
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart_namespace.abort(404, f"Cart not found for user with ID {user.id}")
        
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)
        try:
            paginated_cart_items = CartItem.query.filter_by(cart_id=cart.id).paginate(page=page, per_page=per_page)
            if page > paginated_cart_items.pages:
                cart_namespace.abort(400, "Page number out of range")
            if per_page > 50:
                cart_namespace.abort(400, "Per page limit exceeded")
        except Exception as e:
            logger.error(f"An error occurred while getting all items in the cart for user {user.email}: {str(e)}")
            cart_namespace.abort(500, "An unexpected error occurred while trying to retrieve all items in the cart")
        
        return {"cart_items": paginated_cart_items.items, 
            "pagination": {
            "page": paginated_cart_items.page,
            "per_page": paginated_cart_items.per_page,
            "total": paginated_cart_items.total,
            "pages": paginated_cart_items.pages,
            "next_page": paginated_cart_items.next_num,
            "prev_page": paginated_cart_items.prev_num
        }}, 200

@cart_namespace.route('/cart/all')
class GetAllCarts(Resource):
    @cart_namespace.marshal_with(cart_status_model)
    @jwt_required()
    @cart_namespace.doc(description="Retrieve all carts for all users")
    def get(self):
        """
            Get all carts for all users
        """
        
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=5, type=int)
            carts = Cart.query.paginate(page=page, per_page=per_page)
            if not carts:
                cart_namespace.abort(404, "No carts found")
            if page < 1:
                cart_namespace.abort(400, "Page number must be greater than 0")
            if page > carts.pages:
                cart_namespace.abort(400, "Page number out of range")
            if per_page > 50:
                cart_namespace.abort(400, "Per page limit exceeded")
            return {"carts": carts.items, 
                "pagination": {
                "page": carts.page,
                "per_page": carts.per_page,
                "total": carts.total,
                "pages": carts.pages,
                "next_page": carts.next_num,
                "prev_page": carts.prev_num
            }}, 200
        except Exception as e:
            logger.error(f"An error occurred while trying to retrieve all carts for all users: {str(e)}")
            cart_namespace.abort(500, "An unexpected error occurred while trying to retrieve all carts")
        
        
@cart_namespace.route('/cart/delete/<int:id>')
class DeleteItem(Resource):
    @jwt_required()
    @cart_namespace.doc(description="Delete a cart item in a user's cart by id of the cart item",
                        params={"item_id": "ID of the cart item to delete"},
                        required=True)
    def delete(self, id):
        """
            Delete a cart item in a user's cart by id of the cart item
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            cart_namespace.abort(401, "Invalid or missing authorization token")
        user = User.query.filter_by(email=user_email).first()
        if not user:
            cart_namespace.abort(404, "User not found")
        cart = Cart.query.filter_by(user_id=user.id).first()
        if not cart:
            cart_namespace.abort(404, f"Cart not found for user {user.email}")
        cart_item = CartItem.query.filter_by(id=id, cart_id=cart.id).first()
        if not cart_item:
            cart_namespace.abort(404, f"Cart item not found for cart with ID {cart.id}")
        if cart_item.cart_id != cart.id:
            cart_namespace.abort(400, "Cart item does not belong to this cart")
        try:
            cart_item.delete()
            return {"message": "Cart item deleted successfully"}, 200
        except Exception as e:
            logger.error(f"An error occurred while deleting cart item with ID {id}: {str(e)}")
            cart_namespace.abort(500, "Failed to delete cart item")