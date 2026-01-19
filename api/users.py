"""
User API endpoints for ScootRapid
"""

from flask import request
from flask_restful import Resource
from flask_login import current_user, login_required
from marshmallow import Schema, fields, ValidationError
from api import api
from app.models.user import User

class UpdateProfileSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    phone = fields.Str()

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()

class UserListResource(Resource):
    @login_required
    def get(self):
        """Get all users (admin only)"""
        if not current_user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        role = request.args.get('role')
        limit = request.args.get('limit', 100, type=int)
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        users = query.limit(limit).all()
        
        return [u.to_dict() for u in users], 200

class UserResource(Resource):
    @login_required
    def get(self, user_id):
        """Get user by ID"""
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        if not current_user.is_admin() and current_user.id != user_id:
            return {'message': 'Not authorized'}, 403
        
        include_sensitive = current_user.is_admin() or current_user.id == user_id
        
        return user.to_dict(include_sensitive=include_sensitive), 200

class CurrentUserProfileResource(Resource):
    @login_required
    def get(self):
        """Get current user profile"""
        return current_user.to_dict(include_sensitive=True), 200
    
    @login_required
    def put(self):
        """Update current user profile"""
        try:
            data = update_profile_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        if 'phone' in data:
            current_user.phone = data['phone']
        
        try:
            from app import db
            db.session.commit()
            return current_user.to_dict(include_sensitive=True), 200
        except Exception as e:
            return {'message': f'Error updating profile: {str(e)}'}, 400

class ChangePasswordResource(Resource):
    @login_required
    def put(self):
        """Change current user password"""
        try:
            data = change_password_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        if not current_user.check_password(data['old_password']):
            return {'message': 'Current password is incorrect'}, 400
        
        if len(data['new_password']) < 8:
            return {'message': 'New password must be at least 8 characters long'}, 400
        
        try:
            current_user.set_password(data['new_password'])
            current_user.save()
            return {'message': 'Password changed successfully'}, 200
        except Exception as e:
            return {'message': f'Error changing password: {str(e)}'}, 400

class SearchUsersResource(Resource):
    @login_required
    def get(self):
        """Search users (admin only)"""
        if not current_user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        query_str = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not query_str:
            return [], 200
        
        search_pattern = f'%{query_str}%'
        
        users = list(User.query.filter(
            (User.email.contains(query_str)) |
            (User.first_name.contains(query_str)) |
            (User.last_name.contains(query_str))
        ).limit(limit))
        
        return [u.to_dict() for u in users], 200

api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(CurrentUserProfileResource, '/users/me')
api.add_resource(ChangePasswordResource, '/users/me/password')
api.add_resource(SearchUsersResource, '/users/search')
