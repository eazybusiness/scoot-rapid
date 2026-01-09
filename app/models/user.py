"""
User model for ScootRapid using SQLAlchemy
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    role = db.Column(db.String(20), nullable=False, default='customer', index=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    scooters = db.relationship('Scooter', backref='provider', lazy='dynamic', foreign_keys='Scooter.provider_id')
    rentals = db.relationship('Rental', backref='user', lazy='dynamic', foreign_keys='Rental.user_id')
    payments = db.relationship('Payment', backref='user', lazy='dynamic', foreign_keys='Payment.user_id')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'email' in kwargs:
            self.email = kwargs['email'].lower()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_provider(self):
        return self.role == 'provider'
    
    def is_customer(self):
        return self.role == 'customer'
    
    def can_manage_scooters(self):
        return self.role in ['admin', 'provider']
    
    def get_stats(self):
        total_rentals = self.rentals.count()
        completed_rentals = self.rentals.filter_by(status='completed').all()
        
        total_spent = sum(r.total_cost for r in completed_rentals)
        avg_duration = sum(r.duration_minutes for r in completed_rentals if r.duration_minutes) / len(completed_rentals) if completed_rentals else 0
        
        return {
            'total_rentals': total_rentals,
            'total_spent': total_spent,
            'average_duration': avg_duration
        }
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'is_verified': self.is_verified,
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'
