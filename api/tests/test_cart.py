import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.users import User
from ..models.carts import Cart

class TestCart(unittest.TestCase):
    
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
        
        self.login_admin_data = {
            "email": "admin@gmail.com",
            "password": "admin"
        }
        
        self.login_user_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.product_data = {
            "name": "Product 1",
            "description": "Product 1 description",
            "quantity": 10,
            "price": 100.0,
            "category": "iphone"
        }
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()
        
    def test_create_cart(self):
        # Register a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        access_token = login_response.json['access_token']

        # Test create cart
        cart_response = self.client.post("/carts/create_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(cart_response.status_code, 201)
        self.assertEqual(cart_response.json['user_id'], 1)
    
    def test_delete_cart(self):
        # Register a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        access_token = login_response.json['access_token']
        
        # Create cart
        cart_response = self.client.post("/carts/create_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(cart_response.status_code, 201)
        
        # Test delete cart
        delete_cart_response = self.client.delete("/carts/delete_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(delete_cart_response.status_code, 200)
        self.assertEqual(delete_cart_response.json['message'], "Cart for user with ID 1 deleted successfully")
        self.assertIsNone(delete_cart_response.json.get('user_id'))
        
    # Test get all items in a cart for a user
    def get_all_items_in_a_cart(self):
        # Register a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        access_token = login_response.json['access_token']
        
        # Create cart
        cart_response = self.client.post("/carts/create_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(cart_response.status_code, 201)
        
        # Test get all items in a cart
        get_items_response = self.client.get("/carts/cart_items/all", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(get_items_response.status_code, 200)
        self.assertIsInstance(get_items_response.json, list)
        self.assertEqual(len(get_items_response.json), 0)
        
    
    # Test get all carts for all users
    def test_get_all_carts(self):
        # Register a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        access_token = login_response.json['access_token']
        
        # Create cart
        cart_response = self.client.post("/carts/create_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(cart_response.status_code, 201)
        
        #Test get all carts
        get_carts_response = self.client.get("/carts/cart/all", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(get_carts_response.status_code, 200)
        self.assertIsInstance(get_carts_response.json.get('carts'), list)
        
    # Test:  Delete a cart item in a user's cart by id of the cart item
    def test_delete_cart_item(self):
        # Register a user
        user_response = self.client.post("/auth/register", json=self.user_data)
        self.assertEqual(user_response.status_code, 201)
        
         # Register an admin
        admin_response = self.client.post("/admin/auth/register", json=self.admin_data)
        self.assertEqual(admin_response.status_code, 201)
        
        # Login the admin
        admin_login_response = self.client.post("/admin/auth/login", json=self.login_admin_data)
        self.assertEqual(admin_login_response.status_code, 200)
        self.assertIn("access_token", admin_login_response.json)
        admin_access_token = admin_login_response.json['access_token']
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        access_token = login_response.json['access_token']
        
        # Create cart
        cart_response = self.client.post("/carts/create_cart", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(cart_response.status_code, 201)
        cart_id = cart_response.json['id']
        cart_user_id = cart_response.json['user_id']
        
        # Test: Create a product
        product_response = self.client.post("/products/product", headers={"Authorization": f"Bearer {admin_access_token}"}, json=self.product_data)
        self.assertEqual(product_response.status_code, 201)
        
        # Create a cart item
        add_item_response = self.client.post("/cartItems/add", headers={"Authorization": f"Bearer {access_token}"}, json={"product_id": 1, "quantity": 2, "cart_id": cart_id})
        self.assertEqual(add_item_response.status_code, 201)
        self.assertEqual(add_item_response.json['message'], "Product added to cart")
       
        
        
        # Test delete cart item
        delete_cart_item_response = self.client.delete("/carts/cart/delete/1", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(delete_cart_item_response.status_code, 200)
        self.assertEqual(delete_cart_item_response.json['message'], "Cart item deleted successfully")
        
       
