import os
import base64
import logging
from typing import Dict, Any, Optional, Union, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manager for data encryption and decryption."""
    
    def __init__(self, key: Optional[str] = None, salt: Optional[bytes] = None):
        """Initialize the encryption manager.
        
        Args:
            key: Encryption key (defaults to env var ENCRYPTION_KEY)
            salt: Salt for key derivation (defaults to env var ENCRYPTION_SALT or random)
        """
        # Get key from environment if not provided
        self.key_str = key or os.environ.get('ENCRYPTION_KEY')
        if not self.key_str:
            # Generate a new key if not provided
            self.key = Fernet.generate_key()
            self.key_str = self.key.decode('utf-8')
            logger.warning("No encryption key provided, generated a new one. This should be saved and reused.")
        else:
            # Use the provided key
            self.key = self.key_str.encode('utf-8')
        
        # Get or generate salt
        salt_str = os.environ.get('ENCRYPTION_SALT')
        if salt:
            self.salt = salt
        elif salt_str:
            self.salt = base64.b64decode(salt_str)
        else:
            # Generate a random salt if not provided
            self.salt = os.urandom(16)
            logger.warning("No encryption salt provided, generated a new one. This should be saved and reused.")
        
        # Create the Fernet cipher
        self.cipher = Fernet(self.key)
        
        logger.info("Encryption manager initialized")
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive an encryption key from a password.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (optional, uses instance salt if not provided)
            
        Returns:
            Derived key
        """
        if not salt:
            salt = self.salt
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted data as bytes
            
        Raises:
            InvalidToken: If the data cannot be decrypted
        """
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_to_string(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return as base64 string.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data as base64 string
        """
        encrypted = self.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_from_string(self, encrypted_string: str) -> str:
        """Decrypt data from base64 string.
        
        Args:
            encrypted_string: Encrypted data as base64 string
            
        Returns:
            Decrypted data as string
            
        Raises:
            InvalidToken: If the data cannot be decrypted
        """
        encrypted_data = base64.b64decode(encrypted_string)
        decrypted = self.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt values in a dictionary.
        
        Args:
            data: Dictionary with values to encrypt
            
        Returns:
            Dictionary with encrypted values
        """
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, (str, bytes)):
                encrypted[key] = self.encrypt_to_string(value)
            elif isinstance(value, dict):
                encrypted[key] = self.encrypt_dict(value)
            else:
                encrypted[key] = value
                
        return encrypted
    
    def decrypt_dict(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt values in a dictionary.
        
        Args:
            encrypted_data: Dictionary with encrypted values
            
        Returns:
            Dictionary with decrypted values
            
        Raises:
            InvalidToken: If any value cannot be decrypted
        """
        decrypted = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str):
                try:
                    decrypted[key] = self.decrypt_from_string(value)
                except Exception:
                    # If decryption fails, assume it wasn't encrypted
                    decrypted[key] = value
            elif isinstance(value, dict):
                decrypted[key] = self.decrypt_dict(value)
            else:
                decrypted[key] = value
                
        return decrypted
    
    def get_key_as_string(self) -> str:
        """Get the encryption key as a string.
        
        Returns:
            Encryption key as string
        """
        return self.key_str
    
    def get_salt_as_string(self) -> str:
        """Get the salt as a base64 string.
        
        Returns:
            Salt as base64 string
        """
        return base64.b64encode(self.salt).decode('utf-8')
    
    @classmethod
    def generate_key_pair(cls) -> Tuple[str, str]:
        """Generate a new encryption key and salt.
        
        Returns:
            Tuple of (key, salt) as strings
        """
        key = Fernet.generate_key().decode('utf-8')
        salt = base64.b64encode(os.urandom(16)).decode('utf-8')
        return key, salt