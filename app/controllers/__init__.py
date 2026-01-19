"""
Controllers for ScootRapid
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
scooter_bp = Blueprint('scooters', __name__, url_prefix='/scooters')
rental_bp = Blueprint('rentals', __name__, url_prefix='/rentals')

from app.controllers import auth_controller, main_controller, scooter_controller, rental_controller
