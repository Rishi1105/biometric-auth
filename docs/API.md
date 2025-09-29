# Biometric Authentication System API Reference

## Base URL

All API endpoints are relative to the base URL: `http://localhost:8000`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Error Handling

All API errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message description",
    "details": {}
  }
}
```

## Endpoints

### Authentication

#### Register User

```
POST /api/auth/register
```

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "user_id": "user123",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "created_at": "2023-11-01T12:00:00Z"
}
```

#### Login

```
POST /api/auth/login
```

**Request Body:**

```json
{
  "username": "johndoe",
  "password": "SecurePassword123!"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "user123",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe"
  }
}
```

#### Refresh Token

```
POST /api/auth/refresh
```

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Logout

```
POST /api/auth/logout
```

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "message": "Successfully logged out"
}
```

### Biometric Authentication

#### Register Biometric Data

```
POST /api/auth/biometric/register
```

**Request Body:**

```json
{
  "biometric_type": "face",  // "face", "fingerprint", or "voice"
  "biometric_data": "base64_encoded_data"
}
```

**Response:**

```json
{
  "user_id": "user123",
  "biometric_type": "face",
  "registered": true,
  "message": "Biometric data registered successfully"
}
```

#### Verify Biometric Data

```
POST /api/auth/biometric/verify
```

**Request Body:**

```json
{
  "biometric_type": "face",  // "face", "fingerprint", or "voice"
  "biometric_data": "base64_encoded_data"
}
```

**Response:**

```json
{
  "verified": true,
  "user_id": "user123",
  "confidence": 0.95,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Biometric Status

```
GET /api/auth/biometric/status
```

**Response:**

```json
{
  "user_id": "user123",
  "registered_biometrics": {
    "face": true,
    "fingerprint": false,
    "voice": false
  },
  "last_updated": "2023-11-01T12:00:00Z"
}
```

### Behavioral Monitoring

#### Start Session

```
POST /api/behavior/session/start
```

**Response:**

```json
{
  "session_id": "session123",
  "user_id": "user123",
  "start_time": "2023-11-01T12:00:00Z",
  "message": "Behavioral monitoring session started"
}
```

#### End Session

```
POST /api/behavior/session/end
```

**Response:**

```json
{
  "session_id": "session123",
  "user_id": "user123",
  "start_time": "2023-11-01T12:00:00Z",
  "end_time": "2023-11-01T13:00:00Z",
  "duration": 3600,
  "average_similarity": 0.85,
  "anomaly_count": 2,
  "critical_count": 0
}
```

#### Record Keystroke Data

```
POST /api/behavior/keystroke/record
```

**Request Body:**

```json
{
  "key": "a",
  "event_type": "keydown",  // "keydown" or "keyup"
  "timestamp": 1635763200000,
  "pressure": 0.8,  // Optional
  "duration": 120  // Optional, in milliseconds
}
```

**Response:**

```json
{
  "recorded": true,
  "timestamp": 1635763200000
}
```

#### Record Mouse Data

```
POST /api/behavior/mouse/record
```

**Request Body:**

```json
{
  "event_type": "move",  // "move", "click", or "scroll"
  "x": 100,
  "y": 200,
  "timestamp": 1635763200000,
  "button": "left",  // Optional: "left", "right", or "middle"
  "scroll_delta": 5  // Optional, for scroll events
}
```

**Response:**

```json
{
  "recorded": true,
  "timestamp": 1635763200000
}
```

#### Record Device Data

```
POST /api/behavior/device/record
```

**Request Body:**

```json
{
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
  "screen_resolution": "1920x1080",
  "color_depth": 24,
  "timezone": "America/New_York",
  "language": "en-US",
  "platform": "Windows",
  "device_memory": 8,  // In GB
  "hardware_concurrency": 8  // CPU cores
}
```

**Response:**

```json
{
  "recorded": true,
  "timestamp": 1635763200000
}
```

#### Record Location Data

```
POST /api/behavior/location/record
```

**Request Body:**

```json
{
  "ip_address": "192.168.1.1",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 10,  // In meters
  "timestamp": 1635763200000
}
```

**Response:**

```json
{
  "recorded": true,
  "timestamp": 1635763200000
}
```

#### Analyze Behavior

```
GET /api/behavior/analyze
```

**Response:**

```json
{
  "user_id": "user123",
  "session_id": "session123",
  "timestamp": "2023-11-01T12:30:00Z",
  "similarity_score": 0.85,
  "anomalies": [
    {
      "component": "keystroke",
      "score": 0.65,
      "details": "Unusual typing rhythm detected"
    },
    {
      "component": "geo",
      "score": 0.45,
      "details": "Unusual location detected"
    }
  ],
  "alert_level": "warning"
}
```

### Anomaly Detection

#### Get Anomaly Status

```
GET /api/anomaly/status
```

**Response:**

```json
{
  "user_id": "user123",
  "models_trained": true,
  "last_training": "2023-10-15T08:00:00Z",
  "data_points": 1500,
  "components": {
    "keystroke": {
      "model": "isolation_forest",
      "accuracy": 0.92,
      "last_updated": "2023-10-15T08:00:00Z"
    },
    "mouse": {
      "model": "lstm",
      "accuracy": 0.88,
      "last_updated": "2023-10-15T08:00:00Z"
    },
    "device": {
      "model": "one_class_svm",
      "accuracy": 0.95,
      "last_updated": "2023-10-15T08:00:00Z"
    },
    "geo": {
      "model": "isolation_forest",
      "accuracy": 0.90,
      "last_updated": "2023-10-15T08:00:00Z"
    }
  }
}
```

#### Get Anomaly Alerts

```
GET /api/anomaly/alerts
```

**Query Parameters:**

- `start_date` (optional): Start date for alerts (ISO format)
- `end_date` (optional): End date for alerts (ISO format)
- `limit` (optional): Maximum number of alerts to return (default: 10)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**

```json
{
  "user_id": "user123",
  "total_alerts": 5,
  "alerts": [
    {
      "alert_id": "alert123",
      "timestamp": "2023-11-01T12:30:00Z",
      "level": "warning",
      "score": 0.65,
      "component_scores": {
        "keystroke": 0.65,
        "mouse": 0.85,
        "device": 0.95,
        "geo": 0.45
      },
      "details": "Unusual location and typing pattern detected"
    },
    {
      "alert_id": "alert124",
      "timestamp": "2023-11-01T14:45:00Z",
      "level": "critical",
      "score": 0.35,
      "component_scores": {
        "keystroke": 0.35,
        "mouse": 0.40,
        "device": 0.95,
        "geo": 0.25
      },
      "details": "Multiple behavioral anomalies detected"
    }
  ]
}
```

#### Train Anomaly Models

```
POST /api/anomaly/train
```

**Request Body:**

```json
{
  "components": ["keystroke", "mouse", "device", "geo"],  // Optional, defaults to all
  "force_retrain": false  // Optional, force retraining even with sufficient data
}
```

**Response:**

```json
{
  "user_id": "user123",
  "training_started": true,
  "components": ["keystroke", "mouse", "device", "geo"],
  "estimated_completion": "2023-11-01T13:00:00Z"
}
```

## Webhook Notifications

The system can send webhook notifications for important events. Configure webhooks in the admin panel.

### Anomaly Alert Webhook

**Payload:**

```json
{
  "event": "anomaly_alert",
  "timestamp": "2023-11-01T12:30:00Z",
  "user_id": "user123",
  "alert_id": "alert123",
  "level": "critical",
  "score": 0.35,
  "details": "Multiple behavioral anomalies detected"
}
```

### Authentication Failure Webhook

**Payload:**

```json
{
  "event": "auth_failure",
  "timestamp": "2023-11-01T12:30:00Z",
  "user_id": "user123",
  "auth_type": "biometric",
  "biometric_type": "face",
  "attempt_count": 3,
  "ip_address": "192.168.1.1"
}
```