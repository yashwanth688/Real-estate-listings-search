import re

def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """
    Validate password strength.
    Requires at least 8 characters.
    For a beginner project, we keep it simple.
    """
    return len(password) >= 8

def validate_property_data(data):
    """Validate property form submission."""
    errors = []
    
    if not data.get('title') or len(data.get('title')) < 5:
        errors.append("Title must be at least 5 characters long.")
        
    try:
        price = float(data.get('price', 0))
        if price <= 0:
            errors.append("Price must be greater than zero.")
    except ValueError:
        errors.append("Invalid price format.")
        
    if not data.get('location'):
        errors.append("Location is required.")
        
    try:
        area = int(data.get('area', 0))
        if area <= 0:
            errors.append("Area must be greater than zero.")
    except ValueError:
        errors.append("Invalid area format.")
        
    return errors
