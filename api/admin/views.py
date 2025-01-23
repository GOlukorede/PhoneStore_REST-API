from flask_restx import Resource, Namespace, fields, abort
from flask_jwt_extended import jwt_required, get_jwt
from ..models.users import Admin, User

admin_user_namespace = Namespace('admin', description='Operations related to managing users and administrative tasks')
user_model = admin_user_namespace.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'role': fields.String(required=True)
})

@admin_user_namespace.route('all/users')
class GetAllUsers(Resource):
    @admin_user_namespace.marshal_with(user_model)
    @admin_user_namespace.doc(description="Get all registered users")
    @jwt_required()
    def get(self):
        """
             Retrieve a list of all registered users.
             Accessible only to admin users.
             Returns:  a list of all registered users.
                status codes:
                    200: Success
                    403: Unauthorized
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            admin_user_namespace.abort(403, 'Unauthorized. Only admins can view all users')
        users = User.query.all()
        return users
    
    def delete(self):
        """
            Delete all registered users.
            Accessible only to admin users.
            Returns: a message indicating that all users have been deleted.
                status codes:
                    200: Success
                    403: Unauthorized
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            admin_user_namespace.abort(403, 'Unauthorized. Only admins can delete all users')
        User.query.delete()
        return {"message": "All users deleted successfully"}, 200

@admin_user_namespace.route('users/<int:id>')
class GetUser(Resource):
    @admin_user_namespace.marshal_with(user_model)
    @admin_user_namespace.doc(description="Get a user")
    @jwt_required()
    def get(self, id):
        """
            Retrieve the details of a specific user by their ID.
            Accessible only to admin users.
            Parameters:
                id: The ID of the user to retrieve.
            Returns: The details of the user.
                status codes:
                    200: Success
                    403: Unauthorized
                    404: User not found
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            admin_user_namespace.abort(403, 'Unauthorized. Only admins can view a user')
        user = User.query.get(id)
        if not user:
            admin_user_namespace.abort(404, 'User not found')
        return user
    
    def delete(self, id):
        """
             Delete a specific user by their ID.
             Accessible only to admin users.
                Parameters:
                    id: The ID of the user to delete.
                Returns: a message indicating that the user has been deleted.
                    status codes:
                        200: Success
                        403: Unauthorized
                        404: User not found
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            admin_user_namespace.abort(403, 'Unauthorized. Only admins can delete a user')
        user = User.query.get(id)
        if not user:
            admin_user_namespace.abort(404, 'User not found')
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200