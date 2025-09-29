# Biometric Authentication System Usage Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Reference](#api-reference)
5. [Behavioral Monitoring](#behavioral-monitoring)
6. [Anomaly Detection](#anomaly-detection)
7. [Troubleshooting](#troubleshooting)

## System Overview

This system combines traditional biometric authentication with continuous behavioral monitoring to provide enhanced security. Even after successful biometric authentication, the system monitors user behavior patterns to detect anomalies and potential security threats.

### Key Components

- **Biometric Authentication**: Handles facial recognition, fingerprint scanning, and voice recognition
- **Behavioral Monitoring**: Tracks keystroke dynamics, mouse movements, device information, and geolocation
- **Anomaly Detection**: Uses machine learning models to detect unusual behavior patterns
- **Security Layer**: Manages JWT tokens and encryption for secure communication

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB 6.0+
- Docker and Docker Compose (optional)

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/biometric-auth.git
   cd biometric-auth
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the services:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/biometric-auth.git
   cd biometric-auth
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the backend:
   ```bash
   python app.py
   ```

6. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/biometric_auth` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | (required) |
| `JWT_ALGORITHM` | Algorithm for JWT tokens | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration time | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration time | `7` |
| `ENCRYPTION_KEY` | Key for data encryption | (required) |
| `ENCRYPTION_SALT` | Salt for data encryption | (required) |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Biometric Authentication Configuration

The biometric authentication system can be configured in the `.env` file:

```
# Biometric Authentication
FACE_AUTH_ENABLED=true
FINGERPRINT_AUTH_ENABLED=true
VOICE_AUTH_ENABLED=false
LIVENESS_DETECTION_ENABLED=true
FACE_RECOGNITION_THRESHOLD=0.6
```

### Behavioral Monitoring Configuration

The behavioral monitoring system can be configured in the `.env` file:

```
# Behavioral Monitoring
BEHAVIORAL_MONITORING_ENABLED=true
KEYSTROKE_THRESHOLD=0.7
MOUSE_THRESHOLD=0.7
DEVICE_THRESHOLD=0.8
GEO_THRESHOLD=0.8
```

## API Reference

### Authentication Endpoints

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login with username and password
- `POST /api/auth/refresh`: Refresh access token
- `POST /api/auth/logout`: Logout user

### Biometric Endpoints

- `POST /api/auth/biometric/register`: Register biometric data
- `POST /api/auth/biometric/verify`: Verify biometric data
- `GET /api/auth/biometric/status`: Get biometric registration status

### Behavioral Endpoints

- `POST /api/behavior/session/start`: Start a behavioral monitoring session
- `POST /api/behavior/session/end`: End a behavioral monitoring session
- `POST /api/behavior/keystroke/record`: Record keystroke data
- `POST /api/behavior/mouse/record`: Record mouse data
- `POST /api/behavior/device/record`: Record device data
- `POST /api/behavior/location/record`: Record location data
- `GET /api/behavior/analyze`: Analyze current behavior

### Anomaly Endpoints

- `GET /api/anomaly/status`: Get anomaly detection status
- `GET /api/anomaly/alerts`: Get anomaly alerts
- `POST /api/anomaly/train`: Train anomaly detection models

## Behavioral Monitoring

The behavioral monitoring system collects and analyzes the following data:

### Keystroke Dynamics

- Key press duration
- Key press latency
- Key press pressure (if available)
- Typing rhythm patterns

### Mouse Movements

- Movement speed
- Movement direction
- Click patterns
- Scroll behavior

### Device Information

- Browser and OS details
- Screen resolution
- Hardware information
- Network configuration

### Geolocation

- IP address
- Geographic location
- Time zone
- Connection type

## Anomaly Detection

The anomaly detection system uses the following machine learning models:

### Isolation Forest

Isolation Forest is used for detecting anomalies in non-sequential data like device information and geolocation.

### One-Class SVM

One-Class SVM is used for detecting anomalies in feature-rich data like keystroke dynamics.

### LSTM Autoencoder

LSTM Autoencoder is used for detecting anomalies in sequential data like mouse movements and keystroke sequences.

## Troubleshooting

### Common Issues

1. **Biometric registration fails**
   - Ensure proper lighting for facial recognition
   - Clean the fingerprint sensor
   - Check microphone permissions for voice recognition

2. **High false positive rate in anomaly detection**
   - Adjust the anomaly thresholds in the configuration
   - Retrain the models with more user data
   - Check for environmental factors affecting behavior

3. **Database connection issues**
   - Verify MongoDB is running
   - Check the connection string in the `.env` file
   - Ensure network connectivity to the database server

### Logs

Logs are stored in the `logs` directory and can be useful for troubleshooting:

- `app.log`: Main application log
- `auth.log`: Authentication-related logs
- `behavior.log`: Behavioral monitoring logs
- `anomaly.log`: Anomaly detection logs

### Support

For additional support, please contact the system administrator or open an issue on the GitHub repository.