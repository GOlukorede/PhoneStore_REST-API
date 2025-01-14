from flask_restx import Namespace, Resource, fields, marshal_with
from flask import request
from datetime import datetime
from ..models.users import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_namespace = Namespace('auth', description='User registration and authentication operations')

signup_model = auth_namespace.model('Signup', {
    "id": fields.Integer(),
    "username": fields.String(required=True, description='The username'),
    "email": fields.String(required=True, description='The email address'),
    "password": fields.String(required=True, description='The password')  
})

user_model = auth_namespace.model('User', {
    "id": fields.Integer(),
    "password_hash": fields.String(required=True, description='The hashed password'),
    "username": fields.String(required=True, description='The username'),
    "email": fields.String(required=True, description='The email address'),
    "is_admin": fields.Boolean(default=False, description='The user role'),
    "is_active": fields.Boolean(default=True, description='The user status'),
    "request_count": fields.Integer(description='The request count'),
    "created_at": fields.DateTime(description='The date and time the user was created'),
    "updated_at": fields.DateTime(description='The date and time the user was updated')
})

login_model = auth_namespace.model('Login', {
    "email": fields.String(required=True, description='The email address'),
    "password": fields.String(required=True, description='The password')
})

@auth_namespace.route('/register')
class Register(Resource):
    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(user_model)
    @auth_namespace.doc(description="Register a new user")
    def post(self):
        """
            Create a new user
        """
        data = request.get_json()
        
        if not data:
            return {"message": "No input data provided"}, 400
        if not data['username'] or not data['email'] or not data['password']:
            return {"message": "Invalid input data provided"}, 400
        if '@' not in data['email']:
            return {"message": "Invalid email address"}, 400
        
        try:
            new_user = User(username=data['username'], email=data['email'])
            new_user.set_password(data['password'])
            new_user.save()
            return new_user, 201
        except Exception as e:
            return {"message": f"Something went wrong creating a user: {str(e)}"}, 400

@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(description="Login a user to get the JWT access and refresh tokens")
    def post(self):
        """
            Log in a user and return a JWT access and refresh tokens
        """
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
        if not data.get('email') or not data.get('password'):
            return {"message": "Invalid input data provided"}, 400
        if '@' not in data['email']:
            return {"message": "Invalid email address"}, 400
        email = data['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found. Please register user!"}, 404
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=email)
            if not access_token:
                return {"message": "Something went wrong creating the access token"}, 400
            refresh_token = create_refresh_token(identity=email)
            if not refresh_token:
                return {"message": "Something went wrong creating the refresh token"}, 400
            return {
                "access_token": access_token, 
                "refresh_token": refresh_token
                }, 200
        return {"message": "Invalid credentials"}, 401



@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_namespace.doc(description="Refresh a user's expired JWT access token")
    def post(self):
        """
            Refresh a user's JWT access token
        """
        username = get_jwt_identity()
        access_token = create_access_token(identity=email)
        return {"access_token": access_token}, 200
        