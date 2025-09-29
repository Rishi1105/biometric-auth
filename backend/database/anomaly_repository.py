import os
import logging
import json
import time
import uuid
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union

from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class AnomalyRepository:
    """Repository for anomaly detection data storage and retrieval."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the anomaly repository.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        
        # Initialize database tables
        self._init_tables()
        
        logger.info("Anomaly repository initialized")
    
    def _init_tables(self) -> None:
        """Initialize database tables for anomaly detection data."""
        # Anomaly detection results table
        self.db.create_table(
            'anomaly_results',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT,
            detector_type TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            score REAL NOT NULL,
            threshold REAL NOT NULL,
            is_anomaly BOOLEAN NOT NULL,
            confidence REAL,
            features_used TEXT,
            explanation TEXT,
            raw_data TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES behavior_sessions(id) ON DELETE CASCADE
            """
        )
        
        # Anomaly thresholds table
        self.db.create_table(
            'anomaly_thresholds',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            detector_type TEXT NOT NULL,
            threshold REAL NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Anomaly models table
        self.db.create_table(
            'anomaly_models',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            model_type TEXT NOT NULL,
            model_data BLOB NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            version INTEGER DEFAULT 1,
            metrics TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """
        )
        
        # Anomaly alerts table
        self.db.create_table(
            'anomaly_alerts',
            """
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            result_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'new',
            resolved_at INTEGER,
            resolved_by TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (result_id) REFERENCES anomaly_results(id) ON DELETE CASCADE
            """
        )
        
        # Create indexes
        self.db.create_index('anomaly_results', ['user_id'])
        self.db.create_index('anomaly_results', ['session_id'])
        self.db.create_index('anomaly_results', ['timestamp'])
        self.db.create_index('anomaly_results', ['is_anomaly'])
        self.db.create_index('anomaly_thresholds', ['user_id', 'detector_type'], unique=True)
        self.db.create_index('anomaly_models', ['user_id', 'model_type'], unique=True)
        self.db.create_index('anomaly_alerts', ['user_id'])
        self.db.create_index('anomaly_alerts', ['status'])
        self.db.create_index('anomaly_alerts', ['timestamp'])
        
        logger.info("Anomaly tables initialized")
    
    def store_anomaly_result(self, user_id: str, detector_type: str, score: float, threshold: float, 
                            is_anomaly: bool, session_id: Optional[str] = None, 
                            confidence: Optional[float] = None, features_used: Optional[List[str]] = None, 
                            explanation: Optional[str] = None, raw_data: Optional[Dict[str, Any]] = None) -> str:
        """Store an anomaly detection result.
        
        Args:
            user_id: User ID
            detector_type: Type of anomaly detector (e.g., 'isolation_forest', 'one_class_svm', 'lstm')
            score: Anomaly score
            threshold: Threshold used for anomaly detection
            is_anomaly: Whether the score exceeds the threshold (is an anomaly)
            session_id: Session ID (optional)
            confidence: Confidence level of the anomaly detection (optional)
            features_used: List of features used for anomaly detection (optional)
            explanation: Explanation of the anomaly detection result (optional)
            raw_data: Raw data used for anomaly detection (optional)
            
        Returns:
            Result ID
        """
        try:
            result_id = str(uuid.uuid4())
            now = int(time.time())
            
            # Prepare data
            data = {
                'id': result_id,
                'user_id': user_id,
                'session_id': session_id,
                'detector_type': detector_type,
                'timestamp': now,
                'score': score,
                'threshold': threshold,
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'features_used': json.dumps(features_used) if features_used else None,
                'explanation': explanation,
                'raw_data': json.dumps(raw_data) if raw_data else None
            }
            
            self.db.insert('anomaly_results', data)
            
            # If it's an anomaly, create an alert
            if is_anomaly:
                self.create_anomaly_alert(user_id, result_id, detector_type, score, threshold)
            
            logger.info(f"Stored anomaly result for user {user_id} with detector {detector_type}, is_anomaly={is_anomaly}")
            return result_id
            
        except Exception as e:
            logger.error(f"Error storing anomaly result for user {user_id}: {e}")
            raise
    
    def get_anomaly_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get an anomaly detection result by ID.
        
        Args:
            result_id: Result ID
            
        Returns:
            Anomaly detection result or None if not found
        """
        try:
            result = self.db.fetch_one(
                "SELECT * FROM anomaly_results WHERE id = ?",
                (result_id,)
            )
            
            if result:
                # Parse JSON fields
                if result.get('features_used'):
                    result['features_used'] = json.loads(result['features_used'])
                if result.get('raw_data'):
                    result['raw_data'] = json.loads(result['raw_data'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting anomaly result {result_id}: {e}")
            raise
    
    def get_user_anomaly_results(self, user_id: str, limit: int = 100, 
                                only_anomalies: bool = False) -> List[Dict[str, Any]]:
        """Get anomaly detection results for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results to return
            only_anomalies: Whether to return only anomalies
            
        Returns:
            List of anomaly detection results
        """
        try:
            query = "SELECT * FROM anomaly_results WHERE user_id = ?"
            params = [user_id]
            
            if only_anomalies:
                query += " AND is_anomaly = TRUE"
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.fetch_all(query, tuple(params))
            
            # Parse JSON fields
            for result in results:
                if result.get('features_used'):
                    result['features_used'] = json.loads(result['features_used'])
                if result.get('raw_data'):
                    result['raw_data'] = json.loads(result['raw_data'])
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting anomaly results for user {user_id}: {e}")
            raise
    
    def get_session_anomaly_results(self, session_id: str) -> List[Dict[str, Any]]:
        """Get anomaly detection results for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of anomaly detection results
        """
        try:
            results = self.db.fetch_all(
                "SELECT * FROM anomaly_results WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            
            # Parse JSON fields
            for result in results:
                if result.get('features_used'):
                    result['features_used'] = json.loads(result['features_used'])
                if result.get('raw_data'):
                    result['raw_data'] = json.loads(result['raw_data'])
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting anomaly results for session {session_id}: {e}")
            raise
    
    def set_anomaly_threshold(self, user_id: str, detector_type: str, threshold: float) -> str:
        """Set an anomaly detection threshold for a user.
        
        Args:
            user_id: User ID
            detector_type: Type of anomaly detector
            threshold: Threshold value
            
        Returns:
            Threshold ID
        """
        try:
            # Check if threshold already exists
            existing = self.db.fetch_one(
                "SELECT id FROM anomaly_thresholds WHERE user_id = ? AND detector_type = ?",
                (user_id, detector_type)
            )
            
            now = int(time.time())
            
            if existing:
                # Update existing threshold
                threshold_id = existing['id']
                
                self.db.update(
                    'anomaly_thresholds',
                    {
                        'threshold': threshold,
                        'updated_at': now
                    },
                    "id = ?",
                    (threshold_id,)
                )
                
                logger.info(f"Updated {detector_type} threshold for user {user_id} to {threshold}")
                
            else:
                # Create new threshold
                threshold_id = str(uuid.uuid4())
                
                self.db.insert(
                    'anomaly_thresholds',
                    {
                        'id': threshold_id,
                        'user_id': user_id,
                        'detector_type': detector_type,
                        'threshold': threshold,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                
                logger.info(f"Created new {detector_type} threshold for user {user_id}: {threshold}")
            
            return threshold_id
            
        except Exception as e:
            logger.error(f"Error setting {detector_type} threshold for user {user_id}: {e}")
            raise
    
    def get_anomaly_threshold(self, user_id: str, detector_type: str) -> Optional[float]:
        """Get an anomaly detection threshold for a user.
        
        Args:
            user_id: User ID
            detector_type: Type of anomaly detector
            
        Returns:
            Threshold value or None if not found
        """
        try:
            threshold = self.db.fetch_one(
                "SELECT threshold FROM anomaly_thresholds WHERE user_id = ? AND detector_type = ?",
                (user_id, detector_type)
            )
            
            return threshold['threshold'] if threshold else None
            
        except Exception as e:
            logger.error(f"Error getting {detector_type} threshold for user {user_id}: {e}")
            raise
    
    def store_anomaly_model(self, user_id: str, model_type: str, model_data: Union[bytes, np.ndarray], 
                           metrics: Optional[Dict[str, Any]] = None) -> str:
        """Store an anomaly detection model.
        
        Args:
            user_id: User ID
            model_type: Type of anomaly model (e.g., 'isolation_forest', 'one_class_svm', 'lstm')
            model_data: Serialized model data
            metrics: Model performance metrics (optional)
            
        Returns:
            Model ID
        """
        try:
            # Check if model already exists
            existing = self.db.fetch_one(
                "SELECT id, version FROM anomaly_models WHERE user_id = ? AND model_type = ?",
                (user_id, model_type)
            )
            
            now = int(time.time())
            
            # Ensure model_data is bytes
            if isinstance(model_data, np.ndarray):
                model_data = model_data.tobytes()
            
            if existing:
                # Update existing model
                model_id = existing['id']
                version = existing['version'] + 1
                
                self.db.update(
                    'anomaly_models',
                    {
                        'model_data': model_data,
                        'updated_at': now,
                        'version': version,
                        'metrics': json.dumps(metrics) if metrics else None
                    },
                    "id = ?",
                    (model_id,)
                )
                
                logger.info(f"Updated {model_type} model for user {user_id} to version {version}")
                
            else:
                # Create new model
                model_id = str(uuid.uuid4())
                
                self.db.insert(
                    'anomaly_models',
                    {
                        'id': model_id,
                        'user_id': user_id,
                        'model_type': model_type,
                        'model_data': model_data,
                        'created_at': now,
                        'updated_at': now,
                        'version': 1,
                        'metrics': json.dumps(metrics) if metrics else None
                    }
                )
                
                logger.info(f"Created new {model_type} model for user {user_id}")
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error storing {model_type} model for user {user_id}: {e}")
            raise
    
    def get_anomaly_model(self, user_id: str, model_type: str) -> Optional[Dict[str, Any]]:
        """Get an anomaly detection model.
        
        Args:
            user_id: User ID
            model_type: Type of anomaly model
            
        Returns:
            Model data or None if not found
        """
        try:
            model = self.db.fetch_one(
                "SELECT * FROM anomaly_models WHERE user_id = ? AND model_type = ?",
                (user_id, model_type)
            )
            
            if model and model.get('metrics'):
                model['metrics'] = json.loads(model['metrics'])
            
            return model
            
        except Exception as e:
            logger.error(f"Error getting {model_type} model for user {user_id}: {e}")
            raise
    
    def get_anomaly_model_data(self, user_id: str, model_type: str) -> Optional[bytes]:
        """Get anomaly detection model data.
        
        Args:
            user_id: User ID
            model_type: Type of anomaly model
            
        Returns:
            Model data as bytes or None if not found
        """
        try:
            model = self.db.fetch_one(
                "SELECT model_data FROM anomaly_models WHERE user_id = ? AND model_type = ?",
                (user_id, model_type)
            )
            
            return model['model_data'] if model else None
            
        except Exception as e:
            logger.error(f"Error getting {model_type} model data for user {user_id}: {e}")
            raise
    
    def delete_anomaly_model(self, user_id: str, model_type: str) -> bool:
        """Delete an anomaly detection model.
        
        Args:
            user_id: User ID
            model_type: Type of anomaly model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rows_affected = self.db.delete(
                'anomaly_models',
                "user_id = ? AND model_type = ?",
                (user_id, model_type)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting {model_type} model for user {user_id}: {e}")
            raise
    
    def create_anomaly_alert(self, user_id: str, result_id: str, alert_type: str, 
                            score: float, threshold: float) -> str:
        """Create an anomaly alert.
        
        Args:
            user_id: User ID
            result_id: Anomaly result ID
            alert_type: Type of alert (e.g., 'keystroke', 'mouse', 'device', 'geo')
            score: Anomaly score
            threshold: Threshold value
            
        Returns:
            Alert ID
        """
        try:
            alert_id = str(uuid.uuid4())
            now = int(time.time())
            
            # Determine severity based on how much the score exceeds the threshold
            if threshold == 0:
                severity = 'high'  # Avoid division by zero
            else:
                ratio = score / threshold
                if ratio > 2.0:
                    severity = 'high'
                elif ratio > 1.5:
                    severity = 'medium'
                else:
                    severity = 'low'
            
            description = f"Anomaly detected with {alert_type} detector. Score: {score:.4f}, Threshold: {threshold:.4f}"
            
            self.db.insert(
                'anomaly_alerts',
                {
                    'id': alert_id,
                    'user_id': user_id,
                    'result_id': result_id,
                    'alert_type': alert_type,
                    'severity': severity,
                    'timestamp': now,
                    'description': description,
                    'status': 'new'
                }
            )
            
            logger.info(f"Created {severity} anomaly alert for user {user_id} with {alert_type} detector")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating anomaly alert for user {user_id}: {e}")
            raise
    
    def get_anomaly_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get an anomaly alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert data or None if not found
        """
        try:
            return self.db.fetch_one(
                "SELECT * FROM anomaly_alerts WHERE id = ?",
                (alert_id,)
            )
            
        except Exception as e:
            logger.error(f"Error getting anomaly alert {alert_id}: {e}")
            raise
    
    def get_user_anomaly_alerts(self, user_id: str, status: Optional[str] = None, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get anomaly alerts for a user.
        
        Args:
            user_id: User ID
            status: Alert status filter (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert data
        """
        try:
            query = "SELECT * FROM anomaly_alerts WHERE user_id = ?"
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            return self.db.fetch_all(query, tuple(params))
            
        except Exception as e:
            logger.error(f"Error getting anomaly alerts for user {user_id}: {e}")
            raise
    
    def update_alert_status(self, alert_id: str, status: str, 
                           resolved_by: Optional[str] = None, 
                           resolution_notes: Optional[str] = None) -> bool:
        """Update the status of an anomaly alert.
        
        Args:
            alert_id: Alert ID
            status: New status ('new', 'investigating', 'resolved', 'false_positive')
            resolved_by: User ID of resolver (required if status is 'resolved' or 'false_positive')
            resolution_notes: Notes on resolution (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {'status': status}
            
            if status in ['resolved', 'false_positive']:
                if not resolved_by:
                    raise ValueError("resolved_by is required for resolved or false_positive status")
                
                data['resolved_at'] = int(time.time())
                data['resolved_by'] = resolved_by
                data['resolution_notes'] = resolution_notes
            
            rows_affected = self.db.update(
                'anomaly_alerts',
                data,
                "id = ?",
                (alert_id,)
            )
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error updating status for anomaly alert {alert_id}: {e}")
            raise
    
    def get_anomaly_statistics(self, user_id: Optional[str] = None, 
                             days: int = 30) -> Dict[str, Any]:
        """Get anomaly detection statistics.
        
        Args:
            user_id: User ID (optional, if None, get statistics for all users)
            days: Number of days to include in statistics
            
        Returns:
            Dictionary of statistics
        """
        try:
            now = int(time.time())
            start_time = now - (days * 24 * 60 * 60)
            
            # Base query parts
            where_clause = "timestamp >= ?"
            params = [start_time]
            
            if user_id:
                where_clause += " AND user_id = ?"
                params.append(user_id)
            
            # Total results
            total_results = self.db.fetch_one(
                f"SELECT COUNT(*) as count FROM anomaly_results WHERE {where_clause}",
                tuple(params)
            )['count']
            
            # Total anomalies
            total_anomalies = self.db.fetch_one(
                f"SELECT COUNT(*) as count FROM anomaly_results WHERE {where_clause} AND is_anomaly = TRUE",
                tuple(params)
            )['count']
            
            # Results by detector type
            results_by_detector = self.db.fetch_all(
                f"SELECT detector_type, COUNT(*) as count FROM anomaly_results WHERE {where_clause} GROUP BY detector_type",
                tuple(params)
            )
            
            # Anomalies by detector type
            anomalies_by_detector = self.db.fetch_all(
                f"SELECT detector_type, COUNT(*) as count FROM anomaly_results WHERE {where_clause} AND is_anomaly = TRUE GROUP BY detector_type",
                tuple(params)
            )
            
            # Alerts by severity
            alerts_by_severity = self.db.fetch_all(
                f"SELECT severity, COUNT(*) as count FROM anomaly_alerts WHERE {where_clause} GROUP BY severity",
                tuple(params)
            )
            
            # Alerts by status
            alerts_by_status = self.db.fetch_all(
                f"SELECT status, COUNT(*) as count FROM anomaly_alerts WHERE {where_clause} GROUP BY status",
                tuple(params)
            )
            
            # Format results
            detector_results = {item['detector_type']: item['count'] for item in results_by_detector}
            detector_anomalies = {item['detector_type']: item['count'] for item in anomalies_by_detector}
            severity_counts = {item['severity']: item['count'] for item in alerts_by_severity}
            status_counts = {item['status']: item['count'] for item in alerts_by_status}
            
            return {
                'total_results': total_results,
                'total_anomalies': total_anomalies,
                'anomaly_rate': (total_anomalies / total_results) if total_results > 0 else 0,
                'results_by_detector': detector_results,
                'anomalies_by_detector': detector_anomalies,
                'alerts_by_severity': severity_counts,
                'alerts_by_status': status_counts,
                'time_period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting anomaly statistics: {e}")
            raise
    
    def delete_user_anomaly_data(self, user_id: str) -> Dict[str, int]:
        """Delete all anomaly data for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with counts of deleted records by type
        """
        try:
            # Start transaction
            self.db.begin_transaction()
            
            # Delete data from each table
            alerts_count = self.db.delete('anomaly_alerts', "user_id = ?", (user_id,))
            results_count = self.db.delete('anomaly_results', "user_id = ?", (user_id,))
            thresholds_count = self.db.delete('anomaly_thresholds', "user_id = ?", (user_id,))
            models_count = self.db.delete('anomaly_models', "user_id = ?", (user_id,))
            
            # Commit transaction
            self.db.commit()
            
            logger.info(f"Deleted all anomaly data for user {user_id}")
            
            return {
                'anomaly_alerts': alerts_count,
                'anomaly_results': results_count,
                'anomaly_thresholds': thresholds_count,
                'anomaly_models': models_count
            }
            
        except Exception as e:
            # Rollback transaction
            self.db.rollback()
            logger.error(f"Error deleting anomaly data for user {user_id}: {e}")
            raise