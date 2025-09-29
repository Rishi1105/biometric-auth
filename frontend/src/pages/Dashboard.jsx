import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  AppBar, 
  Toolbar, 
  IconButton, 
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { 
  Logout, 
  Security, 
  Fingerprint, 
  Mouse, 
  Keyboard,
  DevicesOther,
  LocationOn,
  Warning,
  CheckCircle
} from '@mui/icons-material';
import { authService } from '../services/authService';
import { behaviorService } from '../services/behaviorService';
import '../styles/neumorphic.css';

const Dashboard = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [anomalyAlerts, setAnomalyAlerts] = useState([]);
  const [securityStatus, setSecurityStatus] = useState('secure'); // secure, warning, breach
  
  // Fetch user data on component mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // In a real app, this would fetch user data from the API
        // For demo purposes, we'll use mock data
        const mockUserData = {
          id: authService.getUserId(),
          username: 'demo_user',
          email: 'user@example.com',
          biometricMethods: ['face', 'fingerprint'],
          lastLogin: new Date().toISOString(),
          securityScore: 85
        };
        
        setUserData(mockUserData);
        setLoading(false);
        
        // Start behavioral monitoring
        startBehavioralMonitoring();
        
        // Set up anomaly detection simulation
        simulateAnomalyDetection();
      } catch (error) {
        console.error('Error fetching user data:', error);
        setError('Failed to load user data. Please try again.');
        setLoading(false);
      }
    };
    
    fetchUserData();
    
    // Cleanup function
    return () => {
      behaviorService.stopAllMonitoring();
    };
  }, []);
  
  // Start behavioral monitoring
  const startBehavioralMonitoring = () => {
    const token = authService.getToken();
    const userId = authService.getUserId();
    
    if (token && userId) {
      behaviorService.startKeystrokeMonitoring(userId, token);
      behaviorService.startMouseMonitoring(userId, token);
      behaviorService.startDeviceMonitoring(userId, token);
    }
  };
  
  // Simulate anomaly detection for demo purposes
  const simulateAnomalyDetection = () => {
    // Simulate receiving anomaly alerts
    const anomalyTypes = ['keystroke', 'mouse', 'device'];
    const confidenceLevels = [0.65, 0.78, 0.92];
    
    // Add initial anomaly after 10 seconds
    setTimeout(() => {
      const newAlert = {
        id: Date.now(),
        type: anomalyTypes[0],
        timestamp: new Date().toISOString(),
        confidence: confidenceLevels[0],
        details: 'Unusual keystroke pattern detected'
      };
      
      setAnomalyAlerts(prev => [...prev, newAlert]);
      setSecurityStatus('warning');
    }, 10000);
    
    // Add second anomaly after 20 seconds
    setTimeout(() => {
      const newAlert = {
        id: Date.now(),
        type: anomalyTypes[1],
        timestamp: new Date().toISOString(),
        confidence: confidenceLevels[1],
        details: 'Abnormal mouse movement pattern'
      };
      
      setAnomalyAlerts(prev => [...prev, newAlert]);
    }, 20000);
    
    // Add critical anomaly after 30 seconds
    setTimeout(() => {
      const newAlert = {
        id: Date.now(),
        type: anomalyTypes[2],
        timestamp: new Date().toISOString(),
        confidence: confidenceLevels[2],
        details: 'Suspicious device environment change'
      };
      
      setAnomalyAlerts(prev => [...prev, newAlert]);
      setSecurityStatus('breach');
    }, 30000);
  };
  
  // Handle logout
  const handleLogout = () => {
    behaviorService.stopAllMonitoring();
    authService.logout();
  };
  
  // Render security status indicator
  const renderSecurityStatus = () => {
    switch (securityStatus) {
      case 'secure':
        return (
          <Box display="flex" alignItems="center">
            <CheckCircle style={{ color: 'var(--success-color)' }} sx={{ mr: 1 }} />
            <Typography variant="body1" style={{ color: 'var(--success-color)' }}>
              Secure
            </Typography>
          </Box>
        );
      case 'warning':
        return (
          <Box display="flex" alignItems="center">
            <Warning style={{ color: 'var(--warning-color)' }} sx={{ mr: 1 }} />
            <Typography variant="body1" style={{ color: 'var(--warning-color)' }}>
              Anomaly Detected
            </Typography>
          </Box>
        );
      case 'breach':
        return (
          <Box display="flex" alignItems="center">
            <Warning style={{ color: 'var(--error-color)' }} sx={{ mr: 1 }} />
            <Typography variant="body1" style={{ color: 'var(--error-color)' }}>
              Security Breach
            </Typography>
          </Box>
        );
      default:
        return null;
    }
  };
  
  // Render anomaly alert icon based on type
  const renderAnomalyIcon = (type) => {
    switch (type) {
      case 'keystroke':
        return <Keyboard style={{ color: 'var(--error-color)' }} />;
      case 'mouse':
        return <Mouse style={{ color: 'var(--error-color)' }} />;
      case 'device':
        return <DevicesOther style={{ color: 'var(--error-color)' }} />;
      case 'geo':
        return <LocationOn style={{ color: 'var(--error-color)' }} />;
      default:
        return <Warning style={{ color: 'var(--error-color)' }} />;
    }
  };
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  return (
    <Box sx={{ flexGrow: 1 }}>
      <div className="neumorphic-appbar">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Biometric Auth Dashboard
          </Typography>
          {renderSecurityStatus()}
          <IconButton className="neumorphic-icon-button" onClick={handleLogout}>
            <Logout />
          </IconButton>
        </Toolbar>
      </div>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* User Profile */}
          <Grid item xs={12} md={4}>
            <div className="neumorphic-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                User Profile
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="body1">
                    <strong>{userData.username}</strong>
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {userData.email}
                  </Typography>
                </Box>
              </Box>
              <div className="neumorphic-divider" style={{ margin: '16px 0' }}></div>
              <Typography variant="subtitle2" gutterBottom>
                Biometric Methods
              </Typography>
              <List dense>
                {userData.biometricMethods.map((method, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {method === 'face' ? <Fingerprint /> : <Fingerprint />}
                    </ListItemIcon>
                    <ListItemText primary={method.charAt(0).toUpperCase() + method.slice(1)} />
                  </ListItem>
                ))}
              </List>
              <div className="neumorphic-divider" style={{ margin: '16px 0' }}></div>
              <Typography variant="body2">
                Last login: {new Date(userData.lastLogin).toLocaleString()}
              </Typography>
            </div>
          </Grid>
          
          {/* Security Score */}
          <Grid item xs={12} md={4}>
            <div className="neumorphic-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Security Score
              </Typography>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                flexGrow: 1
              }}>
                <Box position="relative" display="inline-flex">
                  <CircularProgress 
                    variant="determinate" 
                    value={userData.securityScore} 
                    size={120} 
                    thickness={5} 
                    color={userData.securityScore > 80 ? "success" : userData.securityScore > 60 ? "warning" : "error"}
                    className="neumorphic-progress"
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h4" component="div" color="text.secondary">
                      {userData.securityScore}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                  Your account security is {userData.securityScore > 80 ? "strong" : userData.securityScore > 60 ? "moderate" : "weak"}
                </Typography>
              </Box>
            </div>
          </Grid>
          
          {/* Behavioral Monitoring */}
          <Grid item xs={12} md={4}>
            <div className="neumorphic-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>
                Behavioral Monitoring
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Keyboard style={{ color: 'var(--primary-color)' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Keystroke Dynamics" 
                    secondary="Active monitoring" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Mouse style={{ color: 'var(--primary-color)' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Mouse Movements" 
                    secondary="Active monitoring" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DevicesOther style={{ color: 'var(--primary-color)' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Device Environment" 
                    secondary="Active monitoring" 
                  />
                </ListItem>
              </List>
              <div className="neumorphic-divider" style={{ margin: '16px 0' }}></div>
              <Typography variant="body2" color="textSecondary">
                Continuous authentication is active
              </Typography>
            </div>
          </Grid>
          
          {/* Anomaly Alerts */}
          <Grid item xs={12}>
            <div className="neumorphic-card" style={{ padding: '16px' }}>
              <Typography variant="h6" gutterBottom>
                Anomaly Alerts
              </Typography>
              {anomalyAlerts.length === 0 ? (
                <Typography variant="body1" color="textSecondary">
                  No anomalies detected
                </Typography>
              ) : (
                <Grid container spacing={2}>
                  {anomalyAlerts.map((alert) => (
                    <Grid item xs={12} sm={6} md={4} key={alert.id}>
                      <div className={`neumorphic-card-alert ${alert.confidence > 0.8 ? 'error' : 'warning'}`} style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                          {renderAnomalyIcon(alert.type)}
                          <div style={{ marginLeft: '8px' }}>
                            <Typography variant="subtitle1">{`${alert.type.charAt(0).toUpperCase() + alert.type.slice(1)} Anomaly`}</Typography>
                            <Typography variant="caption">{new Date(alert.timestamp).toLocaleString()}</Typography>
                          </div>
                        </div>
                        <Typography variant="body2">
                          {alert.details}
                        </Typography>
                        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                          Confidence: {Math.round(alert.confidence * 100)}%
                        </Typography>
                      </div>
                    </Grid>
                  ))}
                </Grid>
                )}
              </div>
            </Grid>
          </Grid>
        </Container>
      </Box>
    );
};

// Get color based on security score
const getSecurityScoreColor = (userData) => {
  const score = userData?.securityScore || 0;
  if (score >= 80) return 'var(--success-color)';
  if (score >= 60) return 'var(--warning-color)';
  return 'var(--error-color)';
};

export default Dashboard;