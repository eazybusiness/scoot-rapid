"""
Main dashboard controller for ScootRapid
"""

from flask import render_template
from flask_login import login_required, current_user
from app.controllers import main_bp
from app.models.user import User
from app.models.scooter import Scooter
from app.models.rental import Rental

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if current_user.role == 'admin':
        return admin_dashboard()
    elif current_user.role == 'provider':
        return provider_dashboard()
    else:
        return customer_dashboard()

def admin_dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    total_scooters = Scooter.query.count()
    total_rentals = Rental.query.count()
    active_rentals = Rental.query.filter_by(status='active').count()
    
    recent_rentals = Rental.query.order_by(Rental.created_at.desc()).limit(10).all()
    
    available_scooters = Scooter.query.filter_by(status='available').count()
    in_use_scooters = Scooter.query.filter_by(status='in_use').count()
    maintenance_scooters = Scooter.query.filter_by(status='maintenance').count()
    
    return render_template('dashboard/admin.html',
                         total_users=total_users,
                         total_scooters=total_scooters,
                         total_rentals=total_rentals,
                         active_rentals=active_rentals,
                         recent_rentals=recent_rentals,
                         available_scooters=available_scooters,
                         in_use_scooters=in_use_scooters,
                         maintenance_scooters=maintenance_scooters)

def provider_dashboard():
    """Provider dashboard"""
    scooters = Scooter.query.filter_by(provider_id=current_user.id).all()
    
    total_scooters = len(scooters)
    available = len([s for s in scooters if s.status == 'available'])
    in_use = len([s for s in scooters if s.status == 'in_use'])
    maintenance = len([s for s in scooters if s.status == 'maintenance'])
    
    total_revenue = sum(s.get_total_revenue() for s in scooters)
    
    recent_rentals = []
    for scooter in scooters[:10]:
        rentals = Rental.query.filter_by(scooter_id=scooter.id).order_by(Rental.created_at.desc()).limit(5).all()
        recent_rentals.extend(rentals)
    
    recent_rentals = sorted(recent_rentals, key=lambda r: r.created_at, reverse=True)[:10]
    
    return render_template('dashboard/provider.html',
                         scooters=scooters,
                         total_scooters=total_scooters,
                         available=available,
                         in_use=in_use,
                         maintenance=maintenance,
                         total_revenue=total_revenue,
                         recent_rentals=recent_rentals)

def customer_dashboard():
    """Customer dashboard"""
    # Get active rental (SQLAlchemy syntax)
    active_rental = Rental.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).first()
    
    # Get rental history (SQLAlchemy syntax)
    rental_history = Rental.query.filter_by(
        user_id=current_user.id
    ).order_by(Rental.created_at.desc()).limit(10).all()
    
    user_stats = current_user.get_stats()
    
    # Get available scooters (SQLAlchemy syntax)
    nearby_scooters = Scooter.query.filter_by(
        status='available'
    ).limit(10).all()
    
    return render_template('dashboard/customer.html',
                         active_rental=active_rental,
                         rental_history=rental_history,
                         user_stats=user_stats,
                         nearby_scooters=nearby_scooters)

from app.models.user import User
