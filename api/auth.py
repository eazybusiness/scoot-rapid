"""
Authentication API endpoints for ScootRapid
"""

from flask import request
from flask_restful import Resource
from flask_login import login_user, current_user
from marshmallow import Schema, fields, ValidationError
from api import api
from app.models.user import User

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone = fields.Str()
    role = fields.Str()

login_schema = LoginSchema()
register_schema = RegisterSchema()

class LoginResource(Resource):
    def post(self):
        """Login with email and password"""
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        user = User.query.filter_by(email=data['email'].lower()).first()
        if not user:
            return {'message': 'Invalid email or password'}, 401
        
        if not user.is_active:
            return {'message': 'Account is deactivated'}, 401
        
        if not user.check_password(data['password']):
            return {'message': 'Invalid email or password'}, 401
        
        user.update_last_login()
        
        return {
            'message': 'Login successful',
            'user': user.to_dict()
        }, 200

class RegisterResource(Resource):
    def post(self):
        """Register a new user"""
        try:
            data = register_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email'].lower()).first()
        if existing_user:
            return {'message': 'User with this email already exists'}, 400
        
        if len(data['password']) < 8:
            return {'message': 'Password must be at least 8 characters long'}, 400
        
        try:
            from app import db
            user = User(
                email=data['email'].lower(),
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                role=data.get('role', 'customer')
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            
            return {
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201
            
        except Exception as e:
            return {'message': f'Registration failed: {str(e)}'}, 400

class CurrentUserResource(Resource):
    def get(self):
        """Get current user information"""
        if not current_user.is_authenticated:
            return {'message': 'Unauthorized'}, 401
        
        return current_user.to_dict(include_sensitive=True), 200

api.add_resource(LoginResource, '/auth/login')
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(CurrentUserResource, '/auth/me')
