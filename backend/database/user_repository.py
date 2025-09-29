import os
import logging
import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for user data storage and retrieval."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the user repository.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
        # Initialize database tables
        self._init_tables()
        
        logger.info("User repository initialized")
    
    def _init_tables(self) -> None:
        """Initialize database tables for user data."""
        # Users table
        self.db.create_table(
            'users',
            """
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            role TEXT DEFAULT 'user',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            last_login INTEGER,
            login_attempts INTEGER DEFAULT 0,
            locked_until INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1
            """
        )
        
        # User biometric data table
        self.db.create_table(
            'user_biometrics',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            biometric_type TEXT NOT NULL,
            biometric_data BLOB NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # User sessions table
        self.db.create_table(
            'user_sessions',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL,
            device_info TEXT,
            ip_address TEXT,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            revoked BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Create indexes
        self.db.create_index('users', ['username'], unique=True)
        self.db.create_index('users', ['email'], unique=True)
        self.db.create_index('user_biometrics', ['user_id', 'biometric_type'])
        self.db.create_index('user_sessions', ['user_id'])
        self.db.create_index('user_sessions', ['token'], unique=True)
        
        logger.info("User tables initialized")
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            User ID
        """
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Generate salt and hash password
        salt = os.urandom(32).hex()
        password_hash = self._hash_password(user_data['password'], salt)
        
        # Prepare user data
        now = int(time.time())
        user = {
            'id': user_id,
            'username': user_data['username'],
            'email': user_data['email'],
            'password_hash': password_hash,
            'salt': salt,
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'role': user_data.get('role', 'user'),
            'created_at': now,
            'updated_at': now
        }
        
        # Insert user
        try:
            self.db.insert('users', user)
            logger.info(f"User {user_id} created")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        try:
            user = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
            
            if user:
                # Remove sensitive data
                user.pop('password_hash', None)
                user.pop('salt', None)
            
            return user
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User data or None if not found
        """
        try:
            return self.db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User data or None if not found
        """
        try:
            return self.db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user data.
        
        Args:
            user_id: User ID
            user_data: User data to update
            
        Returns:
            True if successful, False otherwise
        """
        # Don't allow updating sensitive fields directly
        user_data.pop('id', None)
        user_data.pop('password_hash', None)
        user_data.pop('salt', None)
        user_data.pop('created_at', None)
        
        # Update timestamp
        user_data['updated_at'] = int(time.time())
        
        try:
            rows_affected = self.db.update('users', user_data, "id = ?", (user_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rows_affected = self.db.delete('users', "id = ?", (user_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    def verify_password(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user password.
        
        Args:
            username: Username
            password: Password to verify
            
        Returns:
            User data if password is correct, None otherwise
        """
        try:
            user = self.db.fetch_one(
                "SELECT * FROM users WHERE username = ? AND active = 1 AND (locked_until IS NULL OR locked_until < ?)",
                (username, int(time.time()))
            )
            
            if not user:
                return None
            
            # Verify password
            password_hash = self._hash_password(password, user['salt'])
            
            if password_hash == user['password_hash']:
                # Reset login attempts on successful login
                self.db.update(
                    'users',
                    {
                        'login_attempts': 0,
                        'last_login': int(time.time())
                    },
                    "id = ?",
                    (user['id'],)
                )
                
                # Remove sensitive data
                user.pop('password_hash', None)
                user.pop('salt', None)
                
                return user
            else:
                # Increment login attempts
                self._increment_login_attempts(user['id'], user['login_attempts'])
                return None
            
        except Exception as e:
            logger.error(f"Error verifying password for {username}: {e}")
            raise
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
            
            if not user:
                return False
            
            # Verify current password
            current_hash = self._hash_password(current_password, user['salt'])
            
            if current_hash != user['password_hash']:
                return False
            
            # Generate new salt and hash
            new_salt = os.urandom(32).hex()
            new_hash = self._hash_password(new_password, new_salt)
            
            # Update password
            rows_affected = self.db.update(
                'users',
                {
                    'password_hash': new_hash,
                    'salt': new_salt,
                    'updated_at': int(time.time())
                },
                "id = ?",
                (user_id,)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            raise
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password (admin function).
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
            
            if not user:
                return False
            
            # Generate new salt and hash
            new_salt = os.urandom(32).hex()
            new_hash = self._hash_password(new_password, new_salt)
            
            # Update password
            rows_affected = self.db.update(
                'users',
                {
                    'password_hash': new_hash,
                    'salt': new_salt,
                    'login_attempts': 0,
                    'locked_until': 0,
                    'updated_at': int(time.time())
                },
                "id = ?",
                (user_id,)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error resetting password for user {user_id}: {e}")
            raise
    
    def store_biometric_data(self, user_id: str, biometric_type: str, biometric_data: bytes) -> str:
        """Store user biometric data.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data (face, fingerprint, voice)
            biometric_data: Binary biometric data
            
        Returns:
            Biometric data ID
        """
        try:
            # Check if biometric data already exists
            existing = self.db.fetch_one(
                "SELECT id FROM user_biometrics WHERE user_id = ? AND biometric_type = ?",
                (user_id, biometric_type)
            )
            
            now = int(time.time())
            
            if existing:
                # Update existing biometric data
                self.db.update(
                    'user_biometrics',
                    {
                        'biometric_data': biometric_data,
                        'updated_at': now
                    },
                    "id = ?",
                    (existing['id'],)
                )
                return existing['id']
            else:
                # Insert new biometric data
                biometric_id = str(uuid.uuid4())
                self.db.insert(
                    'user_biometrics',
                    {
                        'id': biometric_id,
                        'user_id': user_id,
                        'biometric_type': biometric_type,
                        'biometric_data': biometric_data,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                return biometric_id
                
        except Exception as e:
            logger.error(f"Error storing biometric data for user {user_id}: {e}")
            raise
    
    def get_biometric_data(self, user_id: str, biometric_type: str) -> Optional[bytes]:
        """Get user biometric data.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data (face, fingerprint, voice)
            
        Returns:
            Binary biometric data or None if not found
        """
        try:
            result = self.db.fetch_one(
                "SELECT biometric_data FROM user_biometrics WHERE user_id = ? AND biometric_type = ?",
                (user_id, biometric_type)
            )
            
            return result['biometric_data'] if result else None
            
        except Exception as e:
            logger.error(f"Error getting biometric data for user {user_id}: {e}")
            raise
    
    def delete_biometric_data(self, user_id: str, biometric_type: str) -> bool:
        """Delete user biometric data.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data (face, fingerprint, voice)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rows_affected = self.db.delete(
                'user_biometrics',
                "user_id = ? AND biometric_type = ?",
                (user_id, biometric_type)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting biometric data for user {user_id}: {e}")
            raise
    
    def create_session(self, user_id: str, token: str, device_info: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None, expires_in: int = 3600) -> str:
        """Create a new user session.
        
        Args:
            user_id: User ID
            token: Session token
            device_info: Device information (optional)
            ip_address: IP address (optional)
            expires_in: Session expiration time in seconds
            
        Returns:
            Session ID
        """
        try:
            session_id = str(uuid.uuid4())
            now = int(time.time())
            
            self.db.insert(
                'user_sessions',
                {
                    'id': session_id,
                    'user_id': user_id,
                    'token': token,
                    'device_info': json.dumps(device_info) if device_info else None,
                    'ip_address': ip_address,
                    'created_at': now,
                    'expires_at': now + expires_in
                }
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            raise
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session by token.
        
        Args:
            token: Session token
            
        Returns:
            Session data or None if not found or expired
        """
        try:
            now = int(time.time())
            
            session = self.db.fetch_one(
                "SELECT * FROM user_sessions WHERE token = ? AND expires_at > ? AND revoked = 0",
                (token, now)
            )
            
            if session and session.get('device_info'):
                session['device_info'] = json.loads(session['device_info'])
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session for token: {e}")
            raise
    
    def revoke_session(self, token: str) -> bool:
        """Revoke a session.
        
        Args:
            token: Session token
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rows_affected = self.db.update(
                'user_sessions',
                {'revoked': 1},
                "token = ?",
                (token,)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            raise
    
    def revoke_all_user_sessions(self, user_id: str, except_token: Optional[str] = None) -> int:
        """Revoke all sessions for a user.
        
        Args:
            user_id: User ID
            except_token: Token to exclude from revocation (optional)
            
        Returns:
            Number of sessions revoked
        """
        try:
            if except_token:
                rows_affected = self.db.update(
                    'user_sessions',
                    {'revoked': 1},
                    "user_id = ? AND token != ? AND revoked = 0",
                    (user_id, except_token)
                )
            else:
                rows_affected = self.db.update(
                    'user_sessions',
                    {'revoked': 1},
                    "user_id = ? AND revoked = 0",
                    (user_id,)
                )
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error revoking all sessions for user {user_id}: {e}")
            raise
    
    def clean_expired_sessions(self) -> int:
        """Clean expired sessions from the database.
        
        Returns:
            Number of sessions cleaned
        """
        try:
            now = int(time.time())
            
            rows_affected = self.db.delete(
                'user_sessions',
                "expires_at < ?",
                (now,)
            )
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Error cleaning expired sessions: {e}")
            raise
    
    def get_users(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated list of users.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of users per page
            
        Returns:
            Dictionary with users and total count
        """
        try:
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get users
            users = self.db.fetch_all(
                "SELECT id, username, email, first_name, last_name, role, created_at, updated_at, last_login, active FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (per_page, offset)
            )
            
            # Get total count
            total = self.db.fetch_one("SELECT COUNT(*) as count FROM users")
            
            return {
                'users': users,
                'total': total['count'] if total else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            raise
    
    def get_user_count(self) -> int:
        """Get total number of users.
        
        Returns:
            User count
        """
        try:
            result = self.db.fetch_one("SELECT COUNT(*) as count FROM users")
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            raise
    
    def get_active_user_count(self, days: int = 30) -> int:
        """Get number of active users in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Active user count
        """
        try:
            now = int(time.time())
            timestamp = now - (days * 86400)  # 86400 seconds in a day
            
            result = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM users WHERE last_login > ?",
                (timestamp,)
            )
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting active user count: {e}")
            raise
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with the given salt.
        
        Args:
            password: Password to hash
            salt: Salt for hashing
            
        Returns:
            Hashed password
        """
        # Use PBKDF2 with SHA-256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            bytes.fromhex(salt),
            100000  # 100,000 iterations
        )
        
        return key.hex()
    
    def _increment_login_attempts(self, user_id: str, current_attempts: int) -> None:
        """Increment login attempts and lock account if necessary.
        
        Args:
            user_id: User ID
            current_attempts: Current number of login attempts
        """
        # Get max login attempts from environment or use default
        max_attempts = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
        lockout_minutes = int(os.environ.get('LOCKOUT_MINUTES', '30'))
        
        new_attempts = current_attempts + 1
        update_data = {'login_attempts': new_attempts}
        
        # Lock account if max attempts reached
        if new_attempts >= max_attempts:
            now = int(time.time())
            locked_until = now + (lockout_minutes * 60)
            update_data['locked_until'] = locked_until
            logger.warning(f"User {user_id} locked until {datetime.fromtimestamp(locked_until)}")
        
        self.db.update('users', update_data, "id = ?", (user_id,))