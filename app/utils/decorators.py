"""
Decorators for ScootRapid
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def provider_required(f):
    """Decorator to require provider or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.can_manage_scooters():
            flash('Provider or admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
