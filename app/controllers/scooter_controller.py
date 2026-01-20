"""
Scooter controller for ScootRapid
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.controllers import scooter_bp
from app.models.scooter import Scooter
from app.models.rental import Rental

@scooter_bp.route('/')
@login_required
def list_scooters():
    """List all scooters"""
    if current_user.role == 'provider':
        scooters = Scooter.query.filter_by(provider_id=current_user.id).all()
    else:
        scooters = Scooter.query.limit(50).all()
    
    return render_template('scooters/list.html', scooters=scooters)

@scooter_bp.route('/available')
@login_required
def available():
    """List available scooters"""
    scooters = Scooter.query.filter(
        Scooter.status == 'available',
        Scooter.battery_level > 15
    ).limit(50).all()
    
    return render_template('scooters/available.html', scooters=scooters)

@scooter_bp.route('/<int:scooter_id>')
@login_required
def detail(scooter_id):
    """Scooter detail page"""
    scooter = Scooter.query.get(scooter_id)
    if not scooter:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    # Calculate rating statistics
    completed_rentals = Rental.query.filter_by(scooter_id=scooter.id, status='completed').all()
    ratings = [r.rating for r in completed_rentals if r.rating]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    total_ratings = len(ratings)
    
    stats = {
        'total_revenue': scooter.get_total_revenue(),
        'utilization_rate': scooter.get_utilization_rate(),
        'rental_count': Rental.query.filter_by(scooter_id=scooter.id).count(),
        'needs_maintenance': scooter.needs_maintenance(),
        'avg_rating': avg_rating,
        'total_ratings': total_ratings
    }
    
    # Generate QR code
    from app.utils.qr_generator import generate_qr_code_data
    qr_code_data = generate_qr_code_data(scooter)
    
    return render_template('scooters/detail.html', scooter=scooter, stats=stats, qr_code_data=qr_code_data)

@scooter_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new scooter"""
    if not current_user.can_manage_scooters():
        flash('You are not authorized to create scooters', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            identifier = request.form.get('identifier').upper()
            
            # Check if identifier exists
            existing_scooter = Scooter.query.filter_by(identifier=identifier).first()
            if existing_scooter:
                flash('Scooter with this identifier already exists', 'danger')
                return render_template('scooters/create.html')
            
            from app import db
            scooter = Scooter(
                identifier=identifier,
                license_plate=request.form.get('license_plate'),
                model=request.form.get('model'),
                brand=request.form.get('brand'),
                latitude=float(request.form.get('latitude')),
                longitude=float(request.form.get('longitude')),
                address=request.form.get('address'),
                battery_level=int(request.form.get('battery_level', 100)),
                provider_id=current_user.id
            )
            db.session.add(scooter)
            db.session.commit()
            
            flash('Scooter created successfully!', 'success')
            return redirect(url_for('scooters.detail', scooter_id=scooter.id))
            
        except Exception as e:
            flash(f'Error creating scooter: {str(e)}', 'danger')
            return render_template('scooters/create.html')
    
    return render_template('scooters/create.html')

@scooter_bp.route('/<int:scooter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(scooter_id):
    """Edit scooter"""
    scooter = Scooter.query.get(scooter_id)
    if not scooter:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider_id != current_user.id:
        flash('You are not authorized to edit this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    if request.method == 'POST':
        try:
            from app import db
            
            # Update all fields including identifier and license plate
            new_identifier = request.form.get('identifier').upper()
            
            # Check if identifier exists (excluding current scooter)
            existing_scooter = Scooter.query.filter(
                Scooter.identifier == new_identifier,
                Scooter.id != scooter_id
            ).first()
            if existing_scooter:
                flash('Scooter with this identifier already exists', 'danger')
                return render_template('scooters/edit.html', scooter=scooter)
            
            scooter.identifier = new_identifier
            scooter.license_plate = request.form.get('license_plate')
            scooter.model = request.form.get('model')
            scooter.brand = request.form.get('brand')
            scooter.address = request.form.get('address')
            scooter.latitude = float(request.form.get('latitude'))
            scooter.longitude = float(request.form.get('longitude'))
            scooter.location = request.form.get('location')
            scooter.battery_level = int(request.form.get('battery_level'))
            scooter.status = request.form.get('status')
            db.session.commit()
            
            flash('Scooter updated successfully!', 'success')
            return redirect(url_for('scooters.detail', scooter_id=scooter_id))
            
        except Exception as e:
            flash(f'Error updating scooter: {str(e)}', 'danger')
    
    return render_template('scooters/edit.html', scooter=scooter)

@scooter_bp.route('/<int:scooter_id>/delete', methods=['POST'])
@login_required
def delete(scooter_id):
    """Delete scooter"""
    scooter = Scooter.query.get(scooter_id)
    if not scooter:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider_id != current_user.id:
        flash('You are not authorized to delete this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    if scooter.get_current_rental():
        flash('Cannot delete scooter with active rental', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    try:
        from app import db
        from app.models.rental import Rental
        
        # Set scooter_id to None for all rentals to maintain data integrity
        rentals = Rental.query.filter_by(scooter_id=scooter.id).all()
        for rental in rentals:
            # Mark as allowed to have None scooter_id
            rental._allow_none_scooter_id = True
            rental.scooter_id = None
        
        # Now safely delete the scooter
        db.session.delete(scooter)
        db.session.commit()
        
        flash(f'Scooter deleted successfully! {len(rentals)} rental(s) preserved without scooter reference.', 'success')
        return redirect(url_for('scooters.list_scooters'))
    except Exception as e:
        flash(f'Error deleting scooter: {str(e)}', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))

@scooter_bp.route('/<int:scooter_id>/status', methods=['POST'])
@login_required
def update_status(scooter_id):
    """Update scooter status"""
    scooter = Scooter.query.get(scooter_id)
    if not scooter:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider_id != current_user.id:
        flash('You are not authorized to update this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    status = request.form.get('status')
    
    try:
        from app import db
        scooter.set_status(status)
        db.session.commit()
        flash('Status updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'danger')
    
    return redirect(url_for('scooters.detail', scooter_id=scooter_id))
