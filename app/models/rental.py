"""
Rental model for ScootRapid using SQLAlchemy
"""

from datetime import datetime
from app import db

class Rental(db.Model):
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    rental_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooters.id'), index=True)
    
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    start_latitude = db.Column(db.Float, nullable=False)
    start_longitude = db.Column(db.Float, nullable=False)
    end_latitude = db.Column(db.Float)
    end_longitude = db.Column(db.Float)
    
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    
    duration_minutes = db.Column(db.Integer)
    distance_km = db.Column(db.Float)
    
    base_fee = db.Column(db.Float, default=1.50)
    per_minute_rate = db.Column(db.Float, default=0.30)
    total_cost = db.Column(db.Float, default=0.0)
    
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    payments = db.relationship('Payment', backref='rental', lazy='dynamic', foreign_keys='Payment.rental_id')
    
    def __init__(self, **kwargs):
        super(Rental, self).__init__(**kwargs)
        
        # Validation: scooter_id should not be None for new rentals
        # But allow None for existing rentals (when scooter is deleted)
        if self.scooter_id is None and not kwargs.get('_allow_none_scooter_id', False):
            raise ValueError("scooter_id cannot be None for new rentals - rental must be associated with a scooter")
        
        if not self.rental_code:
            self.rental_code = f"RNT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self.user_id}"
    
    def start_rental(self):
        from app.models.scooter import Scooter
        
        scooter = Scooter.query.get(self.scooter_id)
        if not scooter:
            raise ValueError("Scooter not found")
        
        if not scooter.is_available():
            raise ValueError("Scooter is not available")
        
        self.status = 'active'
        self.start_time = datetime.utcnow()
        
        scooter.set_status('in_use')
        
        db.session.commit()
    
    def end_rental(self, end_latitude=None, end_longitude=None):
        if self.status != 'active':
            raise ValueError("Rental is not active")
        
        self.end_time = datetime.utcnow()
        self.status = 'completed'
        
        if end_latitude and end_longitude:
            self.end_latitude = end_latitude
            self.end_longitude = end_longitude
        
        duration = (self.end_time - self.start_time).total_seconds() / 60
        self.duration_minutes = int(duration)
        
        self.total_cost = self.calculate_cost()
        
        # Handle deleted scooters gracefully
        if self.scooter_id is not None:
            from app.models.scooter import Scooter
            scooter = Scooter.query.get(self.scooter_id)
            if scooter:
                scooter.set_status('available')
                if end_latitude and end_longitude:
                    scooter.update_location(end_latitude, end_longitude)
        
        db.session.commit()
    
    def cancel_rental(self, reason=None):
        if self.status != 'active':
            raise ValueError("Only active rentals can be cancelled")
        
        self.status = 'cancelled'
        self.end_time = datetime.utcnow()
        
        duration = (self.end_time - self.start_time).total_seconds() / 60
        self.duration_minutes = int(duration)
        
        self.total_cost = min(self.calculate_cost(), self.base_fee)
        
        # Handle deleted scooters gracefully
        if self.scooter_id is not None:
            from app.models.scooter import Scooter
            scooter = Scooter.query.get(self.scooter_id)
            if scooter:
                scooter.set_status('available')
        
        db.session.commit()
    
    def calculate_cost(self):
        if not self.duration_minutes:
            if self.start_time:
                duration = (datetime.utcnow() - self.start_time).total_seconds() / 60
                return self.base_fee + (duration * self.per_minute_rate)
            return self.base_fee
        
        return self.base_fee + (self.duration_minutes * self.per_minute_rate)
    
    def get_duration_minutes(self):
        if self.duration_minutes:
            return self.duration_minutes
        
        if self.start_time:
            end = self.end_time or datetime.utcnow()
            return int((end - self.start_time).total_seconds() / 60)
        
        return 0
    
    def get_duration_formatted(self):
        """Return formatted duration string (e.g., '2 Stunden 30 Minuten')"""
        minutes = self.get_duration_minutes()
        
        if minutes < 60:
            return f"{minutes} Minuten"
        elif minutes < 1440:  # Less than 24 hours
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} Stunde{'n' if hours != 1 else ''}"
            else:
                return f"{hours} Stunde{'n' if hours != 1 else ''} {remaining_minutes} Minute{'n' if remaining_minutes != 1 else ''}"
        else:  # More than 24 hours
            days = minutes // 1440
            remaining_hours = (minutes % 1440) // 60
            if remaining_hours == 0:
                return f"{days} Tag{'e' if days != 1 else ''}"
            else:
                return f"{days} Tag{'e' if days != 1 else ''} {remaining_hours} Stunde{'n' if remaining_hours != 1 else ''}"
    
    def add_rating(self, rating, feedback=None):
        if self.status != 'completed':
            raise ValueError("Can only rate completed rentals")
        
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        # Allow scooter_id = None for deleted scooters, but warn
        if self.scooter_id is None:
            # Don't raise error - allow rating for rentals of deleted scooters
            pass
        
        self.rating = rating
        self.feedback = feedback
        db.session.commit()
    
    def check_overdue_status(self):
        from flask import current_app
        
        if self.status != 'active':
            return False
        
        max_hours = current_app.config.get('MAX_RENTAL_TIME_HOURS', 12)
        duration_hours = (datetime.utcnow() - self.start_time).total_seconds() / 3600
        
        if duration_hours > max_hours:
            self.status = 'overdue'
            db.session.commit()
            return True
        
        return False
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'rental_code': self.rental_code,
            'user_id': self.user_id,
            'scooter_id': self.scooter_id,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.get_duration_minutes(),
            'total_cost': float(self.total_cost) if self.total_cost else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Add scooter info only if scooter exists
        if self.scooter_id is not None:
            data['scooter'] = {
                'id': self.scooter.id,
                'identifier': self.scooter.identifier,
                'model': self.scooter.model,
                'brand': self.scooter.brand,
                'license_plate': self.scooter.license_plate
            }
        else:
            data['scooter'] = None  # Scooter was deleted
        
        if include_sensitive:
            data.update({
                'start_latitude': self.start_latitude,
                'start_longitude': self.start_longitude,
                'end_latitude': self.end_latitude,
                'end_longitude': self.end_longitude,
                'distance_km': self.distance_km,
                'base_fee': float(self.base_fee),
                'per_minute_rate': float(self.per_minute_rate),
                'rating': self.rating,
                'feedback': self.feedback,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<Rental {self.rental_code}>'
