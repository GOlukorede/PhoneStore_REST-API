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

order_namespace = Namespace('orders', description='Order related operations')

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
        Creates an order for a user
    """
    @jwt_required()
    @order_namespace.doc(description="Create an order for a user", security='Bearer Auth')
    def post(self):
        """
            Creates an order for a user
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
        Cancels (or deletes) an order for a user
    """
    @jwt_required()
    @order_namespace.doc(description="Cancel an order for a user", security='Bearer Auth')
    def delete(self):
        """
            Cancels an order for a user
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
       