"""
Rental model for ScootRapid using Peewee ORM
"""

from datetime import datetime, timedelta
from peewee import *
from app import db

class Rental(Model):
    """Rental model tracking scooter usage and billing"""
    
    rental_code = CharField(unique=True, null=False, index=True)
    
    # Rental relationships
    user = ForeignKeyField(User, backref='rentals', null=False)
    scooter = ForeignKeyField(Scooter, backref='rentals', null=False)
    
    # Timing information
    start_time = DateTimeField(null=False)
    end_time = DateTimeField(null=True)
    duration_minutes = IntegerField(default=0)
    
    # Location tracking
    start_latitude = DecimalField(max_digits=10, decimal_places=8, null=False)
    start_longitude = DecimalField(max_digits=11, decimal_places=8, null=False)
    end_latitude = DecimalField(max_digits=10, decimal_places=8, null=True)
    end_longitude = DecimalField(max_digits=11, decimal_places=8, null=True)
    
    # Status tracking
    status = CharField(
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('overdue', 'Overdue')
        ],
        default='active',
        null=False,
        index=True
    )
    
    # Pricing information (stored in JSON for flexibility)
    pricing = JSONField(default=dict)
    total_cost = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional information
    notes = TextField(null=True)
    rating = IntegerField(null=True)  # 1-5 stars
    feedback = TextField(null=True)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow, null=False)
    updated_at = DateTimeField(default=datetime.utcnow, null=False)
    
    # Metadata for extensibility
    metadata = JSONField(default=dict)
    
    class Meta:
        database = db
        table_name = 'rentals'
        indexes = (
            (('user', 'status'), True),
            (('scooter', 'status'), True),
            (('start_time', 'end_time'), False),
        )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'rental_code') or not self.rental_code:
            self.rental_code = self.generate_rental_code()
        
        # Initialize default pricing if not provided
        if not hasattr(self, 'pricing') or not self.pricing:
            self.pricing = self.get_default_pricing()
    
    def save(self, force_insert=False, only=None):
        """Override save to update timestamps and validate"""
        self.updated_at = datetime.utcnow()
        
        # Validate duration
        if self.duration_minutes < 0:
            raise ValueError('Duration minutes cannot be negative')
        
        # Validate rating
        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        
        return super().save(force_insert, only)
    
    def generate_rental_code(self):
        """Generate unique rental code"""
        import uuid
        return f"SR-{uuid.uuid4().hex[:8].upper()}"
    
    def get_default_pricing(self):
        """Get default pricing configuration"""
        from flask import current_app
        
        return {
            'base_fee': current_app.config.get('START_FEE', 1.50),
            'per_minute_rate': current_app.config.get('BASE_PRICE_PER_MINUTE', 0.30),
            'currency': 'EUR'
        }
    
    def start_rental(self):
        """Start the rental process"""
        if not self.scooter.is_available():
            raise ValueError("Scooter is not available for rental")
        
        self.scooter.set_status('in_use')
        self.status = 'active'
        self.start_time = datetime.utcnow()
        self.save()
    
    def end_rental(self, end_latitude=None, end_longitude=None):
        """End the rental and calculate costs"""
        if self.status != 'active':
            raise ValueError("Rental is not active")
        
        # Update timing
        self.end_time = datetime.utcnow()
        self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        # Update end location
        if end_latitude and end_longitude:
            self.end_latitude = end_latitude
            self.end_longitude = end_longitude
            
            # Update scooter location
            self.scooter.update_location(end_latitude, end_longitude)
        
        # Calculate total cost
        self.calculate_cost()
        
        # Update status
        self.status = 'completed'
        
        # Make scooter available again
        self.scooter.set_status('available')
        
        self.save()
    
    def calculate_cost(self):
        """Calculate total rental cost"""
        base_fee = self.pricing.get('base_fee', 1.50)
        per_minute_rate = self.pricing.get('per_minute_rate', 0.30)
        
        if self.duration_minutes <= 0:
            self.total_cost = base_fee
        else:
            self.total_cost = base_fee + (self.duration_minutes * per_minute_rate)
    
    def cancel_rental(self, reason=None):
        """Cancel an active rental"""
        if self.status != 'active':
            raise ValueError("Only active rentals can be cancelled")
        
        # Update timing
        self.end_time = datetime.utcnow()
        self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        # Calculate partial cost (cancellation fee)
        base_fee = self.pricing.get('base_fee', 1.50)
        self.total_cost = base_fee  # Only charge base fee for cancellation
        self.notes = reason or "Cancelled by user"
        self.status = 'cancelled'
        
        # Make scooter available again
        self.scooter.set_status('available')
        
        self.save()
    
    def is_overdue(self):
        """Check if rental is overdue"""
        from flask import current_app
        
        max_hours = current_app.config.get('MAX_RENTAL_TIME_HOURS', 12)
        max_time = self.start_time + timedelta(hours=max_hours)
        
        return self.status == 'active' and datetime.utcnow() > max_time
    
    def check_overdue_status(self):
        """Check and update overdue status"""
        if self.is_overdue():
            self.status = 'overdue'
            self.save()
            return True
        return False
    
    def add_rating(self, rating, feedback=None):
        """Add rating and feedback for completed rental"""
        if self.status != 'completed':
            raise ValueError("Only completed rentals can be rated")
        
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        self.rating = rating
        self.feedback = feedback
        self.save()
    
    def get_payment_status(self):
        """Check payment status"""
        paid_amount = sum(p.amount for p in self.payments if p.status == 'completed')
        return {
            'total_cost': float(self.total_cost),
            'paid_amount': float(paid_amount),
            'outstanding': float(self.total_cost - paid_amount),
            'is_fully_paid': paid_amount >= self.total_cost
        }
    
    def get_duration_formatted(self):
        """Get formatted duration string"""
        if self.duration_minutes < 60:
            return f"{self.duration_minutes} minutes"
        else:
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            return f"{hours}h {minutes}m"
    
    def get_route_distance(self):
        """Calculate distance of the rental route"""
        if self.end_latitude and self.end_longitude:
            from math import radians, cos, sin, asin, sqrt
            
            lat1, lon1 = float(self.start_latitude), float(self.start_longitude)
            lat2, lon2 = float(self.end_latitude), float(self.end_longitude)
            
            # Convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
        return 0.0
    
    def to_dict(self, include_sensitive=False):
        """Convert rental to dictionary"""
        data = {
            'id': self.id,
            'rental_code': self.rental_code,
            'user_id': self.user.id,
            'scooter_id': self.scooter.id,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'duration_formatted': self.get_duration_formatted(),
            'start_location': {
                'latitude': float(self.start_latitude),
                'longitude': float(self.start_longitude)
            },
            'total_cost': float(self.total_cost),
            'created_at': self.created_at.isoformat()
        }
        
        if self.end_latitude and self.end_longitude:
            data['end_location'] = {
                'latitude': float(self.end_latitude),
                'longitude': float(self.end_longitude)
            }
            data['route_distance_km'] = round(self.get_route_distance(), 2)
        
        if include_sensitive:
            data.update({
                'pricing': self.pricing,
                'rating': self.rating,
                'feedback': self.feedback,
                'notes': self.notes,
                'user_name': self.user.get_full_name(),
                'scooter_identifier': self.scooter.identifier,
                'scooter_model': f"{self.scooter.brand} {self.scooter.model}",
                'payment_status': self.get_payment_status(),
                'is_overdue': self.is_overdue(),
                'metadata': self.metadata
            })
        
        return data
    
    def __str__(self):
        return f'{self.rental_code}'

# Import related models at the end to avoid circular imports
from .user import User
from .scooter import Scooter
from .payment import Payment
