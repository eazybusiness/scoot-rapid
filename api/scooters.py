"""
Scooter API endpoints for ScootRapid
"""

from flask import request
from flask_restful import Resource
from flask_login import current_user, login_required
from marshmallow import Schema, fields, ValidationError
from api import api
from app.models.scooter import Scooter

class ScooterSchema(Schema):
    identifier = fields.Str(required=True)
    model = fields.Str(required=True)
    brand = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    address = fields.Str()
    battery_level = fields.Int()

scooter_schema = ScooterSchema()

class ScooterListResource(Resource):
    @login_required
    def get(self):
        """Get all scooters"""
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        query = Scooter.query
        
        if status:
            query = query.filter(Scooter.status == status)
        
        scooters = list(query.limit(limit))
        
        return [s.to_dict() for s in scooters], 200
    
    @login_required
    def post(self):
        """Create a new scooter"""
        if not current_user.can_manage_scooters():
            return {'message': 'Not authorized to create scooters'}, 403
        
        try:
            data = scooter_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        identifier = data['identifier'].upper()
        
        # Check if exists
        try:
            Scooter.get(Scooter.identifier == identifier)
            return {'message': 'Scooter with this identifier already exists'}, 400
        except Scooter.DoesNotExist:
            pass
        
        try:
            scooter = Scooter.create(
                identifier=identifier,
                model=data['model'],
                brand=data['brand'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                address=data.get('address'),
                battery_level=data.get('battery_level', 100),
                provider=current_user
            )
            
            return scooter.to_dict(include_sensitive=True), 201
            
        except Exception as e:
            return {'message': f'Error creating scooter: {str(e)}'}, 400

class ScooterResource(Resource):
    @login_required
    def get(self, scooter_id):
        """Get scooter by ID"""
        try:
            scooter = Scooter.query.get(scooter_id)
        except Scooter.DoesNotExist:
            return {'message': 'Scooter not found'}, 404
        
        include_sensitive = current_user.is_admin() or scooter.provider.id == current_user.id
        
        return scooter.to_dict(include_sensitive=include_sensitive), 200
    
    @login_required
    def put(self, scooter_id):
        """Update scooter"""
        try:
            scooter = Scooter.query.get(scooter_id)
        except Scooter.DoesNotExist:
            return {'message': 'Scooter not found'}, 404
        
        if not current_user.is_admin() and scooter.provider.id != current_user.id:
            return {'message': 'Not authorized'}, 403
        
        data = request.get_json()
        
        allowed_fields = ['model', 'brand', 'address', 'battery_level']
        
        for field in allowed_fields:
            if field in data:
                setattr(scooter, field, data[field])
        
        try:
            from app import db
            db.session.commit()
            return scooter.to_dict(include_sensitive=True), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating scooter: {str(e)}'}, 400
    
    @login_required
    def delete(self, scooter_id):
        """Delete scooter"""
        try:
            scooter = Scooter.query.get(scooter_id)
        except Scooter.DoesNotExist:
            return {'message': 'Scooter not found'}, 404
        
        if not current_user.is_admin() and scooter.provider.id != current_user.id:
            return {'message': 'Not authorized'}, 403
        
        if scooter.get_current_rental():
            return {'message': 'Cannot delete scooter with active rental'}, 400
        
        try:
            scooter.delete_instance()
            return {'message': 'Scooter deleted successfully'}, 200
        except Exception as e:
            return {'message': f'Error deleting scooter: {str(e)}'}, 400

class AvailableScootersResource(Resource):
    @login_required
    def get(self):
        """Get available scooters"""
        limit = request.args.get('limit', 100, type=int)
        
        scooters = list(Scooter.query.filter(
            (Scooter.status == 'available') & (Scooter.battery_level > 15)
        ).limit(limit))
        
        return [s.to_dict() for s in scooters], 200

class NearbyScootersResource(Resource):
    @login_required
    def get(self):
        """Get nearby scooters"""
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 5.0, type=float)
        limit = request.args.get('limit', 50, type=int)
        
        if latitude is None or longitude is None:
            return {'message': 'Latitude and longitude are required'}, 400
        
        # Simple bounding box search
        lat_delta = radius / 111.0
        lon_delta = radius / (111.0 * abs(latitude))
        
        scooters = list(Scooter.query.filter(
            (Scooter.latitude.between(latitude - lat_delta, latitude + lat_delta)) &
            (Scooter.longitude.between(longitude - lon_delta, longitude + lon_delta)) &
            (Scooter.status == 'available')
        ).limit(limit))
        
        # Calculate actual distances
        for scooter in scooters:
            scooter.distance = scooter.distance_from(latitude, longitude)
        
        # Sort by distance
        scooters.sort(key=lambda s: s.distance)
        
        return [s.to_dict() for s in scooters], 200

api.add_resource(ScooterListResource, '/scooters')
api.add_resource(ScooterResource, '/scooters/<int:scooter_id>')
api.add_resource(AvailableScootersResource, '/scooters/available')
api.add_resource(NearbyScootersResource, '/scooters/nearby')
