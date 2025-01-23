import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from ..models.users import Admin, User
from ..models.orders import Order

class TestUserOrder(unittest.TestCase):
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
        
        self.login_user = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()
    
    def test_create_order(self):
        # Create a user
        response = self.client.post('/auth/register', json=self.user_data)
        self.assertEqual(response.status_code, 201)
        
        # Login the user
        response = self.client.post('/auth/login', json=self.login_user)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        access_token = data['access_token']
        
        # Create an order
        response = self.client.post('/orders/create_order', headers={'Authorization': 'Bearer ' + access_token})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Order created successfully')
        
    
    def test_cancel_order(self):
        # Create a user
        response = self.client.post('/auth/register', json=self.user_data)
        self.assertEqual(response.status_code, 201)
        
        # Login the user
        response = self.client.post('/auth/login', json=self.login_user)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        access_token = data['access_token']
        
        # Create an order
        response = self.client.post('/orders/create_order', headers={'Authorization': f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 201)
        
        # Cancel the order
        response = self.client.delete('/orders/cancel_order', headers={'Authorization': f"Bearer {access_token}"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Order deleted successfully')
        
        order = Order.query.first()
        self.assertIsNone(order)