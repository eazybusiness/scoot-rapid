from flask import Blueprint, jsonify, request
from app.models.scooter import Scooter
from app.models.rental import Rental
from app.models.user import User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API Health Check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/login', methods=['POST'])
def api_login():
    """API Login Endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@api_bp.route('/scooters', methods=['GET'])
@jwt_required()
def get_scooters():
    """Get all scooters"""
    try:
        scooters = Scooter.query.all()
        return jsonify({
            'scooters': [
                {
                    'id': scooter.id,
                    'model': scooter.model,
                    'license_plate': scooter.license_plate,
                    'location': scooter.location,
                    'battery_level': scooter.battery_level,
                    'status': scooter.status,
                    'created_at': scooter.created_at.isoformat() if scooter.created_at else None
                }
                for scooter in scooters
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch scooters', 'details': str(e)}), 500

@api_bp.route('/scooters/available', methods=['GET'])
@jwt_required()
def get_available_scooters():
    """Get available scooters"""
    try:
        scooters = Scooter.query.filter_by(status='available').all()
        return jsonify({
            'scooters': [
                {
                    'id': scooter.id,
                    'model': scooter.model,
                    'license_plate': scooter.license_plate,
                    'location': scooter.location,
                    'battery_level': scooter.battery_level
                }
                for scooter in scooters
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch available scooters', 'details': str(e)}), 500

@api_bp.route('/scooters/<int:scooter_id>', methods=['GET'])
@jwt_required()
def get_scooter(scooter_id):
    """Get specific scooter"""
    try:
        scooter = Scooter.query.get_or_404(scooter_id)
        return jsonify({
            'id': scooter.id,
            'model': scooter.model,
            'license_plate': scooter.license_plate,
            'location': scooter.location,
            'battery_level': scooter.battery_level,
            'status': scooter.status,
            'created_at': scooter.created_at.isoformat() if scooter.created_at else None
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch scooter', 'details': str(e)}), 500

@api_bp.route('/rentals', methods=['GET'])
@jwt_required()
def get_rentals():
    """Get user rentals"""
    try:
        user_id = get_jwt_identity()
        rentals = Rental.query.filter_by(user_id=user_id).all()
        return jsonify({
            'rentals': [
                {
                    'id': rental.id,
                    'scooter': {
                        'id': rental.scooter.id,
                        'model': rental.scooter.model,
                        'license_plate': rental.scooter.license_plate
                    },
                    'start_time': rental.start_time.isoformat() if rental.start_time else None,
                    'end_time': rental.end_time.isoformat() if rental.end_time else None,
                    'status': rental.status,
                    'total_cost': rental.total_cost,
                    'duration_formatted': rental.get_duration_formatted()
                }
                for rental in rentals
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch rentals', 'details': str(e)}), 500

@api_bp.route('/rentals/<int:rental_id>', methods=['GET'])
@jwt_required()
def get_rental(rental_id):
    """Get specific rental"""
    try:
        user_id = get_jwt_identity()
        rental = Rental.query.filter_by(id=rental_id, user_id=user_id).first_or_404()
        return jsonify({
            'id': rental.id,
            'scooter': {
                'id': rental.scooter.id,
                'model': rental.scooter.model,
                'license_plate': rental.scooter.license_plate
            },
            'start_time': rental.start_time.isoformat() if rental.start_time else None,
            'end_time': rental.end_time.isoformat() if rental.end_time else None,
            'status': rental.status,
            'total_cost': rental.total_cost,
            'base_fee': rental.base_fee,
            'per_minute_rate': rental.per_minute_rate,
            'duration_formatted': rental.get_duration_formatted()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch rental', 'details': str(e)}), 500

@api_bp.route('/rentals/start', methods=['POST'])
@jwt_required()
def start_rental():
    """Start a new rental"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or not data.get('scooter_id'):
            return jsonify({'error': 'Scooter ID required'}), 400
        
        scooter = Scooter.query.get_or_404(data['scooter_id'])
        
        if scooter.status != 'available':
            return jsonify({'error': 'Scooter not available'}), 400
        
        # Check if user has active rental
        active_rental = Rental.query.filter_by(user_id=user_id, status='active').first()
        if active_rental:
            return jsonify({'error': 'User already has an active rental'}), 400
        
        # Create new rental
        rental = Rental(
            user_id=user_id,
            scooter_id=data['scooter_id'],
            start_time=datetime.utcnow(),
            status='active'
        )
        
        # Update scooter status
        scooter.status = 'in_use'
        
        db.session.add(rental)
        db.session.commit()
        
        return jsonify({
            'message': 'Rental started successfully',
            'rental': {
                'id': rental.id,
                'scooter': {
                    'id': scooter.id,
                    'model': scooter.model,
                    'license_plate': scooter.license_plate
                },
                'start_time': rental.start_time.isoformat(),
                'status': rental.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to start rental', 'details': str(e)}), 500

@api_bp.route('/rentals/<int:rental_id>/end', methods=['POST'])
@jwt_required()
def end_rental(rental_id):
    """End a rental"""
    try:
        user_id = get_jwt_identity()
        rental = Rental.query.filter_by(id=rental_id, user_id=user_id, status='active').first_or_404()
        
        # Calculate cost and end rental
        rental.end_time = datetime.utcnow()
        rental.total_cost = rental.calculate_cost()
        rental.status = 'completed'
        
        # Update scooter status
        rental.scooter.status = 'available'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rental ended successfully',
            'rental': {
                'id': rental.id,
                'end_time': rental.end_time.isoformat(),
                'total_cost': rental.total_cost,
                'duration_formatted': rental.get_duration_formatted(),
                'status': rental.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to end rental', 'details': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get user statistics"""
    try:
        user_id = get_jwt_identity()
        
        total_rentals = Rental.query.filter_by(user_id=user_id).count()
        completed_rentals = Rental.query.filter_by(user_id=user_id, status='completed').count()
        total_spent = db.session.query(db.func.sum(Rental.total_cost)).filter_by(user_id=user_id).scalar() or 0
        
        return jsonify({
            'total_rentals': total_rentals,
            'completed_rentals': completed_rentals,
            'total_spent': float(total_spent),
            'active_rental': Rental.query.filter_by(user_id=user_id, status='active').first() is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch stats', 'details': str(e)}), 500
