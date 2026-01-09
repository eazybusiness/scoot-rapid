"""
Payment model for ScootRapid using Peewee ORM
"""

from datetime import datetime
from peewee import *
from app import db

class Payment(Model):
    """Payment model for rental transactions"""
    
    transaction_id = CharField(unique=True, null=False, index=True)
    
    # Payment relationships
    user = ForeignKeyField(User, backref='payments', null=False)
    rental = ForeignKeyField(Rental, backref='payments', null=False)
    
    # Payment details
    amount = DecimalField(max_digits=10, decimal_places=2, null=False)
    currency = CharField(default='EUR', null=False)
    payment_method = CharField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash', 'Cash')
        ],
        null=False
    )
    
    # Payment status
    status = CharField(
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ],
        default='pending',
        null=False,
        index=True
    )
    
    # Payment gateway information (stored in JSON for flexibility)
    gateway_data = JSONField(default=dict)
    
    # Refund information
    refund_amount = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_reason = TextField(null=True)
    refund_date = DateTimeField(null=True)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow, null=False)
    updated_at = DateTimeField(default=datetime.utcnow, null=False)
    processed_at = DateTimeField(null=True)
    
    # Additional metadata
    metadata = JSONField(default=dict)
    
    class Meta:
        database = db
        table_name = 'payments'
        indexes = (
            (('user', 'status'), True),
            (('rental',), True),
            (('created_at',), False),
        )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'transaction_id') or not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
    
    def save(self, force_insert=False, only=None):
        """Override save to update timestamps and validate"""
        self.updated_at = datetime.utcnow()
        
        # Validate amounts
        if self.amount < 0:
            raise ValueError('Amount cannot be negative')
        if self.refund_amount < 0:
            raise ValueError('Refund amount cannot be negative')
        
        return super().save(force_insert, only)
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import uuid
        return f"SR-PAY-{uuid.uuid4().hex[:12].upper()}"
    
    def process_payment(self, gateway_transaction_id=None, gateway_response=None):
        """Mark payment as processing"""
        self.status = 'processing'
        self.processed_at = datetime.utcnow()
        
        if gateway_transaction_id:
            self.gateway_data['gateway_transaction_id'] = gateway_transaction_id
        if gateway_response:
            self.gateway_data['gateway_response'] = gateway_response
        
        self.save()
    
    def complete_payment(self, gateway_transaction_id=None, gateway_response=None):
        """Mark payment as completed"""
        self.status = 'completed'
        self.processed_at = datetime.utcnow()
        
        if gateway_transaction_id:
            self.gateway_data['gateway_transaction_id'] = gateway_transaction_id
        if gateway_response:
            self.gateway_data['gateway_response'] = gateway_response
        
        self.save()
    
    def fail_payment(self, gateway_response=None):
        """Mark payment as failed"""
        self.status = 'failed'
        self.processed_at = datetime.utcnow()
        
        if gateway_response:
            self.gateway_data['gateway_response'] = gateway_response
        
        self.save()
    
    def refund_payment(self, refund_amount=None, reason=None):
        """Process refund"""
        if self.status != 'completed':
            raise ValueError("Only completed payments can be refunded")
        
        if refund_amount is None:
            refund_amount = self.amount
        
        if refund_amount > self.amount:
            raise ValueError("Refund amount cannot exceed payment amount")
        
        self.refund_amount = refund_amount
        self.refund_reason = reason
        self.refund_date = datetime.utcnow()
        
        if refund_amount >= self.amount:
            self.status = 'refunded'
        
        self.save()
    
    def is_refundable(self):
        """Check if payment can be refunded"""
        return (self.status == 'completed' and 
                self.refund_amount < self.amount and
                (datetime.utcnow() - self.created_at).days <= 30)  # 30-day refund window
    
    def get_refundable_amount(self):
        """Get amount that can be refunded"""
        if not self.is_refundable():
            return 0.0
        return float(self.amount - self.refund_amount)
    
    def get_payment_method_display(self):
        """Get display name for payment method"""
        method_names = {
            'credit_card': 'Credit Card',
            'paypal': 'PayPal',
            'bank_transfer': 'Bank Transfer',
            'cash': 'Cash'
        }
        return method_names.get(self.payment_method, self.payment_method)
    
    def get_status_display(self):
        """Get display name for status"""
        status_names = {
            'pending': 'Pending',
            'processing': 'Processing',
            'completed': 'Completed',
            'failed': 'Failed',
            'refunded': 'Refunded'
        }
        return status_names.get(self.status, self.status)
    
    def add_metadata(self, key, value):
        """Add metadata entry"""
        self.metadata[key] = value
        self.save()
    
    def get_gateway_info(self):
        """Get gateway information"""
        return {
            'gateway_transaction_id': self.gateway_data.get('gateway_transaction_id'),
            'gateway_response': self.gateway_data.get('gateway_response'),
            'gateway_error': self.gateway_data.get('gateway_error')
        }
    
    def to_dict(self, include_sensitive=False):
        """Convert payment to dictionary"""
        data = {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'user_id': self.user.id,
            'rental_id': self.rental.id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_method_display': self.get_payment_method_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
        
        if include_sensitive:
            data.update({
                'gateway_info': self.get_gateway_info(),
                'refund_amount': float(self.refund_amount),
                'refund_reason': self.refund_reason,
                'refund_date': self.refund_date.isoformat() if self.refund_date else None,
                'user_name': self.user.get_full_name(),
                'rental_code': self.rental.rental_code,
                'is_refundable': self.is_refundable(),
                'refundable_amount': self.get_refundable_amount(),
                'metadata': self.metadata
            })
        
        return data
    
    def __str__(self):
        return f'{self.transaction_id}'

# Import related models at the end to avoid circular imports
from .user import User
from .rental import Rental
