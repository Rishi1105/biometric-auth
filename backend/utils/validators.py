import re
from typing import Tuple, Optional

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"
    
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None

def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_username(username: str, min_length: int = 3, max_length: int = 30) -> Tuple[bool, Optional[str]]:
    """Validate username format.
    
    Args:
        username: Username to validate
        min_length: Minimum username length
        max_length: Maximum username length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < min_length:
        return False, f"Username must be at least {min_length} characters long"
    
    if len(username) > max_length:
        return False, f"Username must be at most {max_length} characters long"
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, None

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number cannot be empty"
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s()-]', '', phone)
    
    # Check if it's a valid phone number (simple check for digits and length)
    if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, None