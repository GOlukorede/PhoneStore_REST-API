from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..models.carts import Cart
from ..models.users import User
from ..models.orders import Order
from ..models.orderItems import OrderItem

import logging

# Create a logger instance
logger = logging.getLogger(__name__)

order_namespace = Namespace('orders', description='Handles all operations related to orders, \
    including creating orders,'
    'retrieving order details, and managing order cancellation.')

order_model = order_namespace.model('Order', {
    "user_id": fields.Integer(required=True, description='ID of the user that owns the order')
})

order_status_model = order_namespace.model('Order Status', {
    'id': fields.Integer(),
    'user_id': fields.Integer(required=True, description='ID of the user that owns the order'),
    'created_at': fields.DateTime(),
    'status': fields.String()
})

order_item_model = order_namespace.model('OrderItem', {
    "id": fields.Integer(description='The order item unique identifier'),
    "order_id": fields.Integer(required=True, description='ID of the order to add the product to'),
    "product_id": fields.Integer(required=True, description='ID of the product to add to the order'),
    "quantity": fields.Integer(required=True, description='Quantity of the product to add to the order'),
    "price": fields.Float(required=True, description='Price of the product')
})

pagination_model = order_namespace.model('Pagination', {
    'page': fields.Integer(description='Page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages'),
    'next_page': fields.String(description='Next page URL'),
    'prev_page': fields.String(description='Previous page URL')
})

order_items_model = order_namespace.model('OrderItems', {
    'order_items': fields.List(fields.Nested(order_item_model)),
    'pagination': fields.Nested(pagination_model)
})

@order_namespace.route('/create_order')
class CreateOrder(Resource):
    """
        Resource for creating an order for a user.
        This endpoint allows a user to initiate the creation of an order. The order will be associated
        with the user identified via the JWT token. If the operation succeeds, a success message is returned.
    """
    @jwt_required()
    @order_namespace.doc(description="Create an order for a user", security='Bearer Auth')
    def post(self):
        """
        Handle POST request to create an order.

        This method validates the user's identity using the JWT token, retrieves the user details from the database, 
        and creates an order associated with the user.

        Returns:
            dict: A success message if the order is created successfully.
            HTTP Status Code:
                - 201: Created
                - 401: Unauthorized if the token is invalid or missing.
                - 404: Not Found if the user is not found in the database.
                - 500: Internal Server Error if an unexpected error occurs.
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            order_namespace.abort(401, {'message': 'Invalid or missing authorization token'})
        user = User.query.filter_by(email=user_email).first()
        if not user:
            order_namespace.abort(404, {'message': 'User not found'})

        order = Order(user_id=user.id)
        try:
            order.save()
            return {'message': 'Order created successfully'}, 201
        except Exception as e:
            logger.error(f"An error occurred while creating order for user {user.id}: {str(e)}")
            order_namespace.abort(500, {'message': 'An unexpected error occurred while trying to create an order'})
        return {'message': 'Order created successfully'}, 201

@order_namespace.route('/cancel_order')
class DeleteOrder(Resource):
    """
    Resource for canceling (or deleting) an existing order for a user.
    This endpoint allows a user to cancel an existing order. The order is identified based on the user
    details obtained via the JWT token. Upon successful cancellation, the order is removed from the database.
    """
    @jwt_required()
    @order_namespace.doc(description="Cancel an order for a user", security='Bearer Auth')
    def delete(self):
        """
        Handle DELETE request to cancel an order.
        This method validates the user's identity using the JWT token, retrieves the user's associated order from the 
        database, and deletes the order.

        Returns:
            dict: A success message if the order is canceled successfully.
            HTTP Status Code:
                - 200: OK if the order is deleted successfully.
                - 401: Unauthorized if the token is invalid or missing.
                - 404: Not Found if the user or order does not exist.
                - 500: Internal Server Error if an unexpected error occurs.
        """
        jwt_data = get_jwt()
        user_email = jwt_data['sub']
        if not user_email:
            order_namespace.abort(401, {'message': 'Invalid or missing authorization token'})
        user = User.query.filter_by(email=user_email).first()
        if not user:
            order_namespace.abort(404, {'message': 'User not found'})

        order = Order.query.filter_by(user_id=user.id).first()
        if not order:
            order_namespace.abort(404, {'message': 'Order not found for user'})
        
        try:
            order.delete()
            return {'message': 'Order deleted successfully'}, 200
        except Exception as e:
            logger.error(f"An error occurred while deleting order for user {user.id}: {str(e)}")
            order_namespace.abort(500, {'message': 'An unexpected error occurred while trying to delete an order'})
       