"""
Scooter model for ScootRapid using Peewee ORM
"""

from datetime import datetime
from peewee import *
from app import db

class Scooter(Model):
    """Scooter model with location and status tracking"""
    
    identifier = CharField(unique=True, null=False, index=True)
    model = CharField(null=False)
    brand = CharField(null=False)
    
    # Location information
    latitude = DecimalField(max_digits=10, decimal_places=8, null=False)
    longitude = DecimalField(max_digits=11, decimal_places=8, null=False)
    address = CharField(null=True)
    last_location_update = DateTimeField(default=datetime.utcnow)
    
    # Status management
    status = CharField(
        choices=[
            ('available', 'Available'),
            ('in_use', 'In Use'),
            ('maintenance', 'Maintenance'),
            ('offline', 'Offline')
        ],
        default='available',
        null=False,
        index=True
    )
    battery_level = IntegerField(default=100, null=False)  # 0-100%
    
    # Technical specifications (stored in JSON for flexibility)
    specs = JSONField(default=dict)
    
    # QR code for rental
    qr_code = CharField(unique=True, null=False)
    
    # Provider relationship
    provider = ForeignKeyField(User, backref='scooters', null=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow, null=False)
    updated_at = DateTimeField(default=datetime.utcnow, null=False)
    last_maintenance = DateTimeField(null=True)
    
    # Additional metadata
    metadata = JSONField(default=dict)
    
    class Meta:
        database = db
        table_name = 'scooters'
        indexes = (
            (('status', 'latitude', 'longitude'), False),
            (('provider', 'status'), True),
            (('battery_level',), False),
        )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'identifier' in kwargs:
            self.identifier = kwargs['identifier'].upper()
        if 'model' in kwargs:
            self.model = kwargs['model'].title()
        if 'brand' in kwargs:
            self.brand = kwargs['brand'].title()
        if not hasattr(self, 'qr_code') or not self.qr_code:
            self.qr_code = self.generate_qr_code()
    
    def save(self, force_insert=False, only=None):
        """Override save to update timestamps and validate"""
        self.updated_at = datetime.utcnow()
        
        # Validate battery level
        if not (0 <= self.battery_level <= 100):
            raise ValueError('Battery level must be between 0 and 100')
        
        return super().save(force_insert, only)
    
    def generate_qr_code(self):
        """Generate unique QR code for scooter"""
        import uuid
        return f"SR-{uuid.uuid4().hex[:8].upper()}-{self.identifier}"
    
    def update_location(self, latitude, longitude, address=None):
        """Update scooter location"""
        self.latitude = latitude
        self.longitude = longitude
        if address:
            self.address = address
        self.last_location_update = datetime.utcnow()
        self.save()
    
    def set_status(self, status):
        """Update scooter status with validation"""
        valid_statuses = ['available', 'in_use', 'maintenance', 'offline']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        self.status = status
        self.save()
    
    def is_available(self):
        """Check if scooter is available for rental"""
        return self.status == 'available' and self.battery_level > 15
    
    def needs_maintenance(self):
        """Check if scooter needs maintenance"""
        if self.battery_level < 20:
            return True
        
        if self.last_maintenance:
            days_since_maintenance = (datetime.utcnow() - self.last_maintenance).days
            return days_since_maintenance > 30
        
        return False
    
    def get_current_rental(self):
        """Get currently active rental"""
        try:
            return Rental.get((Rental.scooter == self) & (Rental.status == 'active'))
        except Rental.DoesNotExist:
            return None
    
    def get_rental_history(self, limit=10):
        """Get rental history"""
        return list(Rental.select()
                   .where(Rental.scooter == self)
                   .order_by(Rental.created_at.desc())
                   .limit(limit))
    
    def get_total_revenue(self):
        """Calculate total revenue from this scooter"""
        query = (Payment
                .select(fn.SUM(Payment.amount))
                .join(Rental)
                .where(Rental.scooter == self))
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def get_utilization_rate(self, days=30):
        """Calculate utilization rate for last N days"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Calculate total minutes used in the period
        query = (Rental
                .select(fn.SUM(Rental.duration_minutes))
                .where(
                    (Rental.scooter == self) &
                    (Rental.start_time >= start_date) &
                    (Rental.status == 'completed')
                ))
        
        result = query.scalar()
        total_minutes_used = int(result) if result else 0
        total_possible_minutes = days * 24 * 60  # Total minutes in the period
        
        return (total_minutes_used / total_possible_minutes) * 100 if total_possible_minutes > 0 else 0
    
    def distance_from(self, latitude, longitude):
        """Calculate distance from given coordinates (in kilometers)"""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = float(self.latitude), float(self.longitude)
        lat2, lon2 = float(latitude), float(longitude)
        
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
    
    def get_specs(self):
        """Get technical specifications"""
        default_specs = {
            'max_speed': 25,  # km/h
            'range_km': 30,   # km on full battery
            'weight': 15,     # kg
            'motor_power': 350  # watts
        }
        return {**default_specs, **self.specs}
    
    def update_specs(self, new_specs):
        """Update technical specifications"""
        self.specs = {**self.specs, **new_specs}
        self.save()
    
    def to_dict(self, include_sensitive=False):
        """Convert scooter to dictionary"""
        data = {
            'id': self.id,
            'identifier': self.identifier,
            'model': self.model,
            'brand': self.brand,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'address': self.address,
            'status': self.status,
            'battery_level': self.battery_level,
            'is_available': self.is_available(),
            'specs': self.get_specs(),
            'created_at': self.created_at.isoformat(),
            'last_location_update': self.last_location_update.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'qr_code': self.qr_code,
                'provider_id': self.provider.id,
                'provider_name': self.provider.get_full_name(),
                'total_revenue': self.get_total_revenue(),
                'utilization_rate': self.get_utilization_rate(),
                'rental_count': Rental.select().where(Rental.scooter == self).count(),
                'needs_maintenance': self.needs_maintenance(),
                'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
                'metadata': self.metadata
            })
        
        return data
    
    def __str__(self):
        return f'{self.identifier}'

# Import related models at the end to avoid circular imports
from .user import User
from .rental import Rental
from .payment import Payment
