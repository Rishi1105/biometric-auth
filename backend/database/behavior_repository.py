import os
import logging
import json
import time
import uuid
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union

from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class BehaviorRepository:
    """Repository for behavioral data storage and retrieval."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the behavior repository.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
        # Initialize database tables
        self._init_tables()
        
        logger.info("Behavior repository initialized")
    
    def _init_tables(self) -> None:
        """Initialize database tables for behavioral data."""
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
            timestamp INTEGER NOT NULL,
            key_code INTEGER,
            key_name TEXT,
            press_time INTEGER,
            release_time INTEGER,
            dwell_time INTEGER,
            flight_time INTEGER,
            context TEXT,
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
            timestamp INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            x INTEGER,
            y INTEGER,
            button TEXT,
            movement_speed REAL,
            movement_direction REAL,
            click_duration INTEGER,
            context TEXT,
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
            timestamp INTEGER NOT NULL,
            device_type TEXT,
            os_name TEXT,
            os_version TEXT,
            browser_name TEXT,
            browser_version TEXT,
            screen_width INTEGER,
            screen_height INTEGER,
            color_depth INTEGER,
            timezone TEXT,
            language TEXT,
            plugins TEXT,
            user_agent TEXT,
            fingerprint TEXT,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Geo data table
        self.db.create_table(
            'geo_data',
            """
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            ip_address TEXT,
            country TEXT,
            region TEXT,
            city TEXT,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Behavior profiles table
        self.db.create_table(
            'behavior_profiles',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            profile_type TEXT NOT NULL,
            profile_data BLOB NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            version INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Create indexes
        self.db.create_index('behavior_sessions', ['user_id'])
        self.db.create_index('keystroke_data', ['user_id', 'session_id'])
        self.db.create_index('keystroke_data', ['timestamp'])
        self.db.create_index('mouse_data', ['user_id', 'session_id'])
        self.db.create_index('mouse_data', ['timestamp'])
        self.db.create_index('device_data', ['user_id', 'session_id'])
        self.db.create_index('geo_data', ['user_id', 'session_id'])
        self.db.create_index('behavior_profiles', ['user_id', 'profile_type'], unique=True)
        
        logger.info("Behavior tables initialized")
    
    def create_session(self, user_id: str, session_type: str, device_info: Optional[Dict[str, Any]] = None, 
                      ip_address: Optional[str] = None, geo_location: Optional[Dict[str, Any]] = None) -> str:
        """Create a new behavior session.
        
        Args:
            user_id: User ID
            session_type: Session type (e.g., 'login', 'continuous')
            device_info: Device information (optional)
            ip_address: IP address (optional)
            geo_location: Geographic location (optional)
            
        Returns:
            Session ID
        """
        try:
            session_id = str(uuid.uuid4())
            now = int(time.time())
            
            self.db.insert(
                'behavior_sessions',
                {
                    'id': session_id,
                    'user_id': user_id,
                    'session_type': session_type,
                    'device_info': json.dumps(device_info) if device_info else None,
                    'ip_address': ip_address,
                    'geo_location': json.dumps(geo_location) if geo_location else None,
                    'started_at': now,
                    'ended_at': None
                }
            )
            
            logger.info(f"Created behavior session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating behavior session for user {user_id}: {e}")
            raise
    
    def end_session(self, session_id: str) -> bool:
        """End a behavior session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            now = int(time.time())
            
            rows_affected = self.db.update(
                'behavior_sessions',
                {'ended_at': now},
                "id = ? AND ended_at IS NULL",
                (session_id,)
            )
            
            if rows_affected > 0:
                logger.info(f"Ended behavior session {session_id}")
                return True
            else:
                logger.warning(f"Session {session_id} not found or already ended")
                return False
                
        except Exception as e:
            logger.error(f"Error ending behavior session {session_id}: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a behavior session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        try:
            session = self.db.fetch_one(
                "SELECT * FROM behavior_sessions WHERE id = ?",
                (session_id,)
            )
            
            if session:
                # Parse JSON fields
                if session.get('device_info'):
                    session['device_info'] = json.loads(session['device_info'])
                if session.get('geo_location'):
                    session['geo_location'] = json.loads(session['geo_location'])
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting behavior session {session_id}: {e}")
            raise
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent behavior sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of session data
        """
        try:
            sessions = self.db.fetch_all(
                "SELECT * FROM behavior_sessions WHERE user_id = ? ORDER BY started_at DESC LIMIT ?",
                (user_id, limit)
            )
            
            # Parse JSON fields
            for session in sessions:
                if session.get('device_info'):
                    session['device_info'] = json.loads(session['device_info'])
                if session.get('geo_location'):
                    session['geo_location'] = json.loads(session['geo_location'])
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting behavior sessions for user {user_id}: {e}")
            raise
    
    def store_keystroke_data(self, session_id: str, user_id: str, keystroke_data: Dict[str, Any]) -> str:
        """Store keystroke data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            keystroke_data: Keystroke data
            
        Returns:
            Data ID
        """
        try:
            data_id = str(uuid.uuid4())
            
            # Prepare data
            data = {
                'id': data_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': keystroke_data.get('timestamp', int(time.time())),
                'key_code': keystroke_data.get('key_code'),
                'key_name': keystroke_data.get('key_name'),
                'press_time': keystroke_data.get('press_time'),
                'release_time': keystroke_data.get('release_time'),
                'dwell_time': keystroke_data.get('dwell_time'),
                'flight_time': keystroke_data.get('flight_time'),
                'context': keystroke_data.get('context')
            }
            
            self.db.insert('keystroke_data', data)
            return data_id
            
        except Exception as e:
            logger.error(f"Error storing keystroke data for session {session_id}: {e}")
            raise
    
    def store_keystroke_batch(self, session_id: str, user_id: str, keystroke_batch: List[Dict[str, Any]]) -> int:
        """Store a batch of keystroke data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            keystroke_batch: List of keystroke data
            
        Returns:
            Number of records inserted
        """
        try:
            # Prepare data
            now = int(time.time())
            params_list = []
            
            for keystroke in keystroke_batch:
                data_id = str(uuid.uuid4())
                params = (
                    data_id,
                    session_id,
                    user_id,
                    keystroke.get('timestamp', now),
                    keystroke.get('key_code'),
                    keystroke.get('key_name'),
                    keystroke.get('press_time'),
                    keystroke.get('release_time'),
                    keystroke.get('dwell_time'),
                    keystroke.get('flight_time'),
                    keystroke.get('context')
                )
                params_list.append(params)
            
            # Insert batch
            query = """
                INSERT INTO keystroke_data 
                (id, session_id, user_id, timestamp, key_code, key_name, press_time, 
                release_time, dwell_time, flight_time, context) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_many(query, params_list)
            return len(params_list)
            
        except Exception as e:
            logger.error(f"Error storing keystroke batch for session {session_id}: {e}")
            raise
    
    def get_keystroke_data(self, session_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get keystroke data for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of records to return
            
        Returns:
            List of keystroke data
        """
        try:
            return self.db.fetch_all(
                "SELECT * FROM keystroke_data WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
                (session_id, limit)
            )
            
        except Exception as e:
            logger.error(f"Error getting keystroke data for session {session_id}: {e}")
            raise
    
    def get_user_keystroke_data(self, user_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get keystroke data for a user across all sessions.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of keystroke data
        """
        try:
            return self.db.fetch_all(
                "SELECT * FROM keystroke_data WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            
        except Exception as e:
            logger.error(f"Error getting keystroke data for user {user_id}: {e}")
            raise
    
    def store_mouse_data(self, session_id: str, user_id: str, mouse_data: Dict[str, Any]) -> str:
        """Store mouse data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            mouse_data: Mouse data
            
        Returns:
            Data ID
        """
        try:
            data_id = str(uuid.uuid4())
            
            # Prepare data
            data = {
                'id': data_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': mouse_data.get('timestamp', int(time.time())),
                'event_type': mouse_data.get('event_type'),  # 'move', 'click', 'scroll'
                'x': mouse_data.get('x'),
                'y': mouse_data.get('y'),
                'button': mouse_data.get('button'),  # 'left', 'right', 'middle'
                'movement_speed': mouse_data.get('movement_speed'),
                'movement_direction': mouse_data.get('movement_direction'),
                'click_duration': mouse_data.get('click_duration'),
                'context': mouse_data.get('context')
            }
            
            self.db.insert('mouse_data', data)
            return data_id
            
        except Exception as e:
            logger.error(f"Error storing mouse data for session {session_id}: {e}")
            raise
    
    def store_mouse_batch(self, session_id: str, user_id: str, mouse_batch: List[Dict[str, Any]]) -> int:
        """Store a batch of mouse data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            mouse_batch: List of mouse data
            
        Returns:
            Number of records inserted
        """
        try:
            # Prepare data
            now = int(time.time())
            params_list = []
            
            for mouse_event in mouse_batch:
                data_id = str(uuid.uuid4())
                params = (
                    data_id,
                    session_id,
                    user_id,
                    mouse_event.get('timestamp', now),
                    mouse_event.get('event_type'),
                    mouse_event.get('x'),
                    mouse_event.get('y'),
                    mouse_event.get('button'),
                    mouse_event.get('movement_speed'),
                    mouse_event.get('movement_direction'),
                    mouse_event.get('click_duration'),
                    mouse_event.get('context')
                )
                params_list.append(params)
            
            # Insert batch
            query = """
                INSERT INTO mouse_data 
                (id, session_id, user_id, timestamp, event_type, x, y, button, 
                movement_speed, movement_direction, click_duration, context) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_many(query, params_list)
            return len(params_list)
            
        except Exception as e:
            logger.error(f"Error storing mouse batch for session {session_id}: {e}")
            raise
    
    def get_mouse_data(self, session_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get mouse data for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of records to return
            
        Returns:
            List of mouse data
        """
        try:
            return self.db.fetch_all(
                "SELECT * FROM mouse_data WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
                (session_id, limit)
            )
            
        except Exception as e:
            logger.error(f"Error getting mouse data for session {session_id}: {e}")
            raise
    
    def get_user_mouse_data(self, user_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get mouse data for a user across all sessions.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of mouse data
        """
        try:
            return self.db.fetch_all(
                "SELECT * FROM mouse_data WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            
        except Exception as e:
            logger.error(f"Error getting mouse data for user {user_id}: {e}")
            raise
    
    def store_device_data(self, session_id: str, user_id: str, device_data: Dict[str, Any]) -> str:
        """Store device data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            device_data: Device data
            
        Returns:
            Data ID
        """
        try:
            data_id = str(uuid.uuid4())
            
            # Prepare data
            data = {
                'id': data_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': device_data.get('timestamp', int(time.time())),
                'device_type': device_data.get('device_type'),
                'os_name': device_data.get('os_name'),
                'os_version': device_data.get('os_version'),
                'browser_name': device_data.get('browser_name'),
                'browser_version': device_data.get('browser_version'),
                'screen_width': device_data.get('screen_width'),
                'screen_height': device_data.get('screen_height'),
                'color_depth': device_data.get('color_depth'),
                'timezone': device_data.get('timezone'),
                'language': device_data.get('language'),
                'plugins': json.dumps(device_data.get('plugins')) if device_data.get('plugins') else None,
                'user_agent': device_data.get('user_agent'),
                'fingerprint': device_data.get('fingerprint')
            }
            
            self.db.insert('device_data', data)
            return data_id
            
        except Exception as e:
            logger.error(f"Error storing device data for session {session_id}: {e}")
            raise
    
    def get_device_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get device data for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Device data or None if not found
        """
        try:
            device_data = self.db.fetch_one(
                "SELECT * FROM device_data WHERE session_id = ? ORDER BY timestamp DESC LIMIT 1",
                (session_id,)
            )
            
            if device_data and device_data.get('plugins'):
                device_data['plugins'] = json.loads(device_data['plugins'])
            
            return device_data
            
        except Exception as e:
            logger.error(f"Error getting device data for session {session_id}: {e}")
            raise
    
    def get_user_devices(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get devices used by a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of devices to return
            
        Returns:
            List of device data
        """
        try:
            # Get unique devices by fingerprint
            devices = self.db.fetch_all(
                """
                SELECT DISTINCT ON (fingerprint) * FROM device_data 
                WHERE user_id = ? 
                ORDER BY fingerprint, timestamp DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
            
            # Parse JSON fields
            for device in devices:
                if device.get('plugins'):
                    device['plugins'] = json.loads(device['plugins'])
            
            return devices
            
        except Exception as e:
            logger.error(f"Error getting devices for user {user_id}: {e}")
            raise
    
    def store_geo_data(self, session_id: str, user_id: str, geo_data: Dict[str, Any]) -> str:
        """Store geographic location data.
        
        Args:
            session_id: Session ID
            user_id: User ID
            geo_data: Geographic location data
            
        Returns:
            Data ID
        """
        try:
            data_id = str(uuid.uuid4())
            
            # Prepare data
            data = {
                'id': data_id,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': geo_data.get('timestamp', int(time.time())),
                'latitude': geo_data.get('latitude'),
                'longitude': geo_data.get('longitude'),
                'accuracy': geo_data.get('accuracy'),
                'ip_address': geo_data.get('ip_address'),
                'country': geo_data.get('country'),
                'region': geo_data.get('region'),
                'city': geo_data.get('city')
            }
            
            self.db.insert('geo_data', data)
            return data_id
            
        except Exception as e:
            logger.error(f"Error storing geo data for session {session_id}: {e}")
            raise
    
    def get_geo_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get geographic location data for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Geographic location data or None if not found
        """
        try:
            return self.db.fetch_one(
                "SELECT * FROM geo_data WHERE session_id = ? ORDER BY timestamp DESC LIMIT 1",
                (session_id,)
            )
            
        except Exception as e:
            logger.error(f"Error getting geo data for session {session_id}: {e}")
            raise
    
    def get_user_locations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get locations used by a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of locations to return
            
        Returns:
            List of geographic location data
        """
        try:
            return self.db.fetch_all(
                """
                SELECT * FROM geo_data 
                WHERE user_id = ? 
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
            
        except Exception as e:
            logger.error(f"Error getting locations for user {user_id}: {e}")
            raise
    
    def store_behavior_profile(self, user_id: str, profile_type: str, profile_data: Union[Dict[str, Any], np.ndarray, bytes]) -> str:
        """Store a behavior profile.
        
        Args:
            user_id: User ID
            profile_type: Profile type (e.g., 'keystroke', 'mouse', 'device', 'geo')
            profile_data: Profile data (will be serialized)
            
        Returns:
            Profile ID
        """
        try:
            # Check if profile already exists
            existing = self.db.fetch_one(
                "SELECT id, version FROM behavior_profiles WHERE user_id = ? AND profile_type = ?",
                (user_id, profile_type)
            )
            
            now = int(time.time())
            
            # Serialize profile data
            if isinstance(profile_data, np.ndarray):
                serialized_data = profile_data.tobytes()
            elif isinstance(profile_data, dict):
                serialized_data = json.dumps(profile_data).encode('utf-8')
            elif isinstance(profile_data, bytes):
                serialized_data = profile_data
            else:
                serialized_data = str(profile_data).encode('utf-8')
            
            if existing:
                # Update existing profile
                profile_id = existing['id']
                version = existing['version'] + 1
                
                self.db.update(
                    'behavior_profiles',
                    {
                        'profile_data': serialized_data,
                        'updated_at': now,
                        'version': version
                    },
                    "id = ?",
                    (profile_id,)
                )
                
                logger.info(f"Updated {profile_type} profile for user {user_id} to version {version}")
                
            else:
                # Create new profile
                profile_id = str(uuid.uuid4())
                
                self.db.insert(
                    'behavior_profiles',
                    {
                        'id': profile_id,
                        'user_id': user_id,
                        'profile_type': profile_type,
                        'profile_data': serialized_data,
                        'created_at': now,
                        'updated_at': now,
                        'version': 1
                    }
                )
                
                logger.info(f"Created new {profile_type} profile for user {user_id}")
            
            return profile_id
            
        except Exception as e:
            logger.error(f"Error storing {profile_type} profile for user {user_id}: {e}")
            raise
    
    def get_behavior_profile(self, user_id: str, profile_type: str) -> Optional[Dict[str, Any]]:
        """Get a behavior profile.
        
        Args:
            user_id: User ID
            profile_type: Profile type (e.g., 'keystroke', 'mouse', 'device', 'geo')
            
        Returns:
            Profile data or None if not found
        """
        try:
            profile = self.db.fetch_one(
                "SELECT * FROM behavior_profiles WHERE user_id = ? AND profile_type = ?",
                (user_id, profile_type)
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting {profile_type} profile for user {user_id}: {e}")
            raise
    
    def get_behavior_profile_data(self, user_id: str, profile_type: str, as_dict: bool = False) -> Optional[Union[bytes, Dict[str, Any]]]:
        """Get behavior profile data.
        
        Args:
            user_id: User ID
            profile_type: Profile type (e.g., 'keystroke', 'mouse', 'device', 'geo')
            as_dict: Whether to deserialize JSON data as dictionary
            
        Returns:
            Profile data or None if not found
        """
        try:
            profile = self.db.fetch_one(
                "SELECT profile_data FROM behavior_profiles WHERE user_id = ? AND profile_type = ?",
                (user_id, profile_type)
            )
            
            if not profile:
                return None
            
            profile_data = profile['profile_data']
            
            # Try to deserialize as JSON if requested
            if as_dict:
                try:
                    return json.loads(profile_data)
                except:
                    pass
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting {profile_type} profile data for user {user_id}: {e}")
            raise
    
    def delete_behavior_profile(self, user_id: str, profile_type: str) -> bool:
        """Delete a behavior profile.
        
        Args:
            user_id: User ID
            profile_type: Profile type (e.g., 'keystroke', 'mouse', 'device', 'geo')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rows_affected = self.db.delete(
                'behavior_profiles',
                "user_id = ? AND profile_type = ?",
                (user_id, profile_type)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting {profile_type} profile for user {user_id}: {e}")
            raise
    
    def delete_user_data(self, user_id: str) -> Dict[str, int]:
        """Delete all behavioral data for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with counts of deleted records by type
        """
        try:
            # Start transaction
            self.db.begin_transaction()
            
            # Delete data from each table
            keystroke_count = self.db.delete('keystroke_data', "user_id = ?", (user_id,))
            mouse_count = self.db.delete('mouse_data', "user_id = ?", (user_id,))
            device_count = self.db.delete('device_data', "user_id = ?", (user_id,))
            geo_count = self.db.delete('geo_data', "user_id = ?", (user_id,))
            profile_count = self.db.delete('behavior_profiles', "user_id = ?", (user_id,))
            session_count = self.db.delete('behavior_sessions', "user_id = ?", (user_id,))
            
            # Commit transaction
            self.db.commit()
            
            logger.info(f"Deleted all behavioral data for user {user_id}")
            
            return {
                'keystroke_data': keystroke_count,
                'mouse_data': mouse_count,
                'device_data': device_count,
                'geo_data': geo_count,
                'behavior_profiles': profile_count,
                'behavior_sessions': session_count
            }
            
        except Exception as e:
            # Rollback transaction
            self.db.rollback()
            logger.error(f"Error deleting behavioral data for user {user_id}: {e}")
            raise