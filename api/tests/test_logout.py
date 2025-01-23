import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users import User
from ..models.logout import TokenBlockList
from flask_jwt_extended import create_access_token, get_jwt

class TestLogOut(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()   
        self.client = self.app.test_client()
        db.create_all()
        self.token_block_list = TokenBlockList.query.all()
        self.assertEqual(len(self.token_block_list), 0)
        
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
        
    def test_logout_user(self):
        # Register a user
        register_response = self.client.post("/auth/register", json=self.user_data)
        
        # Login the user
        login_response = self.client.post("/auth/login", json=self.login_user)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access_token', login_response.json)
        
        # Logout the user
        access_token = login_response.json['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.post("/logout/user", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Check if token is in block list
        token = TokenBlockList.query.all()
        self.assertEqual(len(token), 1)
        
    def test_logout_user_invalid_token(self):
        # Logout with an invalid token
        headers = {'Authorization': 'Bearer invalid-token'}
        response = self.client.post('/logout/user', headers=headers)
        self.assertEqual(response.status_code, 422)

        
    def test_logout_user_missing_token(self):
        # Logout without a token
        response = self.client.post('/logout/user')
        self.assertEqual(response.status_code, 401)
