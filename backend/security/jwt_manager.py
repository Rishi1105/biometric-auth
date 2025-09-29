import os
import logging
import datetime
from typing import Dict, Any, Optional, List, Union

from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

logger = logging.getLogger(__name__)

class JWTManager:
    """Manager for JWT token generation and validation."""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256',
                access_token_expire_minutes: int = 30, refresh_token_expire_days: int = 7):
        """Initialize the JWT manager.
        
        Args:
            secret_key: Secret key for JWT encoding/decoding (defaults to env var JWT_SECRET_KEY)
            algorithm: JWT algorithm to use
            access_token_expire_minutes: Access token expiration time in minutes
            refresh_token_expire_days: Refresh token expiration time in days
        """
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables or provided explicitly")
            
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        logger.info("JWT manager initialized")
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Create a new access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time (optional)
            
        Returns:
            JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "token_type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Create a new refresh token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time (optional)
            
        Returns:
            JWT refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "token_type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid
            ExpiredSignatureError: If token has expired
            JWTClaimsError: If token claims are invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except JWTClaimsError as e:
            logger.warning(f"Invalid token claims: {e}")
            raise
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            raise
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify an access token.
        
        Args:
            token: JWT access token to verify
            
        Returns:
            Decoded token payload if valid
            
        Raises:
            ValueError: If token is not an access token
            JWTError: If token is invalid
        """
        payload = self.decode_token(token)
        
        if payload.get("token_type") != "access":
            logger.warning("Token is not an access token")
            raise ValueError("Token is not an access token")
        
        return payload
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify a refresh token.
        
        Args:
            token: JWT refresh token to verify
            
        Returns:
            Decoded token payload if valid
            
        Raises:
            ValueError: If token is not a refresh token
            JWTError: If token is invalid
        """
        payload = self.decode_token(token)
        
        if payload.get("token_type") != "refresh":
            logger.warning("Token is not a refresh token")
            raise ValueError("Token is not a refresh token")
        
        return payload
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create a new access token from a refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            New JWT access token
            
        Raises:
            ValueError: If token is not a refresh token
            JWTError: If token is invalid
        """
        payload = self.verify_refresh_token(refresh_token)
        
        # Remove token-specific fields
        if "exp" in payload:
            del payload["exp"]
        if "token_type" in payload:
            del payload["token_type"]
        
        return self.create_access_token(payload)
    
    def get_token_expiration(self, token: str) -> datetime.datetime:
        """Get the expiration time of a token.
        
        Args:
            token: JWT token
            
        Returns:
            Expiration datetime
            
        Raises:
            JWTError: If token is invalid
            KeyError: If token does not have an expiration
        """
        payload = self.decode_token(token)
        
        if "exp" not in payload:
            raise KeyError("Token does not have an expiration")
        
        return datetime.datetime.fromtimestamp(payload["exp"])
    
    def get_token_remaining_time(self, token: str) -> datetime.timedelta:
        """Get the remaining time until a token expires.
        
        Args:
            token: JWT token
            
        Returns:
            Remaining time as timedelta
            
        Raises:
            JWTError: If token is invalid
            KeyError: If token does not have an expiration
        """
        expiration = self.get_token_expiration(token)
        remaining = expiration - datetime.datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else datetime.timedelta(0)
    
    def is_token_expired(self, token: str) -> bool:
        """Check if a token has expired.
        
        Args:
            token: JWT token
            
        Returns:
            True if token has expired, False otherwise
            
        Raises:
            JWTError: If token is invalid
            KeyError: If token does not have an expiration
        """
        try:
            remaining = self.get_token_remaining_time(token)
            return remaining.total_seconds() <= 0
        except ExpiredSignatureError:
            return True