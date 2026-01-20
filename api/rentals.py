"""
Rental API endpoints for ScootRapid
"""

from flask import request
from flask_restful import Resource
from flask_login import current_user, login_required
from marshmallow import Schema, fields, ValidationError
from api import api
from app.models.rental import Rental
from app.models.scooter import Scooter

class StartRentalSchema(Schema):
    scooter_id = fields.Int(required=True)
    start_latitude = fields.Float(required=True)
    start_longitude = fields.Float(required=True)

class EndRentalSchema(Schema):
    end_latitude = fields.Float()
    end_longitude = fields.Float()

class RatingSchema(Schema):
    rating = fields.Int(required=True)
    feedback = fields.Str()

start_rental_schema = StartRentalSchema()
end_rental_schema = EndRentalSchema()
rating_schema = RatingSchema()

class RentalListResource(Resource):
    @login_required
    def get(self):
        """Get rentals"""
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        if current_user.is_admin():
            query = Rental.query
        else:
            query = Rental.query.filter(Rental.user == current_user)
        
        if status:
            query = query.filter(Rental.status == status)
        
        rentals = list(query.order_by(Rental.created_at.desc()).limit(limit))
        
        return [r.to_dict() for r in rentals], 200
    
    @login_required
    def post(self):
        """Start a new rental"""
        try:
            data = start_rental_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Check if user has active rental
        active_rental = Rental.query.filter_by(user_id=current_user.id, status='active').first()
        if active_rental:
            return {'message': 'User already has an active rental'}, 400
        
        # Get scooter
        scooter = Scooter.query.get(data['scooter_id'])
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        # Prevent providers from renting their own scooters
        if current_user.is_provider() and scooter.provider_id == current_user.id:
            return {'message': 'Providers cannot rent their own scooters'}, 400
        
        if not scooter.is_available():
            return {'message': 'Scooter is not available'}, 400
        
        try:
            from app import db
            rental = Rental(
                user_id=current_user.id,
                scooter_id=scooter.id,
                start_latitude=data['start_latitude'],
                start_longitude=data['start_longitude']
            )
            db.session.add(rental)
            db.session.commit()
            
            rental.start_rental()
            
            return rental.to_dict(include_sensitive=True), 201
            
        except Exception as e:
            return {'message': f'Error starting rental: {str(e)}'}, 400

class RentalResource(Resource):
    @login_required
    def get(self, rental_id):
        """Get rental by ID"""
        try:
            rental = Rental.query.get(rental_id)
        except Rental.DoesNotExist:
            return {'message': 'Rental not found'}, 404
        
        # Check access
        if not current_user.is_admin() and rental.user.id != current_user.id:
            if not (current_user.is_provider() and rental.scooter and rental.scooter.provider.id == current_user.id):
                return {'message': 'Not authorized'}, 403
        
        include_sensitive = current_user.is_admin() or rental.user.id == current_user.id
        
        return rental.to_dict(include_sensitive=include_sensitive), 200

class EndRentalResource(Resource):
    @login_required
    def post(self, rental_id):
        """End an active rental"""
        try:
            rental = Rental.query.get(rental_id)
        except Rental.DoesNotExist:
            return {'message': 'Rental not found'}, 404
        
        if rental.status != 'active':
            return {'message': 'Rental is not active'}, 400
        
        if not current_user.is_admin() and rental.user.id != current_user.id:
            return {'message': 'Not authorized'}, 403
        
        try:
            data = end_rental_schema.load(request.get_json() or {})
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        try:
            rental.end_rental(
                data.get('end_latitude'),
                data.get('end_longitude')
            )
            
            return rental.to_dict(include_sensitive=True), 200
            
        except Exception as e:
            return {'message': f'Error ending rental: {str(e)}'}, 400

class CancelRentalResource(Resource):
    @login_required
    def post(self, rental_id):
        """Cancel an active rental"""
        try:
            rental = Rental.query.get(rental_id)
        except Rental.DoesNotExist:
            return {'message': 'Rental not found'}, 404
        
        if rental.status != 'active':
            return {'message': 'Only active rentals can be cancelled'}, 400
        
        if not current_user.is_admin() and rental.user.id != current_user.id:
            return {'message': 'Not authorized'}, 403
        
        data = request.get_json() or {}
        reason = data.get('reason')
        
        try:
            rental.cancel_rental(reason)
            return rental.to_dict(include_sensitive=True), 200
        except Exception as e:
            return {'message': f'Error cancelling rental: {str(e)}'}, 400

class RateRentalResource(Resource):
    @login_required
    def post(self, rental_id):
        """Rate a completed rental"""
        try:
            rental = Rental.query.get(rental_id)
        except Rental.DoesNotExist:
            return {'message': 'Rental not found'}, 404
        
        if rental.user.id != current_user.id:
            return {'message': 'Not authorized'}, 403
        
        try:
            data = rating_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        try:
            rental.add_rating(data['rating'], data.get('feedback'))
            return {'message': 'Rating added successfully'}, 200
        except Exception as e:
            return {'message': f'Error adding rating: {str(e)}'}, 400

class ActiveRentalsResource(Resource):
    @login_required
    def get(self):
        """Get active rentals"""
        if current_user.is_admin():
            rentals = list(Rental.query.filter(Rental.status == 'active'))
        else:
            try:
                rental = Rental.get(
                    (Rental.user == current_user) & (Rental.status == 'active')
                )
                rentals = [rental]
            except Rental.DoesNotExist:
                rentals = []
        
        return [r.to_dict() for r in rentals], 200

api.add_resource(RentalListResource, '/rentals')
api.add_resource(RentalResource, '/rentals/<int:rental_id>')
api.add_resource(EndRentalResource, '/rentals/<int:rental_id>/end')
api.add_resource(CancelRentalResource, '/rentals/<int:rental_id>/cancel')
api.add_resource(RateRentalResource, '/rentals/<int:rental_id>/rate')
api.add_resource(ActiveRentalsResource, '/rentals/active')
