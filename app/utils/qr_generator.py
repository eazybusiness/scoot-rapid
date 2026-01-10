"""
QR Code Generator for ScootRapid
"""

import qrcode
import io
import base64
from flask import url_for

def generate_qr_code_data(scooter):
    """Generate QR code data URI for a scooter"""
    # Create QR code with scooter information
    qr_data = f"SR-SCOOTER-{scooter.id}-{scooter.qr_code}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="#1a237e", back_color="white")
    
    # Convert to base64 for HTML embedding
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

def generate_rental_qr_code(rental):
    """Generate QR code for active rental"""
    qr_data = f"SR-RENTAL-{rental.id}-{rental.qr_code or rental.id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#27ae60", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"
