# AI-Powered Biometric Authentication with Behavioral Anomaly Detection

## Project Overview
This system combines traditional biometric authentication (facial recognition, fingerprint, etc.) with continuous behavioral monitoring to provide enhanced security. Even after successful biometric authentication, the system monitors user behavior patterns to detect anomalies and potential security threats.

## Key Features

### 1. Biometric Authentication (Primary Login)
- Facial / fingerprint / iris / voice recognition
- Liveness detection to prevent spoofing

### 2. Behavioral AI Monitoring (Post-Login)
- Typing dynamics (keystroke duration, pressure)
- Mouse dynamics (movement pattern, speed)
- Device fingerprint (browser, OS, screen resolution)
- Geo-location & IP pattern tracking
- App or website interaction patterns

### 3. Anomaly Detection Engine
- Machine learning models:
  - Isolation Forest: Detects outliers by isolating observations
  - One-Class SVM: Identifies anomalies in an unsupervised framework
  - LSTM Autoencoder: Deep learning model for sequence-based anomaly detection
- Real-time session scoring and risk assessment
- Automated alerts and re-authentication triggers
- Continuous model retraining based on user behavior

## Use Case Example
1. User logs in with facial recognition — ✅ successful
2. After login, typing speed is 2x faster and IP is from another country — ❌ suspicious
3. System asks for re-authentication or logs out

## Technology Stack

| Area | Tools/Frameworks |
|------|------------------|
| Biometric Auth | OpenCV, TensorFlow, Dlib, FaceNet, Whisper |
| Behavioral Monitoring | JavaScript (for typing/mouse), Python (Pynput) |
| Anomaly Detection | Scikit-learn (Isolation Forest, One-Class SVM), PyOD |
| Frontend UI | React |
| Backend API | FastAPI |
| Database | MongoDB |
| Security Layer | JWT, AES Encryption |
| Deployment | Docker |

## System Architecture
```
[User Device]
      ↓
[Biometric Login System]
      ↓          ↘
[Access Control]  [Behavior Monitoring Script (JS/Python)]
      ↓                    ↓
[Main App]        [Behavioral AI Engine]
      ↓                    ↓
   [Secure Session Manager & Alert System]
      ↓
[Encrypted Database + Logs]
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB
- Docker (optional for deployment)

### Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/biometric-auth.git
cd biometric-auth
```

2. Install backend dependencies
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application
```bash
# Start backend
python app.py

# Start frontend (in another terminal)
cd frontend
npm start
```

### Demo Credentials
For testing purposes, you can use these pre-configured accounts:
- **Username:** `user1` **Password:** `password1`
- **Username:** `user2` **Password:** `password2`

### Modern UI Features
- **Glassmorphism design** with gradient backgrounds
- **Smooth animations** and transitions
- **Responsive layout** for all devices
- **Real-time biometric capture** with camera overlay
- **Interactive behavioral monitoring** visualization

## Project Structure
```
biometric-auth/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── auth/                # Biometric authentication modules
│   ├── behavioral/          # Behavioral monitoring modules
│   ├── anomaly/             # Anomaly detection algorithms
│   ├── database/            # Database models and connections
│   ├── security/            # Security utilities
│   └── utils/               # Helper functions
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/      # React components
│       ├── pages/           # Application pages
│       ├── services/        # API services
│       └── utils/           # Utility functions
├── models/                  # Pre-trained ML models
├── tests/                   # Unit and integration tests
├── docker/                  # Docker configuration
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## License
MIT

## Acknowledgements
- CMU Keystroke Dataset
- Balabit Mouse Dynamics Dataset
- LFW, FVC2004, CASIA, VoxCeleb Datasets