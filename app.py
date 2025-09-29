import os
import time
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.middleware.proxy_fix import ProxyFix
from backend.behavioral.behavior_manager import behavior_manager

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Record start time for uptime tracking
    app.start_time = time.time()
    
    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_EXPIRATION_MINUTES', '60')) * 60
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.environ.get('JWT_REFRESH_EXPIRATION_DAYS', '30')) * 86400
    
    # Configure CORS - use CORS() without parameters to enable for all routes
    CORS(app)
    
    # Configure proxy fix for proper IP handling behind reverse proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Setup API routes
    setup_routes(app)
    
    logger.info("Application initialized")
    
    return app

def setup_routes(app):
    """Set up API routes for the Flask application."""
    
    # Mock user database
    users = {
        "user1": {"password": "password1", "biometric_data": "mock_face_data_1", "email": "user1@example.com", "full_name": "User One"},
        "user2": {"password": "password2", "biometric_data": "mock_face_data_2", "email": "user2@example.com", "full_name": "User Two"}
    }
    
    # Global OPTIONS handler for CORS preflight requests
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        full_name = data.get('full_name')
        
        # Check if username already exists
        if username in users:
            return jsonify({"status": "error", "message": "Username already exists"}), 400
        
        # Add new user to mock database
        users[username] = {
            "password": password,
            "email": email,
            "full_name": full_name,
            "biometric_data": None  # Will be added during biometric setup
        }
        
        # Create access token
        access_token = create_access_token(identity=username)
        
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "userId": username,
            "token": access_token
        }), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username not in users or users[username]['password'] != password:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(identity=username)
        
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "userId": username,
            "token": access_token,
            "requiresBiometric": True
        })
    
    @app.route('/api/auth/verify-biometric', methods=['POST'])
    @jwt_required()
    def verify_biometric():
        # In a real app, this would verify biometric data
        # For demo purposes, we'll just return success
        
        return jsonify({
            "status": "success",
            "message": "Biometric verification successful",
            "token": create_access_token(identity=get_jwt_identity())
        })
    
    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        username = get_jwt_identity()
        
        # In a real app, this would fetch user data from a database
        return jsonify({
            "status": "success",
            "data": {
                "username": username,
                "email": f"{username}@example.com",
                "lastLogin": "2023-09-14T12:00:00Z",
                "securityScore": 85
            }
        })
    
    @app.route('/api/behavior/security-score', methods=['GET'])
    @jwt_required()
    def get_security_score():
        username = get_jwt_identity()
        
        try:
            # Get security score using behavior manager
            security_score = behavior_manager.get_security_score(username)
            logger.info(f"Retrieved security score for user {username}")
            
            return jsonify({
                "status": "success",
                "data": security_score
            })
        except Exception as e:
            logger.error(f"Error getting security score for user {username}: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to get security score"
            }), 500
    
    @app.route('/api/anomaly/status', methods=['GET'])
    @jwt_required()
    def get_anomaly_status():
        # In a real app, this would check for anomalies
        return jsonify({
            "status": "success",
            "data": {
                "anomalyDetected": False,
                "securityScore": 85,
                "lastCheck": "2023-09-14T12:00:00Z",
                "riskLevel": "low"
            }
        })
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        uptime = time.time() - app.start_time
        return jsonify({
            "status": "success",
            "uptime": uptime,
            "version": "1.0.0"
        })
    
    # Behavioral monitoring endpoints
    @app.route('/api/behavior/keystroke', methods=['POST'])
    @jwt_required()
    def keystroke_data():
        data = request.get_json()
        userId = data.get('userId')
        keystroke_events = data.get('data', [])
        
        try:
            # Process keystroke data using behavior manager
            result = behavior_manager.process_keystroke_data(userId, keystroke_events)
            logger.info(f"Processed {len(keystroke_events)} keystroke events for user {userId}")
            
            return jsonify({
                "status": "success",
                "message": "Keystroke data processed",
                "anomaly_score": result.get('anomaly_score', 0.0),
                "anomalies_detected": result.get('anomalies_detected', [])
            })
        except Exception as e:
            logger.error(f"Error processing keystroke data for user {userId}: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to process keystroke data"
            }), 500
    
    @app.route('/api/behavior/mouse', methods=['POST'])
    @jwt_required()
    def mouse_data():
        data = request.get_json()
        userId = data.get('userId')
        mouse_events = data.get('data', [])
        
        try:
            # Process mouse data using behavior manager
            result = behavior_manager.process_mouse_data(userId, mouse_events)
            logger.info(f"Processed {len(mouse_events)} mouse events for user {userId}")
            
            return jsonify({
                "status": "success",
                "message": "Mouse data processed",
                "anomaly_score": result.get('anomaly_score', 0.0),
                "anomalies_detected": result.get('anomalies_detected', [])
            })
        except Exception as e:
            logger.error(f"Error processing mouse data for user {userId}: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to process mouse data"
            }), 500
    
    @app.route('/api/behavior/device', methods=['POST'])
    @jwt_required()
    def device_data():
        data = request.get_json()
        userId = data.get('userId')
        device_info = data.get('data', {})
        
        try:
            # Process device data using behavior manager
            result = behavior_manager.process_device_data(userId, device_info)
            logger.info(f"Processed device data for user {userId}")
            
            return jsonify({
                "status": "success",
                "message": "Device data processed",
                "device_match": result.get('device_match', True),
                "anomalies_detected": result.get('anomalies_detected', [])
            })
        except Exception as e:
            logger.error(f"Error processing device data for user {userId}: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to process device data"
            }), 500

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting application on {host}:{port} (debug={debug})")
    
    app.run(host=host, port=port, debug=debug)