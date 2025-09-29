import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(name: str = None, level: int = logging.INFO, 
               log_file: Optional[str] = None, max_size: int = 10485760, 
               backup_count: int = 5) -> logging.Logger:
    """Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name (defaults to root logger if None)
        level: Logging level
        log_file: Path to log file (optional)
        max_size: Maximum log file size in bytes before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger
    """
    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:  
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger