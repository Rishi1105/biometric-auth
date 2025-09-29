import os
import logging
import argparse
from typing import Dict, Any

from .db_manager import DatabaseManager
from .schema import DatabaseSchema

logger = logging.getLogger(__name__)

def init_database(config: Dict[str, Any] = None) -> None:
    """Initialize the database with schema and default data.
    
    Args:
        config: Optional configuration dictionary
    """
    if config is None:
        config = {
            'db_uri': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/biometric_auth'),
            'db_name': os.environ.get('DB_NAME', 'biometric_auth')
        }
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    
    # Initialize schema manager
    schema_manager = DatabaseSchema(db_manager)
    
    # Create all tables
    schema_manager.create_all_tables()
    
    logger.info("Database initialized successfully")
    return db_manager

def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description='Initialize the biometric authentication database')
    parser.add_argument('--reset', action='store_true', help='Reset the database (drop all tables)')
    parser.add_argument('--db-uri', help='Database URI')
    parser.add_argument('--db-name', help='Database name')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Prepare configuration
    config = {
        'db_uri': args.db_uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/biometric_auth'),
        'db_name': args.db_name or os.environ.get('DB_NAME', 'biometric_auth')
    }
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    
    # Initialize schema manager
    schema_manager = DatabaseSchema(db_manager)
    
    if args.reset:
        logger.warning("Resetting database (dropping all tables)")
        schema_manager.drop_all_tables()
    
    # Create all tables
    schema_manager.create_all_tables()
    
    logger.info("Database initialized successfully")

if __name__ == '__main__':
    main()