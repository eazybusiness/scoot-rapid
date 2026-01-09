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
        rentals = list(Rental.select().order_by(Rental.created_at.desc()).limit(50))
    else:
        rentals = list(Rental.select()
                      .where(Rental.user == current_user)
                      .order_by(Rental.created_at.desc())
                      .limit(50))
    
    return render_template('rentals/list.html', rentals=rentals)

@rental_bp.route('/<int:rental_id>')
@login_required
def detail(rental_id):
    """Rental detail page"""
    try:
        rental = Rental.get_by_id(rental_id)
    except Rental.DoesNotExist:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    # Check access
    if not current_user.is_admin() and rental.user.id != current_user.id:
        if not (current_user.is_provider() and rental.scooter.provider.id == current_user.id):
            flash('You are not authorized to view this rental', 'danger')
            return redirect(url_for('rentals.list_rentals'))
    
    return render_template('rentals/detail.html', rental=rental)

@rental_bp.route('/start/<int:scooter_id>', methods=['GET', 'POST'])
@login_required
def start(scooter_id):
    """Start a rental"""
    try:
        scooter = Scooter.get_by_id(scooter_id)
    except Scooter.DoesNotExist:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.available'))
    
    if not scooter.is_available():
        flash('Scooter is not available', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    # Check if user has active rental
    try:
        active_rental = Rental.get(
            (Rental.user == current_user) & (Rental.status == 'active')
        )
        flash('You already have an active rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=active_rental.id))
    except Rental.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            latitude = float(request.form.get('latitude', scooter.latitude))
            longitude = float(request.form.get('longitude', scooter.longitude))
            
            rental = Rental.create(
                user=current_user,
                scooter=scooter,
                start_latitude=latitude,
                start_longitude=longitude
            )
            
            rental.start_rental()
            
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
    try:
        rental = Rental.get_by_id(rental_id)
    except Rental.DoesNotExist:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.status != 'active':
        flash('Rental is not active', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    if not current_user.is_admin() and rental.user.id != current_user.id:
        flash('You are not authorized to end this rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    try:
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        rental.end_rental(latitude, longitude)
        
        flash('Rental ended successfully!', 'success')
    except Exception as e:
        flash(f'Error ending rental: {str(e)}', 'danger')
    
    return redirect(url_for('rentals.detail', rental_id=rental_id))

@rental_bp.route('/<int:rental_id>/cancel', methods=['POST'])
@login_required
def cancel(rental_id):
    """Cancel a rental"""
    try:
        rental = Rental.get_by_id(rental_id)
    except Rental.DoesNotExist:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.status != 'active':
        flash('Only active rentals can be cancelled', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    if not current_user.is_admin() and rental.user.id != current_user.id:
        flash('You are not authorized to cancel this rental', 'danger')
        return redirect(url_for('rentals.detail', rental_id=rental_id))
    
    try:
        reason = request.form.get('reason')
        rental.cancel_rental(reason)
        
        flash('Rental cancelled', 'info')
    except Exception as e:
        flash(f'Error cancelling rental: {str(e)}', 'danger')
    
    return redirect(url_for('rentals.detail', rental_id=rental_id))

@rental_bp.route('/<int:rental_id>/rate', methods=['POST'])
@login_required
def rate(rental_id):
    """Rate a rental"""
    try:
        rental = Rental.get_by_id(rental_id)
    except Rental.DoesNotExist:
        flash('Rental not found', 'danger')
        return redirect(url_for('rentals.list_rentals'))
    
    if rental.user.id != current_user.id:
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
