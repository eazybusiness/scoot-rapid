"""
User model for ScootRapid using Peewee ORM
"""

from datetime import datetime
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, Model):
    """User model with authentication and authorization"""
    
    email = CharField(unique=True, null=False, index=True)
    password_hash = CharField(null=False)
    first_name = CharField(null=False)
    last_name = CharField(null=False)
    phone = CharField(null=True)
    
    # Role-based access control
    role = CharField(
        choices=[('admin', 'Admin'), ('provider', 'Provider'), ('customer', 'Customer')],
        default='customer',
        null=False
    )
    
    # Account status
    is_active = BooleanField(default=True, null=False)
    is_verified = BooleanField(default=False, null=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow, null=False)
    updated_at = DateTimeField(default=datetime.utcnow, null=False)
    last_login = DateTimeField(null=True)
    
    # JSON fields for flexible data storage
    metadata = JSONField(default=dict)
    preferences = JSONField(default=dict)
    
    class Meta:
        database = db
        table_name = 'users'
        indexes = (
            (('email', 'is_active'), True),
            (('role', 'created_at'), False),
        )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'email' in kwargs:
            self.email = kwargs['email'].lower()
        if 'first_name' in kwargs:
            self.first_name = kwargs['first_name'].title()
        if 'last_name' in kwargs:
            self.last_name = kwargs['last_name'].title()
    
    def save(self, force_insert=False, only=None):
        """Override save to update timestamps"""
        self.updated_at = datetime.utcnow()
        return super().save(force_insert, only)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def is_provider(self):
        """Check if user is a provider"""
        return self.role == 'provider'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def can_manage_scooters(self):
        """Check if user can manage scooters"""
        return self.role in ['admin', 'provider']
    
    def get_active_rentals(self):
        """Get currently active rentals"""
        return list(Rental.select().where(
            (Rental.user == self) & (Rental.status == 'active')
        ))
    
    def get_rental_history(self, limit=10):
        """Get rental history"""
        return list(Rental.select()
                   .where(Rental.user == self)
                   .order_by(Rental.created_at.desc())
                   .limit(limit))
    
    def get_total_spent(self):
        """Calculate total amount spent on rentals"""
        query = (Payment
                .select(fn.SUM(Payment.amount))
                .join(Rental)
                .where(Rental.user == self))
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def get_scooter_count(self):
        """Get number of scooters owned by provider"""
        if self.is_provider():
            return Scooter.select().where(Scooter.provider == self).count()
        return 0
    
    def get_stats(self):
        """Get user statistics"""
        return {
            'total_rentals': Rental.select().where(Rental.user == self).count(),
            'total_spent': self.get_total_spent(),
            'scooter_count': self.get_scooter_count(),
            'active_rentals': len(self.get_active_rentals()),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'metadata': self.metadata,
                'preferences': self.preferences,
                'stats': self.get_stats()
            })
        
        return data
    
    @classmethod
    def create_admin(cls, email, password, first_name, last_name):
        """Create an admin user"""
        try:
            admin = cls.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='admin'
            )
            admin.set_password(password)
            admin.save()
            return admin
        except IntegrityError:
            raise ValueError('User with this email already exists')
    
    def __str__(self):
        return f'{self.email}'

# Import related models at the end to avoid circular imports
from .scooter import Scooter
from .rental import Rental
from .payment import Payment
