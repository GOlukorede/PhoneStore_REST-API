import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users import User
from ..models.logout import TokenBlockList
from flask_jwt_extended import create_access_token

class TestUserAuth(unittest.TestCase):
    
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
    
    def test_register_user(self):
        
        data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        response = self.client.post("/auth/register", json=data)
        
        user = User.query.filter_by(email=data['email']).first()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertIsInstance(user.username, str)
        self.assertIsInstance(user.email, str)
        self.assertIn('@', data['email'])
        
    def test_login_user(self):
        
       # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/auth/register", json=register_data)
        
        # Login the user
        
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        self.assertIn("access_token", response.json)
        self.assertIn("refresh_token", response.json)
        self.assertEqual(response.status_code, 200)
        
        # Check missing data
        missing_data = {}
        response = self.client.post("/auth/login", json=missing_data)
        self.assertEqual(response.status_code, 400)
        
        #Check missing email
        missing_email_data = {
            "password": "testapi"
        }
        response = self.client.post("/auth/login", json=missing_email_data)
        self.assertEqual(response.status_code, 400)
        
        # Check missing password
        missing_password_data = {
            "email": "testapi@gmail.com"
        }
        response = self.client.post("/auth/login", json=missing_password_data)
        self.assertEqual(response.status_code, 400)
        
    def test_refresh_token(self):
        # Create and register a user
        register_data = {
            "username": "testapi",
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        self.client.post("/auth/register", json=register_data)
        
        # Login the user
        
        login_data = {
            "email": "testapi@gmail.com",
            "password": "testapi"
        }
        
        login_response = self.client.post("/auth/login", json=login_data)
        self.assertIn("refresh_token", login_response.json)
        refresh_token = login_response.json['refresh_token']
        
        # Test refresh token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = self.client.post("/auth/refresh", headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json)
        
        
        
        