import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.users import Admin
from ..models.products import Product

class TestUserProduct(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        
        self.client = self.app.test_client()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()
    
    # Test to add a product
    def test_add_product(self):
        
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/admin/auth/register", json=register_data)
        
        # Login the user
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        login_response = self.client.post("/admin/auth/login", json=login_data)
        self.assertIn("access_token", login_response.json)
        self.assertIn("refresh_token", login_response.json)
        self.assertEqual(login_response.status_code, 200)
        # self.assertEqual("admin", login_response.json['role'])
        
        # Verify the user is an admin
        admin = Admin.query.filter_by(email=login_data['email']).first()
        self.assertTrue(admin.is_admin)
        
        # Add a product
        product_data = {
            "name": "iphone 12",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
        }
        
        access_token = login_response.json['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = self.client.post("/products/product", json=product_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)
        self.assertIsInstance(response.json['id'], int)
        self.assertEqual(response.json['name'], product_data['name'])
        self.assertIsInstance(response.json['name'], str)
        self.assertIsInstance(response.json['description'], str)
        self.assertIsInstance(response.json['quantity'], int)
        self.assertIsInstance(response.json['price'], float)
        self.assertIsInstance(response.json['category'], str)
    
    # Test to get all products
    def test_get_products(self):
        
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        response = self.client.post("/admin/auth/register", json=register_data)
        self.assertEqual(response.status_code, 201)
    
    # Test to get a single product by id
    def test_get_product_by_id(self):
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/admin/auth/register", json=register_data)
        
        # Login the user
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        login_response = self.client.post("/admin/auth/login", json=login_data)
        self.assertIn("access_token", login_response.json)
        self.assertIn("refresh_token", login_response.json)
        self.assertEqual(login_response.status_code, 200)
        # self.assertEqual("admin", login_response.json['role'])
        
        # Verify the user is an admin
        admin = Admin.query.filter_by(email=login_data['email']).first()
        self.assertTrue(admin.is_admin)
        
        # Add a product
        product_data = {
            "name": "iphone 12",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
        }
        
        access_token = login_response.json['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = self.client.post("/products/product", json=product_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json)
        
        # Get the product by id
        product_id = response.json['id']
        response = self.client.get(f"/products/product/{product_id}")
        self.assertEqual(response.status_code, 200)
        
    
    # Test to update a product by id
    
    def test_update_product_by_id(self):
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/admin/auth/register", json=register_data)
        
        # Login the user
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        login_response = self.client.post("/admin/auth/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json)
        self.assertIn("refresh_token", login_response.json)
        
        access_token = login_response.json['access_token']
        
        # Verify the user is an admin
        admin = Admin.query.filter_by(email=login_data['email']).first()
        self.assertTrue(admin.is_admin)
        
        # Add a product
        product_data = {
            "name": "iphone 12",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        add_product_response = self.client.post("/products/product", json=product_data, headers=headers)
        self.assertEqual(add_product_response.status_code, 201)
        self.assertIsNotNone(add_product_response.json)
        
        # Update the product
        product_id = add_product_response.json['id']
        update_data = {
            "name": "iphone 12 pro",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
        }
        
        response = self.client.put(f"/products/product/{product_id}", json=update_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.assertEqual(response.json['name'], update_data['name'])
        self.assertEqual(response.json['description'], update_data['description'])
        self.assertEqual(response.json['quantity'], update_data['quantity'])
        self.assertEqual(response.json['price'], update_data['price'])
        self.assertEqual(response.json['category'], 'ProductCategory.iphone')
        
    
    # Test to delete a product by id
    def test_delete_product_by_id(self):
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/admin/auth/register", json=register_data)
        
        # Login the user
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        login_response = self.client.post("/admin/auth/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json['access_token']
        
        # Add a product
        product_data = {
            "name": "iphone 12",
            "description": "iphone 12 pro max",
            "quantity": 10,
            "price": 1000.00,
            "category": "iphone"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        add_product_response = self.client.post("/products/product", json=product_data, headers=headers)
        self.assertEqual(add_product_response.status_code, 201)
        
        # Delete the product
        product_id = add_product_response.json['id']
        response = self.client.delete(f"/products/product/{product_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        product = Product.query.get(product_id)
        self.assertIsNone(product)

        
        
        
        
        