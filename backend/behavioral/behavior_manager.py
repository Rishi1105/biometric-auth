import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
try:
    import numpy as np
except ImportError:
    np = None
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class BehaviorManager:
    """
    Manages behavioral monitoring and anomaly detection for continuous authentication.
    Tracks user behavior patterns and detects anomalies in real-time.
    """
    
    def __init__(self):
        self.user_profiles = {}  # Store user behavior profiles
        self.active_sessions = {}  # Track active monitoring sessions
        self.anomaly_models = {}  # ML models for each user
        self.scalers = {}  # Data scalers for normalization
        self.behavior_buffer = {}  # Buffer recent behavior events
        self.buffer_size = 50  # Number of events to keep in buffer
        
        # Initialize anomaly detection models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models for anomaly detection."""
        logger.info("Initializing anomaly detection models")
        
        # Default model parameters
        self.model_params = {
            'contamination': 0.1,  # Expected proportion of anomalies
            'n_estimators': 100,
            'max_samples': 'auto',
            'random_state': 42
        }
        
    def create_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new behavior profile for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing the created profile
        """
        profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'keystroke_patterns': {
                'avg_typing_speed': 0,
                'keystroke_intervals': [],
                'error_rate': 0,
                'common_sequences': []
            },
            'mouse_patterns': {
                'avg_movement_speed': 0,
                'click_patterns': [],
                'scroll_patterns': [],
                'movement_variance': 0
            },
            'device_patterns': {
                'screen_resolution': None,
                'browser_info': None,
                'os_info': None,
                'ip_address': None
            },
            'baseline_established': False,
            'anomaly_threshold': 0.15
        }
        
        self.user_profiles[user_id] = profile
        self.behavior_buffer[user_id] = []
        
        # Initialize ML model for this user if sklearn is available
        if SKLEARN_AVAILABLE:
            self.anomaly_models[user_id] = IsolationForest(**self.model_params)
            self.scalers[user_id] = StandardScaler()
        else:
            # Use a simple mock model if sklearn is not available
            self.anomaly_models[user_id] = None
            self.scalers[user_id] = None
        
        logger.info(f"Created behavior profile for user {user_id}")
        return profile
    
    def process_keystroke_data(self, user_id: str, keystroke_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process keystroke data and update user profile.
        
        Args:
            user_id: User identifier
            keystroke_events: List of keystroke events
            
        Returns:
            Processing results including anomaly scores
        """
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
            
        profile = self.user_profiles[user_id]
        results = {
            'user_id': user_id,
            'events_processed': len(keystroke_events),
            'anomaly_score': 0.0,
            'anomalies_detected': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract features from keystroke events
            features = self._extract_keystroke_features(keystroke_events)
            
            # Update profile with new data
            self._update_keystroke_profile(profile, features)
            
            # Add to behavior buffer
            for event in keystroke_events:
                event['type'] = 'keystroke'
                event['timestamp'] = datetime.now().isoformat()
                self.behavior_buffer[user_id].append(event)
                
            # Maintain buffer size
            if len(self.behavior_buffer[user_id]) > self.buffer_size:
                self.behavior_buffer[user_id] = self.behavior_buffer[user_id][-self.buffer_size:]
            
            # Perform anomaly detection if baseline is established
            if profile['baseline_established']:
                anomaly_score = self._detect_keystroke_anomalies(user_id, features)
                results['anomaly_score'] = anomaly_score
                
                if anomaly_score > profile['anomaly_threshold']:
                    results['anomalies_detected'].append({
                        'type': 'keystroke',
                        'score': anomaly_score,
                        'description': 'Unusual keystroke pattern detected'
                    })
            else:
                # Check if we have enough data to establish baseline
                if self._check_baseline_sufficient(profile):
                    profile['baseline_established'] = True
                    self._train_user_model(user_id)
                    logger.info(f"Baseline established for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error processing keystroke data for user {user_id}: {str(e)}")
            results['error'] = str(e)
            
        return results
    
    def process_mouse_data(self, user_id: str, mouse_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process mouse movement and click data.
        
        Args:
            user_id: User identifier
            mouse_events: List of mouse events
            
        Returns:
            Processing results including anomaly scores
        """
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
            
        profile = self.user_profiles[user_id]
        results = {
            'user_id': user_id,
            'events_processed': len(mouse_events),
            'anomaly_score': 0.0,
            'anomalies_detected': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract features from mouse events
            features = self._extract_mouse_features(mouse_events)
            
            # Update profile with new data
            self._update_mouse_profile(profile, features)
            
            # Add to behavior buffer
            for event in mouse_events:
                event['type'] = 'mouse'
                event['timestamp'] = datetime.now().isoformat()
                self.behavior_buffer[user_id].append(event)
                
            # Maintain buffer size
            if len(self.behavior_buffer[user_id]) > self.buffer_size:
                self.behavior_buffer[user_id] = self.behavior_buffer[user_id][-self.buffer_size:]
            
            # Perform anomaly detection if baseline is established
            if profile['baseline_established']:
                anomaly_score = self._detect_mouse_anomalies(user_id, features)
                results['anomaly_score'] = anomaly_score
                
                if anomaly_score > profile['anomaly_threshold']:
                    results['anomalies_detected'].append({
                        'type': 'mouse',
                        'score': anomaly_score,
                        'description': 'Unusual mouse movement pattern detected'
                    })
                    
        except Exception as e:
            logger.error(f"Error processing mouse data for user {user_id}: {str(e)}")
            results['error'] = str(e)
            
        return results
    
    def process_device_data(self, user_id: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process device fingerprinting data.
        
        Args:
            user_id: User identifier
            device_info: Device information dictionary
            
        Returns:
            Processing results
        """
        if user_id not in self.user_profiles:
            self.create_user_profile(user_id)
            
        profile = self.user_profiles[user_id]
        results = {
            'user_id': user_id,
            'device_match': True,
            'anomalies_detected': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check for device anomalies
            device_patterns = profile['device_patterns']
            
            # Check screen resolution
            if device_patterns['screen_resolution'] and \
               device_patterns['screen_resolution'] != device_info.get('screen_resolution'):
                results['anomalies_detected'].append({
                    'type': 'device',
                    'description': 'Screen resolution changed',
                    'severity': 'medium'
                })
                
            # Check browser info
            if device_patterns['browser_info'] and \
               device_patterns['browser_info'] != device_info.get('browser_info'):
                results['anomalies_detected'].append({
                    'type': 'device',
                    'description': 'Browser information changed',
                    'severity': 'low'
                })
                
            # Check IP address (significant security concern)
            if device_patterns['ip_address'] and \
               device_patterns['ip_address'] != device_info.get('ip_address'):
                results['anomalies_detected'].append({
                    'type': 'device',
                    'description': 'IP address changed - potential location change',
                    'severity': 'high'
                })
                
            # Update device patterns
            device_patterns.update(device_info)
            
        except Exception as e:
            logger.error(f"Error processing device data for user {user_id}: {str(e)}")
            results['error'] = str(e)
            
        return results
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user behavior profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary or None if not found
        """
        return self.user_profiles.get(user_id)
    
    def get_security_score(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate overall security score for a user based on behavior patterns.
        
        Args:
            user_id: User identifier
            
        Returns:
            Security assessment dictionary
        """
        if user_id not in self.user_profiles:
            return {
                'user_id': user_id,
                'security_score': 0,
                'risk_level': 'unknown',
                'anomalies_count': 0,
                'baseline_established': False
            }
            
        profile = self.user_profiles[user_id]
        
        # Calculate security score based on various factors
        score = 100
        risk_level = 'low'
        anomalies_count = 0
        
        # Check recent behavior for anomalies
        recent_events = self.behavior_buffer.get(user_id, [])
        if recent_events:
            # Analyze recent events for anomalies
            recent_anomalies = self._analyze_recent_behavior(user_id, recent_events)
            anomalies_count = len(recent_anomalies)
            
            # Reduce score based on anomalies
            score -= anomalies_count * 10
            
            # Determine risk level
            if anomalies_count == 0:
                risk_level = 'low'
            elif anomalies_count <= 2:
                risk_level = 'medium'
            else:
                risk_level = 'high'
                
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return {
            'user_id': user_id,
            'security_score': score,
            'risk_level': risk_level,
            'anomalies_count': anomalies_count,
            'baseline_established': profile['baseline_established'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_keystroke_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features from keystroke events."""
        if not events:
            return {}
            
        features = {
            'typing_speed': 0,
            'keystroke_intervals': [],
            'error_count': 0,
            'special_key_usage': 0
        }
        
        # Calculate typing speed and intervals
        keydown_times = []
        for event in events:
            if event.get('type') == 'keydown':
                keydown_times.append(event.get('timestamp', time.time()))
                
        if len(keydown_times) > 1:
            intervals = [keydown_times[i] - keydown_times[i-1] for i in range(1, len(keydown_times))]
            features['keystroke_intervals'] = intervals
            features['typing_speed'] = len(events) / (max(intervals) if intervals else 1)
            
        return features
    
    def _extract_mouse_features(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features from mouse events."""
        if not events:
            return {}
            
        features = {
            'movement_speed': 0,
            'click_count': 0,
            'scroll_count': 0,
            'movement_variance': 0
        }
        
        # Count events
        for event in events:
            if event.get('type') == 'click':
                features['click_count'] += 1
            elif event.get('type') == 'scroll':
                features['scroll_count'] += 1
                
        return features
    
    def _update_keystroke_profile(self, profile: Dict[str, Any], features: Dict[str, Any]):
        """Update keystroke patterns in user profile."""
        keystroke_patterns = profile['keystroke_patterns']
        
        if features.get('typing_speed'):
            # Update average typing speed
            current_avg = keystroke_patterns['avg_typing_speed']
            new_speed = features['typing_speed']
            keystroke_patterns['avg_typing_speed'] = (current_avg + new_speed) / 2 if current_avg else new_speed
            
        if features.get('keystroke_intervals'):
            keystroke_patterns['keystroke_intervals'].extend(features['keystroke_intervals'])
            # Keep only recent intervals
            if len(keystroke_patterns['keystroke_intervals']) > 1000:
                keystroke_patterns['keystroke_intervals'] = keystroke_patterns['keystroke_intervals'][-1000:]
    
    def _update_mouse_profile(self, profile: Dict[str, Any], features: Dict[str, Any]):
        """Update mouse patterns in user profile."""
        mouse_patterns = profile['mouse_patterns']
        
        if features.get('movement_speed'):
            current_avg = mouse_patterns['avg_movement_speed']
            new_speed = features['movement_speed']
            mouse_patterns['avg_movement_speed'] = (current_avg + new_speed) / 2 if current_avg else new_speed
            
        if features.get('click_count'):
            mouse_patterns['click_patterns'].append(features['click_count'])
            if len(mouse_patterns['click_patterns']) > 100:
                mouse_patterns['click_patterns'] = mouse_patterns['click_patterns'][-100:]
    
    def _detect_keystroke_anomalies(self, user_id: str, features: Dict[str, Any]) -> float:
        """Detect anomalies in keystroke patterns."""
        if not SKLEARN_AVAILABLE:
            # Return a mock anomaly score when sklearn is not available
            return 0.1  # Low anomaly score indicating normal behavior
            
        try:
            model = self.anomaly_models.get(user_id)
            scaler = self.scalers.get(user_id)
            
            if not model or not scaler:
                return 0.0
                
            # Convert features to numerical array
            feature_vector = [
                features.get('typing_speed', 0),
                len(features.get('keystroke_intervals', [])),
                features.get('error_count', 0),
                features.get('special_key_usage', 0)
            ]
            
            # Normalize features
            feature_vector_scaled = scaler.transform([feature_vector])
            
            # Predict anomaly (returns -1 for anomaly, 1 for normal)
            prediction = model.predict(feature_vector_scaled)
            
            # Convert to anomaly score (0 to 1)
            anomaly_score = 0.0 if prediction[0] == 1 else 1.0
            
            # Get decision function for more granular scoring
            decision_scores = model.decision_function(feature_vector_scaled)
            anomaly_score = max(0, min(1, (decision_scores[0] + 0.5) / 1.0))
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Error detecting keystroke anomalies for user {user_id}: {str(e)}")
            return 0.0
    
    def _detect_mouse_anomalies(self, user_id: str, features: Dict[str, Any]) -> float:
        """Detect anomalies in mouse patterns."""
        if not SKLEARN_AVAILABLE:
            # Return a mock anomaly score when sklearn is not available
            return 0.1  # Low anomaly score indicating normal behavior
            
        try:
            model = self.anomaly_models.get(user_id)
            scaler = self.scalers.get(user_id)
            
            if not model or not scaler:
                return 0.0
                
            # Convert features to numerical array
            feature_vector = [
                features.get('movement_speed', 0),
                features.get('click_count', 0),
                features.get('scroll_count', 0),
                features.get('movement_variance', 0)
            ]
            
            # Normalize features
            feature_vector_scaled = scaler.transform([feature_vector])
            
            # Predict anomaly
            prediction = model.predict(feature_vector_scaled)
            
            # Convert to anomaly score
            anomaly_score = 0.0 if prediction[0] == 1 else 1.0
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Error detecting mouse anomalies for user {user_id}: {str(e)}")
            return 0.0
    
    def _check_baseline_sufficient(self, profile: Dict[str, Any]) -> bool:
        """Check if we have enough data to establish baseline."""
        keystroke_patterns = profile['keystroke_patterns']
        mouse_patterns = profile['mouse_patterns']
        
        # Check if we have sufficient keystroke data
        sufficient_keystrokes = len(keystroke_patterns['keystroke_intervals']) >= 50
        
        # Check if we have sufficient mouse data
        sufficient_mouse = len(mouse_patterns['click_patterns']) >= 20
        
        return sufficient_keystrokes or sufficient_mouse
    
    def _train_user_model(self, user_id: str):
        """Train anomaly detection model for a specific user."""
        if not SKLEARN_AVAILABLE:
            logger.warning(f"Sklearn not available, skipping model training for user {user_id}")
            return
            
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return
                
            # Collect training data from user profile
            training_data = []
            
            # Add keystroke features
            keystroke_patterns = profile['keystroke_patterns']
            if keystroke_patterns['avg_typing_speed'] > 0:
                training_data.append([
                    keystroke_patterns['avg_typing_speed'],
                    len(keystroke_patterns['keystroke_intervals']),
                    keystroke_patterns['error_rate'],
                    0  # special key usage
                ])
            
            # Add mouse features
            mouse_patterns = profile['mouse_patterns']
            if mouse_patterns['avg_movement_speed'] > 0:
                mean_clicks = 0
                if mouse_patterns['click_patterns']:
                    if np is not None:
                        mean_clicks = np.mean(mouse_patterns['click_patterns'])
                    else:
                        mean_clicks = sum(mouse_patterns['click_patterns']) / len(mouse_patterns['click_patterns'])
                training_data.append([
                    mouse_patterns['avg_movement_speed'],
                    mean_clicks,
                    0,  # scroll count
                    mouse_patterns['movement_variance']
                ])
            
            if len(training_data) > 0 and np is not None:
                # Convert to numpy array
                training_array = np.array(training_data)
                
                # Fit scaler
                scaler = self.scalers[user_id]
                if scaler:
                    scaler.fit(training_array)
                
                # Fit model
                model = self.anomaly_models[user_id]
                if model:
                    model.fit(training_array)
                
                logger.info(f"Trained anomaly detection model for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error training model for user {user_id}: {str(e)}")
    
    def _analyze_recent_behavior(self, user_id: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze recent behavior for anomalies."""
        anomalies = []
        
        # Group events by type
        keystroke_events = [e for e in events if e.get('type') == 'keystroke']
        mouse_events = [e for e in events if e.get('type') == 'mouse']
        
        # Analyze keystroke events
        if keystroke_events:
            features = self._extract_keystroke_features(keystroke_events)
            anomaly_score = self._detect_keystroke_anomalies(user_id, features)
            if anomaly_score > 0.5:
                anomalies.append({
                    'type': 'keystroke',
                    'score': anomaly_score,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Analyze mouse events
        if mouse_events:
            features = self._extract_mouse_features(mouse_events)
            anomaly_score = self._detect_mouse_anomalies(user_id, features)
            if anomaly_score > 0.5:
                anomalies.append({
                    'type': 'mouse',
                    'score': anomaly_score,
                    'timestamp': datetime.now().isoformat()
                })
        
        return anomalies

# Global instance
behavior_manager = BehaviorManager()