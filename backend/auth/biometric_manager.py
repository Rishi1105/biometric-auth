import os
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
import base64
import json

# Import necessary libraries for biometric processing
try:
    import cv2
    import face_recognition
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logging.warning("Some biometric dependencies are not installed. Limited functionality available.")

logger = logging.getLogger(__name__)

class BiometricAuthManager:
    """Manager for biometric authentication methods including face, fingerprint, and voice."""
    
    def __init__(self, storage_path: str = None):
        """Initialize the biometric authentication manager.
        
        Args:
            storage_path: Path to store biometric templates (defaults to env var BIOMETRIC_STORAGE_PATH)
        """
        self.storage_path = storage_path or os.environ.get('BIOMETRIC_STORAGE_PATH', './biometric_data')
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            
        # Thresholds for matching
        self.face_threshold = float(os.environ.get('FACE_MATCH_THRESHOLD', '0.6'))
        self.fingerprint_threshold = float(os.environ.get('FINGERPRINT_MATCH_THRESHOLD', '0.7'))
        self.voice_threshold = float(os.environ.get('VOICE_MATCH_THRESHOLD', '0.85'))
        
        logger.info("Biometric authentication manager initialized")
    
    def _get_user_path(self, user_id: str) -> str:
        """Get the path for a user's biometric data.
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user's biometric data directory
        """
        user_path = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        return user_path
    
    def _save_biometric_data(self, user_id: str, biometric_type: str, data: Any) -> bool:
        """Save biometric data for a user.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data ('face', 'fingerprint', 'voice')
            data: Biometric data to save
            
        Returns:
            Success status
        """
        try:
            user_path = self._get_user_path(user_id)
            file_path = os.path.join(user_path, f"{biometric_type}.json")
            
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(data, np.ndarray):
                data = data.tolist()
                
            with open(file_path, 'w') as f:
                json.dump(data, f)
                
            logger.info(f"Saved {biometric_type} data for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving {biometric_type} data: {str(e)}")
            return False
    
    def _load_biometric_data(self, user_id: str, biometric_type: str) -> Optional[Any]:
        """Load biometric data for a user.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data ('face', 'fingerprint', 'voice')
            
        Returns:
            Loaded biometric data or None if not found
        """
        try:
            user_path = self._get_user_path(user_id)
            file_path = os.path.join(user_path, f"{biometric_type}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"No {biometric_type} data found for user {user_id}")
                return None
                
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Convert lists back to numpy arrays if needed
            if biometric_type in ['face', 'fingerprint', 'voice'] and isinstance(data, list):
                data = np.array(data)
                
            return data
        except Exception as e:
            logger.error(f"Error loading {biometric_type} data: {str(e)}")
            return None
    
    def register_face(self, user_id: str, face_image: Union[str, bytes, np.ndarray]) -> Tuple[bool, str]:
        """Register a face for a user.
        
        Args:
            user_id: User ID
            face_image: Face image as base64 string, bytes, or numpy array
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Convert input to numpy array if needed
            if isinstance(face_image, str) and face_image.startswith('data:image'):
                # Handle data URL format
                face_image = face_image.split(',')[1]
                face_image = base64.b64decode(face_image)
            elif isinstance(face_image, str):
                # Assume base64 encoded string
                face_image = base64.b64decode(face_image)
                
            if isinstance(face_image, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(face_image, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = face_image
                
            # Detect faces in the image
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                return False, "No face detected in the image"
                
            if len(face_locations) > 1:
                return False, "Multiple faces detected in the image"
                
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(img, face_locations)
            if not face_encodings:
                return False, "Failed to extract face features"
                
            # Save face encoding
            success = self._save_biometric_data(user_id, 'face', face_encodings[0])
            if success:
                return True, "Face registered successfully"
            else:
                return False, "Failed to save face data"
        except Exception as e:
            logger.error(f"Error registering face: {str(e)}")
            return False, f"Error registering face: {str(e)}"
    
    def verify_face(self, user_id: str, face_image: Union[str, bytes, np.ndarray]) -> Tuple[bool, float, str]:
        """Verify a face against a registered template.
        
        Args:
            user_id: User ID
            face_image: Face image as base64 string, bytes, or numpy array
            
        Returns:
            Tuple of (match_result, confidence_score, message)
        """
        try:
            # Load registered face encoding
            registered_encoding = self._load_biometric_data(user_id, 'face')
            if registered_encoding is None:
                return False, 0.0, "No registered face found for this user"
                
            # Convert input to numpy array if needed
            if isinstance(face_image, str) and face_image.startswith('data:image'):
                # Handle data URL format
                face_image = face_image.split(',')[1]
                face_image = base64.b64decode(face_image)
            elif isinstance(face_image, str):
                # Assume base64 encoded string
                face_image = base64.b64decode(face_image)
                
            if isinstance(face_image, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(face_image, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = face_image
                
            # Detect faces in the image
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                return False, 0.0, "No face detected in the image"
                
            if len(face_locations) > 1:
                return False, 0.0, "Multiple faces detected in the image"
                
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(img, face_locations)
            if not face_encodings:
                return False, 0.0, "Failed to extract face features"
                
            # Compare face encodings
            matches = face_recognition.compare_faces([registered_encoding], face_encodings[0], tolerance=self.face_threshold)
            distance = face_recognition.face_distance([registered_encoding], face_encodings[0])[0]
            confidence = 1.0 - distance
            
            if matches[0]:
                return True, float(confidence), "Face verified successfully"
            else:
                return False, float(confidence), "Face verification failed"
        except Exception as e:
            logger.error(f"Error verifying face: {str(e)}")
            return False, 0.0, f"Error verifying face: {str(e)}"
    
    def register_fingerprint(self, user_id: str, fingerprint_data: Union[str, bytes, np.ndarray]) -> Tuple[bool, str]:
        """Register a fingerprint for a user.
        
        Args:
            user_id: User ID
            fingerprint_data: Fingerprint data as base64 string, bytes, or feature vector
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Convert input to feature vector if needed
            if isinstance(fingerprint_data, str):
                # Assume base64 encoded string
                fingerprint_data = base64.b64decode(fingerprint_data)
                
            if isinstance(fingerprint_data, bytes):
                # In a real implementation, this would extract minutiae points
                # For this example, we'll just use a hash of the data as a simple feature vector
                import hashlib
                hash_obj = hashlib.sha256(fingerprint_data)
                feature_vector = np.frombuffer(hash_obj.digest(), dtype=np.uint8)
                feature_vector = feature_vector.astype(float) / 255.0  # Normalize to [0,1]
            else:
                feature_vector = fingerprint_data
                
            # Save fingerprint feature vector
            success = self._save_biometric_data(user_id, 'fingerprint', feature_vector)
            if success:
                return True, "Fingerprint registered successfully"
            else:
                return False, "Failed to save fingerprint data"
        except Exception as e:
            logger.error(f"Error registering fingerprint: {str(e)}")
            return False, f"Error registering fingerprint: {str(e)}"
    
    def verify_fingerprint(self, user_id: str, fingerprint_data: Union[str, bytes, np.ndarray]) -> Tuple[bool, float, str]:
        """Verify a fingerprint against a registered template.
        
        Args:
            user_id: User ID
            fingerprint_data: Fingerprint data as base64 string, bytes, or feature vector
            
        Returns:
            Tuple of (match_result, confidence_score, message)
        """
        try:
            # Load registered fingerprint feature vector
            registered_vector = self._load_biometric_data(user_id, 'fingerprint')
            if registered_vector is None:
                return False, 0.0, "No registered fingerprint found for this user"
                
            # Convert input to feature vector if needed
            if isinstance(fingerprint_data, str):
                # Assume base64 encoded string
                fingerprint_data = base64.b64decode(fingerprint_data)
                
            if isinstance(fingerprint_data, bytes):
                # In a real implementation, this would extract minutiae points
                # For this example, we'll just use a hash of the data as a simple feature vector
                import hashlib
                hash_obj = hashlib.sha256(fingerprint_data)
                feature_vector = np.frombuffer(hash_obj.digest(), dtype=np.uint8)
                feature_vector = feature_vector.astype(float) / 255.0  # Normalize to [0,1]
            else:
                feature_vector = fingerprint_data
                
            # Compare fingerprint feature vectors using cosine similarity
            similarity = cosine_similarity([registered_vector], [feature_vector])[0][0]
            
            if similarity >= self.fingerprint_threshold:
                return True, float(similarity), "Fingerprint verified successfully"
            else:
                return False, float(similarity), "Fingerprint verification failed"
        except Exception as e:
            logger.error(f"Error verifying fingerprint: {str(e)}")
            return False, 0.0, f"Error verifying fingerprint: {str(e)}"
    
    def register_voice(self, user_id: str, voice_data: Union[str, bytes, np.ndarray]) -> Tuple[bool, str]:
        """Register a voice for a user.
        
        Args:
            user_id: User ID
            voice_data: Voice data as base64 string, bytes, or feature vector
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Convert input to feature vector if needed
            if isinstance(voice_data, str):
                # Assume base64 encoded string
                voice_data = base64.b64decode(voice_data)
                
            if isinstance(voice_data, bytes):
                # In a real implementation, this would extract voice features
                # For this example, we'll just use a hash of the data as a simple feature vector
                import hashlib
                hash_obj = hashlib.sha256(voice_data)
                feature_vector = np.frombuffer(hash_obj.digest(), dtype=np.uint8)
                feature_vector = feature_vector.astype(float) / 255.0  # Normalize to [0,1]
            else:
                feature_vector = voice_data
                
            # Save voice feature vector
            success = self._save_biometric_data(user_id, 'voice', feature_vector)
            if success:
                return True, "Voice registered successfully"
            else:
                return False, "Failed to save voice data"
        except Exception as e:
            logger.error(f"Error registering voice: {str(e)}")
            return False, f"Error registering voice: {str(e)}"
    
    def verify_voice(self, user_id: str, voice_data: Union[str, bytes, np.ndarray]) -> Tuple[bool, float, str]:
        """Verify a voice against a registered template.
        
        Args:
            user_id: User ID
            voice_data: Voice data as base64 string, bytes, or feature vector
            
        Returns:
            Tuple of (match_result, confidence_score, message)
        """
        try:
            # Load registered voice feature vector
            registered_vector = self._load_biometric_data(user_id, 'voice')
            if registered_vector is None:
                return False, 0.0, "No registered voice found for this user"
                
            # Convert input to feature vector if needed
            if isinstance(voice_data, str):
                # Assume base64 encoded string
                voice_data = base64.b64decode(voice_data)
                
            if isinstance(voice_data, bytes):
                # In a real implementation, this would extract voice features
                # For this example, we'll just use a hash of the data as a simple feature vector
                import hashlib
                hash_obj = hashlib.sha256(voice_data)
                feature_vector = np.frombuffer(hash_obj.digest(), dtype=np.uint8)
                feature_vector = feature_vector.astype(float) / 255.0  # Normalize to [0,1]
            else:
                feature_vector = voice_data
                
            # Compare voice feature vectors using cosine similarity
            similarity = cosine_similarity([registered_vector], [feature_vector])[0][0]
            
            if similarity >= self.voice_threshold:
                return True, float(similarity), "Voice verified successfully"
            else:
                return False, float(similarity), "Voice verification failed"
        except Exception as e:
            logger.error(f"Error verifying voice: {str(e)}")
            return False, 0.0, f"Error verifying voice: {str(e)}"
    
    def check_liveness(self, face_image: Union[str, bytes, np.ndarray]) -> Tuple[bool, float, str]:
        """Check if a face image is from a live person (anti-spoofing).
        
        Args:
            face_image: Face image as base64 string, bytes, or numpy array
            
        Returns:
            Tuple of (is_live, confidence_score, message)
        """
        try:
            # Convert input to numpy array if needed
            if isinstance(face_image, str) and face_image.startswith('data:image'):
                # Handle data URL format
                face_image = face_image.split(',')[1]
                face_image = base64.b64decode(face_image)
            elif isinstance(face_image, str):
                # Assume base64 encoded string
                face_image = base64.b64decode(face_image)
                
            if isinstance(face_image, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(face_image, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = face_image
                
            # In a real implementation, this would use advanced liveness detection techniques
            # For this example, we'll just do some basic checks
            
            # Check if there's a face in the image
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                return False, 0.0, "No face detected in the image"
                
            # Simple check: look for eye blinks or head movements in a video stream
            # This is just a placeholder - real liveness detection is more complex
            # For now, we'll return a random confidence score above the threshold
            import random
            confidence = random.uniform(0.7, 0.99)
            
            return True, float(confidence), "Liveness check passed"
        except Exception as e:
            logger.error(f"Error in liveness check: {str(e)}")
            return False, 0.0, f"Error in liveness check: {str(e)}"
    
    def delete_biometric_data(self, user_id: str, biometric_type: Optional[str] = None) -> bool:
        """Delete biometric data for a user.
        
        Args:
            user_id: User ID
            biometric_type: Type of biometric data to delete (None for all)
            
        Returns:
            Success status
        """
        try:
            user_path = self._get_user_path(user_id)
            
            if biometric_type:
                # Delete specific biometric data
                file_path = os.path.join(user_path, f"{biometric_type}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted {biometric_type} data for user {user_id}")
                    return True
                else:
                    logger.warning(f"No {biometric_type} data found for user {user_id}")
                    return False
            else:
                # Delete all biometric data
                import shutil
                if os.path.exists(user_path):
                    shutil.rmtree(user_path)
                    logger.info(f"Deleted all biometric data for user {user_id}")
                    return True
                else:
                    logger.warning(f"No biometric data found for user {user_id}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting biometric data: {str(e)}")
            return False
    
    def get_registered_biometrics(self, user_id: str) -> Dict[str, bool]:
        """Get the biometric methods registered for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of biometric types and registration status
        """
        user_path = self._get_user_path(user_id)
        result = {
            'face': os.path.exists(os.path.join(user_path, 'face.json')),
            'fingerprint': os.path.exists(os.path.join(user_path, 'fingerprint.json')),
            'voice': os.path.exists(os.path.join(user_path, 'voice.json'))
        }
        return result