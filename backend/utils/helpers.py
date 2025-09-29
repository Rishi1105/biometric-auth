import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional

def generate_id(prefix: str = '') -> str:
    """Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def current_timestamp() -> int:
    """Get current Unix timestamp.
    
    Returns:
        Current Unix timestamp in seconds
    """
    return int(time.time())

def format_datetime(timestamp: Optional[int] = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format timestamp as datetime string.
    
    Args:
        timestamp: Unix timestamp in seconds (defaults to current time)
        format_str: DateTime format string
        
    Returns:
        Formatted datetime string
    """
    if timestamp is None:
        timestamp = current_timestamp()
        
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)

def parse_datetime(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> int:
    """Parse datetime string to timestamp.
    
    Args:
        datetime_str: Datetime string to parse
        format_str: DateTime format string
        
    Returns:
        Unix timestamp in seconds
    """
    dt = datetime.strptime(datetime_str, format_str)
    return int(dt.timestamp())

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested dictionaries
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def safe_get(d: Dict[str, Any], key_path: str, default: Any = None, sep: str = '.') -> Any:
    """Safely get a value from a nested dictionary.
    
    Args:
        d: Dictionary to get value from
        key_path: Path to key (e.g. 'a.b.c')
        default: Default value if key not found
        sep: Separator for key path
        
    Returns:
        Value at key path or default
    """
    keys = key_path.split(sep)
    result = d
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
            
    return result