"""
Payment model for ScootRapid using SQLAlchemy
"""

from datetime import datetime
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=False, index=True)
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='CHF', nullable=False)
    
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    
    gateway_transaction_id = db.Column(db.String(255))
    
    refund_amount = db.Column(db.Float, default=0.0)
    refund_reason = db.Column(db.Text)
    refunded_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        if not self.transaction_id:
            self.transaction_id = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self.user_id}"
    
    def process_payment(self, gateway_transaction_id=None, gateway_response=None):
        if self.status != 'pending':
            raise ValueError(f"Cannot process payment with status: {self.status}")
        
        self.status = 'processing'
        
        if gateway_transaction_id:
            self.gateway_transaction_id = gateway_transaction_id
        
        db.session.commit()
    
    def complete_payment(self, gateway_transaction_id=None, gateway_response=None):
        if self.status == 'completed':
            raise ValueError("Payment is already completed")
        
        self.status = 'completed'
        self.processed_at = datetime.utcnow()
        
        if gateway_transaction_id:
            self.gateway_transaction_id = gateway_transaction_id
        
        db.session.commit()
    
    def fail_payment(self, gateway_response=None):
        self.status = 'failed'
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def refund_payment(self, refund_amount=None, reason=None):
        if self.status != 'completed':
            raise ValueError("Can only refund completed payments")
        
        if refund_amount is None:
            refund_amount = self.amount - self.refund_amount
        
        if refund_amount <= 0:
            raise ValueError("Refund amount must be greater than 0")
        
        if self.refund_amount + refund_amount > self.amount:
            raise ValueError("Refund amount exceeds payment amount")
        
        self.refund_amount += refund_amount
        self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
        
        if self.refund_amount >= self.amount:
            self.status = 'refunded'
        
        db.session.commit()
    
    def is_refundable(self):
        if self.status != 'completed':
            return False
        
        if self.refund_amount >= self.amount:
            return False
        
        days_since_payment = (datetime.utcnow() - self.created_at).days
        return days_since_payment <= 30
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'rental_id': self.rental_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'gateway_transaction_id': self.gateway_transaction_id,
                'refund_amount': float(self.refund_amount),
                'refund_reason': self.refund_reason,
                'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
                'processed_at': self.processed_at.isoformat() if self.processed_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
