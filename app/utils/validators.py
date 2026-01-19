"""
Validation utilities for ScootRapid
"""

import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, ""

def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Validate geographic coordinates
    Returns: (is_valid, error_message)
    """
    if latitude is None or longitude is None:
        return False, "Latitude and longitude are required"
    
    if not (-90 <= latitude <= 90):
        return False, "Latitude must be between -90 and 90"
    
    if not (-180 <= longitude <= 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format
    Returns: (is_valid, error_message)
    """
    if not phone:
        return True, ""  # Phone is optional
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it contains only digits and optional + at start
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, ""

def validate_battery_level(level: int) -> Tuple[bool, str]:
    """
    Validate battery level
    Returns: (is_valid, error_message)
    """
    if level is None:
        return False, "Battery level is required"
    
    if not (0 <= level <= 100):
        return False, "Battery level must be between 0 and 100"
    
    return True, ""

def validate_rating(rating: int) -> Tuple[bool, str]:
    """
    Validate rating value
    Returns: (is_valid, error_message)
    """
    if rating is None:
        return False, "Rating is required"
    
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5"
    
    return True, ""
