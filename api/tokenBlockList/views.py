from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from ..models.logout import TokenBlockList
from flask import request

logout_namespace = Namespace('logout', description='Logout User')

@logout_namespace.route('/user')
class LogoutUser(Resource):
    @jwt_required(verify_type=False)
    @logout_namespace.doc(description="Logout a user")
    def post(self):
        """
            Logout a user
        """
        try:
            jwt_data = get_jwt()
            jti = jwt_data['jti']
            token_type = jwt_data['type']
            
            token = TokenBlockList(jti=jti)
            token.save()
            return {"message": f"{token_type} token revoked successfully. User logged out"}, 200
        except Exception as e:
            return {"message": f"Something went wrong logging out user {jwt_data['sub']}: {str(e)}"}, 400