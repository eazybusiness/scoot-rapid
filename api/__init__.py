"""
API Blueprint for ScootRapid using Flask-RESTful
"""

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

from api import auth, scooters, rentals, users
