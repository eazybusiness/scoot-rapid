"""
Scooter model for ScootRapid using SQLAlchemy
"""

from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from app import db

class Scooter(db.Model):
    __tablename__ = 'scooters'
    
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.String(100), unique=True, index=True)
    
    model = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20))
    
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255))
    
    status = db.Column(db.String(20), nullable=False, default='available', index=True)
    battery_level = db.Column(db.Integer, default=100, nullable=False)
    
    max_speed = db.Column(db.Integer, default=25)
    range_km = db.Column(db.Integer, default=30)
    
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_maintenance = db.Column(db.DateTime)
    
    rentals = db.relationship('Rental', backref='scooter', lazy='dynamic', foreign_keys='Rental.scooter_id')
    
    def __init__(self, **kwargs):
        super(Scooter, self).__init__(**kwargs)
        if 'identifier' in kwargs:
            self.identifier = kwargs['identifier'].upper()
        if not self.qr_code:
            self.qr_code = f"SR-{self.identifier}-{datetime.utcnow().timestamp()}"
    
    def update_location(self, latitude, longitude, address=None):
        self.latitude = latitude
        self.longitude = longitude
        if address:
            self.address = address
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def set_status(self, status):
        valid_statuses = ['available', 'in_use', 'maintenance', 'offline']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        self.status = status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_available(self):
        return self.status == 'available' and self.battery_level > 15
    
    def needs_maintenance(self):
        if self.battery_level < 20:
            return True
        
        if self.last_maintenance:
            days_since_maintenance = (datetime.utcnow() - self.last_maintenance).days
            return days_since_maintenance > 30
        
        return False
    
    def distance_from(self, latitude, longitude):
        lat1, lon1, lat2, lon2 = map(radians, [self.latitude, self.longitude, latitude, longitude])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        r = 6371
        return c * r
    
    def get_current_rental(self):
        return self.rentals.filter_by(status='active').first()
    
    def get_total_revenue(self):
        completed_rentals = self.rentals.filter_by(status='completed').all()
        return sum(r.total_cost for r in completed_rentals)
    
    def get_utilization_rate(self):
        total_rentals = self.rentals.count()
        if total_rentals == 0:
            return 0.0
        
        completed_rentals = self.rentals.filter_by(status='completed').all()
        total_minutes = sum(r.duration_minutes for r in completed_rentals if r.duration_minutes)
        
        days_active = (datetime.utcnow() - self.created_at).days or 1
        available_minutes = days_active * 24 * 60
        
        return (total_minutes / available_minutes * 100) if available_minutes > 0 else 0.0
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'identifier': self.identifier,
            'model': self.model,
            'brand': self.brand,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'status': self.status,
            'battery_level': self.battery_level,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'qr_code': self.qr_code,
                'max_speed': self.max_speed,
                'range_km': self.range_km,
                'provider_id': self.provider_id,
                'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<Scooter {self.identifier}>'
