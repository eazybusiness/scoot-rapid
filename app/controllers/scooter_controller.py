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
    """List scooters"""
    if current_user.is_provider():
        scooters = list(Scooter.select().where(Scooter.provider == current_user))
    else:
        scooters = list(Scooter.select().limit(50))
    
    return render_template('scooters/list.html', scooters=scooters)

@scooter_bp.route('/available')
@login_required
def available():
    """List available scooters"""
    scooters = list(Scooter.select().where(
        (Scooter.status == 'available') & (Scooter.battery_level > 15)
    ).limit(50))
    
    return render_template('scooters/available.html', scooters=scooters)

@scooter_bp.route('/<int:scooter_id>')
@login_required
def detail(scooter_id):
    """Scooter detail page"""
    try:
        scooter = Scooter.get_by_id(scooter_id)
    except Scooter.DoesNotExist:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    stats = {
        'total_revenue': scooter.get_total_revenue(),
        'utilization_rate': scooter.get_utilization_rate(),
        'rental_count': Rental.select().where(Rental.scooter == scooter).count(),
        'needs_maintenance': scooter.needs_maintenance()
    }
    
    return render_template('scooters/detail.html', scooter=scooter, stats=stats)

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
            try:
                Scooter.get(Scooter.identifier == identifier)
                flash('Scooter with this identifier already exists', 'danger')
                return render_template('scooters/create.html')
            except Scooter.DoesNotExist:
                pass
            
            scooter = Scooter.create(
                identifier=identifier,
                model=request.form.get('model'),
                brand=request.form.get('brand'),
                latitude=float(request.form.get('latitude')),
                longitude=float(request.form.get('longitude')),
                address=request.form.get('address'),
                battery_level=int(request.form.get('battery_level', 100)),
                provider=current_user
            )
            
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
    try:
        scooter = Scooter.get_by_id(scooter_id)
    except Scooter.DoesNotExist:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider.id != current_user.id:
        flash('You are not authorized to edit this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    if request.method == 'POST':
        try:
            scooter.model = request.form.get('model')
            scooter.brand = request.form.get('brand')
            scooter.address = request.form.get('address')
            scooter.battery_level = int(request.form.get('battery_level'))
            scooter.save()
            
            flash('Scooter updated successfully!', 'success')
            return redirect(url_for('scooters.detail', scooter_id=scooter_id))
            
        except Exception as e:
            flash(f'Error updating scooter: {str(e)}', 'danger')
    
    return render_template('scooters/edit.html', scooter=scooter)

@scooter_bp.route('/<int:scooter_id>/delete', methods=['POST'])
@login_required
def delete(scooter_id):
    """Delete scooter"""
    try:
        scooter = Scooter.get_by_id(scooter_id)
    except Scooter.DoesNotExist:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider.id != current_user.id:
        flash('You are not authorized to delete this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    if scooter.get_current_rental():
        flash('Cannot delete scooter with active rental', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    try:
        scooter.delete_instance()
        flash('Scooter deleted successfully!', 'success')
        return redirect(url_for('scooters.list_scooters'))
    except Exception as e:
        flash(f'Error deleting scooter: {str(e)}', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))

@scooter_bp.route('/<int:scooter_id>/status', methods=['POST'])
@login_required
def update_status(scooter_id):
    """Update scooter status"""
    try:
        scooter = Scooter.get_by_id(scooter_id)
    except Scooter.DoesNotExist:
        flash('Scooter not found', 'danger')
        return redirect(url_for('scooters.list_scooters'))
    
    if not current_user.is_admin() and scooter.provider.id != current_user.id:
        flash('You are not authorized to update this scooter', 'danger')
        return redirect(url_for('scooters.detail', scooter_id=scooter_id))
    
    status = request.form.get('status')
    
    try:
        scooter.set_status(status)
        flash('Status updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'danger')
    
    return redirect(url_for('scooters.detail', scooter_id=scooter_id))
