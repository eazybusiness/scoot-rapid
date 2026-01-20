"""
Helper utilities for ScootRapid
"""

from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

def format_currency(amount: float, currency: str = 'CHF') -> str:
    """
    Format amount as currency
    """
    if currency == 'CHF':
        return f"CHF {amount:.2f}"
    elif currency == 'EUR':
        return f"€{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string
    """
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    
    return f"{hours}h {mins}min"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def format_datetime(dt: datetime, format_str: str = '%d.%m.%Y %H:%M') -> str:
    """
    Format datetime to string
    """
    if not dt:
        return ''
    
    return dt.strftime(format_str)

def time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string
    """
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days != 1 else ""} ago'
    else:
        return format_datetime(dt, '%d.%m.%Y')

def generate_qr_code_data(scooter_id: int, identifier: str) -> str:
    """
    Generate QR code data for scooter
    """
    return f"SR-{scooter_id}-{identifier}"

def calculate_rental_cost(duration_minutes: int, base_fee: float = 1.50, 
                         per_minute_rate: float = 0.30) -> float:
    """
    Calculate rental cost
    """
    if duration_minutes <= 0:
        return base_fee
    
    return base_fee + (duration_minutes * per_minute_rate)

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def paginate(items: list, page: int = 1, per_page: int = 20) -> dict:
    """
    Paginate a list of items
    Returns dict with items, page info
    """
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
