from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from ..models.orders import Order
from ..models.orderItems import OrderItem
from ..models.users import User
from ..models.products import Product
from ..models.carts import Cart
from ..utils import db

import logging

# Create a logger instance
logger = logging.getLogger(__name__)


orderItems_namespace = Namespace('orderItems', description='Order Items related operations')

orderStatus_model = orderItems_namespace.model('Order Status', {
    "order_id": fields.Integer(required=True, description='ID of the order to add the product to'),
})

orderItem_model = orderItems_namespace.model('OrderItem', {
    "id": fields.Integer(readOnly=True, description='The order item unique identifier'),
    "order_id": fields.Integer(required=True, description='ID of the order to add the product to'),
    "product_id": fields.Integer(required=True, description='ID of the product to add to the order'),
    "quantity": fields.Integer(required=True, description='Quantity of the product to add to the order'),
    "price": fields.Float(required=True, description='Price of the product')
})


@orderItems_namespace.route('/add_order_item')
class AddOrderItem(Resource):
    @jwt_required()
    @orderItems_namespace.doc(description="Add item(s) to an order from the cart (Place an order)")
    def post(self):
        """
            Adds item(s) to an order from the cart (Place an order)
        """
        
        jwt_data = get_jwt()
        user_email = jwt_data.get('sub')
        if not user_email:
            orderItems_namespace.abort(401, {'message': 'Invalid or missing authorization token'})
        
        # Validate user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            orderItems_namespace.abort(404, {'message': 'User not found'})
        
        # Validate cart
        user_id = user.id
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            orderItems_namespace.abort(404, {'message': 
                f'Cart not found for user {user_email}. Cart is empty or does not exist'})
        if not cart.items:
            orderItems_namespace.abort(404, {'message': 
                f'Cart is empty for user {user_email}. Add items to cart before placing an order'})
        
        # Validate order and create a new order if it does not exist
        order = Order.query.filter_by(user_id=user_id).first()
        if not order:
            # Create a new order
            order = Order(user_id=user_id)
            try:
                order.save()
            except Exception as e:
                logger.error(f"An error occurred while creating order: {str(e)}")
                orderItems_namespace.abort(500, {'message': 'An unexpected error occurred while trying to create order'})
        # Add order items to an order from the cart (Place an order)
        for item in cart.items:
            order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
            try:
                order_item.save()
            except Exception as e:
                logger.error(f"An error occurred while adding product to order: {str(e)}")
                orderItems_namespace.abort(500, {'message': 'An unexpected error occurred while trying to add product to order'})
                
                # Update product stock
                product = Product.query.get(item.product_id)
                if product:
                    product.stock -= item.quantity
                    try:
                        product.save()
                    except Exception as e:
                        logger.error(f"An error occurred while updating product stock: {str(e)}")
                        orderItems_namespace.abort(500, 
                        {'message': 'An unexpected error occurred while trying to update product stock'}
                        )
                        
        # Delete cart after placing an order
        try:
            cart.delete()
        except Exception as e:
            logger.error(f"An error occurred while deleting cart: {str(e)}")
            orderItems_namespace.abort(500, {'message': 'An unexpected error occurred while trying to delete cart'})
        return {'message': f'Order placed successfully for {user_email}, order.id:{order.id}'}, 201