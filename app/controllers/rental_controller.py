"""
Rental controller for ScootRapid
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.controllers import rental_bp
from app.models.rental import Rental
from app.models.scooter import Scooter

@rental_bp.route('/')
@login_required
def list_rentals():
    """List rentals"""
    if current_user.is_admin():
        rentals = Rental.query.order_by(Rental.created_at.desc()).limit(50).all()
    else:
        rentals = Rental.query.filter_by(user_id=current_user.id).order_by(Rental.created_at.desc()).limit(50).all()
    
    return render_template('rentals/list.html', rentals=rentals)

@rental_bp.route('/<int:rental_id>')
@login_required
def detail(rental_id):
    """Rental detail page"""
    rental = Rental.query.get(rental_id)
    if not rental:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    # Check access
    if not current_user.is_admin() and rental.user_id != current_user.id:
        if not (current_user.is_provider() and rental.scooter.provider_id == current_user.id):
            flash('You are not authorized to view this rental', 'danger')
            return redirect(url_for('rentals.list_rentals'))
    
    return render_template('rentals/detail.html', rental=rental)

@rental_bp.route('/start/<int:scooter_id>', methods=['GET', 'POST'])
@login_required
def start(scooter_id):
    """Start a rental"""
    scooter = Scooter.query.get(scooter_id)
    if not scooter:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.available'))
    
    if not scooter.is_available():
        flash('Scooter is not available', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    # Prevent providers from renting their own scooters
    if current_user.is_provider() and scooter.provider_id == current_user.id:
        flash('Providers cannot rent their own scooters', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    # Check if user has active rental
    active_rental = Rental.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).first()
    if active_rental:
        flash('You already have an active rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=active_rental.id))
    
    if request.method == 'POST':
        try:
            from app import db
            latitude = float(request.form.get('latitude', scooter.latitude))
            longitude = float(request.form.get('longitude', scooter.longitude))
            
            rental = Rental(
                user_id=current_user.id,
                scooter_id=scooter.id,
                start_latitude=latitude,
                start_longitude=longitude
            )
            
            rental.start_rental()
            db.session.add(rental)
            db.session.commit()
            
            flash('Rental started successfully!', 'success')
            return redirect(url_for('rentals.detail', rental_id=rental.id))
            
        except Exception as e:
            flash(f'Error starting rental: {str(e)}', 'danger')
            return render_template('rentals/start.html', scooter=scooter)
    
    return render_template('rentals/start.html', scooter=scooter)

@rental_bp.route('/<int:rental_id>/end', methods=['POST'])
@login_required
def end(rental_id):
    """End a rental"""
    rental = Rental.query.get(rental_id)
    if not rental:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.status != 'active':
        flash('Rental is not active', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    if not current_user.is_admin() and rental.user_id != current_user.id:
        flash('You are not authorized to end this rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    try:
        from app import db
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        rental.end_rental(latitude, longitude)
        db.session.commit()
        
        flash('Rental ended successfully!', 'success')
    except Exception as e:
        flash(f'Error ending rental: {str(e)}', 'danger')
    
    return redirect(url_for('rentals.detail', rental_id=rental_id))

@rental_bp.route('/<int:rental_id>/cancel', methods=['POST'])
@login_required
def cancel(rental_id):
    """Cancel a rental"""
    rental = Rental.query.get(rental_id)
    if not rental:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.status != 'active':
        flash('Only active rentals can be cancelled', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    if not current_user.is_admin() and rental.user_id != current_user.id:
        flash('You are not authorized to cancel this rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    try:
        from app import db
        reason = request.form.get('reason')
        rental.cancel_rental(reason)
        db.session.commit()
        
        flash('Rental cancelled', 'info')
    except Exception as e:
        flash(f'Error cancelling rental: {str(e)}', 'danger')
    
    return redirect(url_for('rentals.detail', rental_id=rental_id))

@rental_bp.route('/<int:rental_id>/rate', methods=['POST'])
@login_required
def rate(rental_id):
    """Rate a rental"""
    rental = Rental.query.get(rental_id)
    if not rental:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.user_id != current_user.id:
        flash('You are not authorized to rate this rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    try:
        rating = int(request.form.get('rating'))
        feedback = request.form.get('feedback')
        
        rental.add_rating(rating, feedback)
        
        flash('Thank you for your rating!', 'success')
    except Exception as e:
        flash(f'Error adding rating: {str(e)}', 'danger')
    
    return redirect(url_for('rentals.detail', rental_id=rental_id))
