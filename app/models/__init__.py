"""
ScootRapid Models
"""

from .user import User
from .scooter import Scooter
from .rental import Rental
from .payment import Payment

__all__ = ['User', 'Scooter', 'Rental', 'Payment']
