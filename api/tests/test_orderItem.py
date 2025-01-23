import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.users import Admin, User
from ..models.cartItems import CartItem


class TestUserOrderItems(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()

        self.user_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.admin_data = {
                "username": "admin",
                "email": "admin@gmail.com",
                "password": "admin"
        }
        
        self.user_login = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.login_admin_data = {
            "email": "admin@gmail.com",
            "password": "admin"
            }
        
        self.product_data = {
            "name": "iphone 12",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
            }
        
        self.cart_item_data = {
            "cart_id": 1,
            "product_id": 1,
            "quantity": 2,
            "price": 199.99
            }
        
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()
        

    def test_place_an_order(self):
        # Create a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
        # Create admin
        admin_response = self.client.post("/admin/auth/register", json=self.admin_data)
        self.assertEqual(admin_response.status_code, 201)
        
        # Login user
        user_login_response = self.client.post("/auth/login", json=self.user_login)
        self.assertEqual(user_login_response.status_code, 200)
        self.assertIn("access_token", user_login_response.json)
        user_access_token = user_login_response.json['access_token']
        
         #login admin
        login_admin = self.client.post("/admin/auth/login", json=self.login_admin_data)
        self.assertEqual(login_admin.status_code, 200)
        self.assertIn("access_token", login_admin.json)
        admin_access_token = login_admin.json["access_token"]
        
        # Create product
        headers = {"Authorization": f"Bearer {admin_access_token}"}
        product_response = self.client.post("/products/product", json=self.product_data, headers=headers)
        self.assertEqual(product_response.status_code, 201)
        self.assertIsNotNone(product_response.json)
        
        # Add product to cart
        headers = {"Authorization": f"Bearer {user_access_token}"}
        cart_response = self.client.post("/cartItems/add", json=self.cart_item_data, headers=headers)
        self.assertEqual(cart_response.status_code, 201)
        self.assertIsNotNone(cart_response.json)
        self.assertEqual(cart_response.json['message'], 'Product added to cart')
        
        # Place an order
        response = self.client.post("/orderItems/add_order_item", headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json)
        
        # Check if the cart is empty
        cart = CartItem.query.filter_by(cart_id=1).first()
        self.assertIsNone(cart)