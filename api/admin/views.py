from flask_restx import Resource, Namespace, fields, abort
from flask_jwt_extended import jwt_required, get_jwt
from ..models.users import Admin, User

admin_user_namespace = Namespace('admin', description='Admin related operations')
admin_user


@admin_user_namespace.route('all/users')
class GetAllUsers(Resource):
    @admin_user_namespace.marshal_with(user_model)
    @admin_user_namespace.doc(description="Get all registered users")
    @jwt_required()
    def get(self):
        """
            Get all users
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            admin_user_namespace.abort(403, 'Unauthorized. Only admins can view all users')
        users = User.query.all()
        return users