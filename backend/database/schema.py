import logging
from typing import Dict, Any, List, Optional
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Manages database schema creation and migrations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the database schema manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        logger.info("Database schema manager initialized")
    
    def create_all_tables(self) -> None:
        """Create all database tables if they don't exist."""
        self._create_users_table()
        self._create_biometric_data_tables()
        self._create_behavioral_data_tables()
        self._create_anomaly_data_tables()
        logger.info("All database tables created successfully")
    
    def _create_users_table(self) -> None:
        """Create users table."""
        self.db.create_table(
            'users',
            """
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            last_login INTEGER
            """
        )
        
        # Create index on username and email
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        
        logger.info("Users table created successfully")
    
    def _create_biometric_data_tables(self) -> None:
        """Create tables for biometric data."""
        # Biometric profiles table
        self.db.create_table(
            'biometric_profiles',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            face_registered BOOLEAN DEFAULT FALSE,
            fingerprint_registered BOOLEAN DEFAULT FALSE,
            voice_registered BOOLEAN DEFAULT FALSE,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Face data table
        self.db.create_table(
            'face_data',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            face_encoding BLOB NOT NULL,
            face_image BLOB,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Fingerprint data table
        self.db.create_table(
            'fingerprint_data',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            finger_position TEXT NOT NULL,
            fingerprint_template BLOB NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Voice data table
        self.db.create_table(
            'voice_data',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            voice_embedding BLOB NOT NULL,
            voice_sample BLOB,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Authentication history table
        self.db.create_table(
            'auth_history',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            auth_type TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            confidence REAL,
            ip_address TEXT,
            device_info TEXT,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        logger.info("Biometric data tables created successfully")
    
    def _create_behavioral_data_tables(self) -> None:
        """Create tables for behavioral data."""
        # Behavior sessions table
        self.db.create_table(
            'behavior_sessions',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            device_info TEXT,
            ip_address TEXT,
            geo_location TEXT,
            started_at INTEGER NOT NULL,
            ended_at INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Keystroke data table
        self.db.create_table(
            'keystroke_data',
            """
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            key_code TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            duration INTEGER,
            pressure REAL,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Mouse data table
        self.db.create_table(
            'mouse_data',
            """
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            button TEXT,
            scroll_delta INTEGER,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Device data table
        self.db.create_table(
            'device_data',
            """
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_agent TEXT,
            screen_resolution TEXT,
            color_depth INTEGER,
            timezone TEXT,
            language TEXT,
            platform TEXT,
            device_memory INTEGER,
            hardware_concurrency INTEGER,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Geolocation data table
        self.db.create_table(
            'geo_data',
            """
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            ip_address TEXT,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Behavioral profiles table
        self.db.create_table(
            'behavioral_profiles',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            profile_type TEXT NOT NULL,
            profile_data BLOB NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        logger.info("Behavioral data tables created successfully")
    
    def _create_anomaly_data_tables(self) -> None:
        """Create tables for anomaly detection data."""
        # Anomaly models table
        self.db.create_table(
            'anomaly_models',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            model_type TEXT NOT NULL,
            component TEXT NOT NULL,
            model_data BLOB NOT NULL,
            accuracy REAL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Anomaly alerts table
        self.db.create_table(
            'anomaly_alerts',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            level TEXT NOT NULL,
            score REAL NOT NULL,
            component_scores TEXT NOT NULL,
            details TEXT,
            timestamp INTEGER NOT NULL,
            resolved BOOLEAN DEFAULT FALSE,
            resolved_at INTEGER,
            resolved_by TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE
            """
        )
        
        # Create index on user_id and timestamp
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_anomaly_alerts_user ON anomaly_alerts(user_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_anomaly_alerts_timestamp ON anomaly_alerts(timestamp)")
        
        logger.info("Anomaly data tables created successfully")
    
    def drop_all_tables(self) -> None:
        """Drop all database tables (for testing purposes)."""
        tables = [
            'anomaly_alerts', 'anomaly_models',
            'geo_data', 'device_data', 'mouse_data', 'keystroke_data',
            'behavioral_profiles', 'behavior_sessions',
            'auth_history', 'voice_data', 'fingerprint_data', 'face_data',
            'biometric_profiles', 'users'
        ]
        
        for table in tables:
            self.db.execute(f"DROP TABLE IF EXISTS {table}")
        
        logger.info("All database tables dropped successfully")