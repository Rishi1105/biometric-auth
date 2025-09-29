import React, { useState, useRef, useEffect } from 'react';
import { Box, Typography, Grid, Alert } from '@mui/material';
import { FaceRetouchingOff, Fingerprint, Keyboard, Mouse, Visibility, VisibilityOff, Person, Email, Lock } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { behaviorService } from '../services/behaviorService';
import LoadingSpinner from './LoadingSpinner';
import '../styles/void-auth.css';

const AuthForm = ({ isRegister: initialIsRegister = false }) => {
  const [isRegister, setIsRegister] = useState(initialIsRegister);
  const [formState, setFormState] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    step: 'credentials', // credentials -> biometric -> behavioral -> complete
    loading: false,
    error: null,
    biometricType: 'face', // face, fingerprint
    behavioralMonitoring: false,
    transitioning: false,
    transitionDirection: 'forward', // forward or backward
    previousStep: null,
    userId: null,
    token: null,
    showPassword: false
  });
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const navigate = useNavigate();
  
  // Generate transition effects for step changes
  const generateTransitionEffects = () => {
    if (!formState.transitioning) return null;
    
    return (
      <div className="transition-overlay" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1000,
        pointerEvents: 'none',
        background: 'radial-gradient(circle, transparent, rgba(0, 0, 0, 0.8))'
      }}>
        {/* Transition energy burst */}
        <div className="transition-burst" style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '100px',
          height: '100px',
          transform: 'translate(-50%, -50%)',
          animation: 'transitionBurst 0.8s ease-out forwards'
        }}>
          <div style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            border: '3px solid var(--neon-cyan)',
            borderRadius: '50%',
            animation: 'voidSpin 0.5s linear infinite'
          }} />
          <div style={{
            position: 'absolute',
            width: '80%',
            height: '80%',
            top: '10%',
            left: '10%',
            border: '2px solid var(--neon-purple)',
            borderRadius: '50%',
            animation: 'voidSpin 0.3s linear infinite reverse'
          }} />
        </div>
        
        {/* Transition particles */}
        {Array.from({ length: 20 }, (_, i) => {
          const angle = (i / 20) * Math.PI * 2;
          const distance = 200 + Math.random() * 100;
          const endX = Math.cos(angle) * distance;
          const endY = Math.sin(angle) * distance;
          
          return (
            <div
              key={`transition-particle-${i}`}
              style={{
                position: 'absolute',
                width: '4px',
                height: '4px',
                background: `var(--${['neon-cyan', 'neon-purple', 'neon-pink'][i % 3]})`,
                borderRadius: '50%',
                top: '50%',
                left: '50%',
                animation: `transitionParticleFly ${0.6 + Math.random() * 0.4}s ease-out forwards`,
                animationDelay: `${Math.random() * 0.2}s`,
                boxShadow: '0 0 10px currentColor',
                '--particle-end-x': `${endX}px`,
                '--particle-end-y': `${endY}px`
              }}
            />
          );
        })}
        
        {/* Transition energy waves */}
        {Array.from({ length: 3 }, (_, i) => (
          <div
            key={`transition-wave-${i}`}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: '50px',
              height: '50px',
              border: `2px solid var(--${['neon-cyan', 'neon-purple', 'neon-pink'][i]})`,
              borderRadius: '50%',
              transform: 'translate(-50%, -50%)',
              animation: `transitionWaveExpand ${0.8 + i * 0.2}s ease-out forwards`,
              animationDelay: `${i * 0.1}s`
            }}
          />
        ))}
      </div>
    );
  };

  // Handle step transitions with void-like animations
  const transitionToStep = (newStep, direction = 'forward') => {
    setFormState({
      ...formState,
      transitioning: true,
      transitionDirection: direction,
      previousStep: formState.step
    });
    
    setTimeout(() => {
      setFormState(prev => ({
        ...prev,
        step: newStep,
        transitioning: false,
        previousStep: prev.step
      }));
    }, 800);
  };

  // Generate energy particles for background effect
  const generateEnergyParticles = () => {
    const particles = [];
    for (let i = 0; i < 50; i++) {
      particles.push(
        <div
          key={i}
          className="energy-particle"
          style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 4}s`,
            animationDuration: `${3 + Math.random() * 3}s`
          }}
        />
      );
    }
    return particles;
  };

  // Generate neon veins for background effect
  const generateNeonVeins = () => {
    const veins = [];
    for (let i = 0; i < 20; i++) {
      const isVertical = Math.random() > 0.5;
      veins.push(
        <div
          key={i}
          className={`neon-vein ${isVertical ? 'vertical' : ''}`}
          style={{
            top: isVertical ? `${Math.random() * 100}%` : `${20 + Math.random() * 60}%`,
            left: isVertical ? `${10 + Math.random() * 80}%` : '0',
            width: isVertical ? '1px' : `${100 + Math.random() * 200}px`,
            height: isVertical ? `${50 + Math.random() * 100}px` : '1px',
            animationDelay: `${Math.random() * 8}s`,
            animationDuration: `${6 + Math.random() * 4}s`
          }}
        />
      );
    }
    return veins;
  };

  // Handle form input changes
  const handleChange = (e) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
      error: null // Clear error when user starts typing
    });
  };
  
  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setFormState({ ...formState, showPassword: !formState.showPassword });
  };
  
  // Handle credential submission
  const handleCredentialSubmit = async (e) => {
    e.preventDefault();
    setFormState({ ...formState, loading: true, error: null });
    
    try {
      let response;
      
      if (isRegister) {
        response = await authService.register({
          username: formState.username,
          password: formState.password,
          email: formState.email,
          full_name: formState.full_name
        });
        setFormState({
          ...formState,
          loading: false,
          step: 'biometric',
          userId: response.userId,
          token: response.token
        });
      } else {
        response = await authService.login(formState.username, formState.password);
        setFormState({
          ...formState,
          loading: false,
          step: 'biometric',
          userId: response.userId,
          token: response.token
        });
      }
    } catch (error) {
      setFormState({
        ...formState,
        loading: false,
        error: error.message || (isRegister ? 'Registration failed. Please try again.' : 'Authentication failed. Please try again.')
      });
    }
  };
  
  // Handle biometric authentication
  const handleBiometricAuth = async () => {
    setFormState({ ...formState, loading: true, error: null });
    
    try {
      let biometricData;
      
      if (formState.biometricType === 'face') {
        biometricData = await captureFace();
      } else {
        biometricData = await captureFingerprint();
      }
      
      const response = await authService.verifyBiometric(
        formState.userId,
        formState.token,
        formState.biometricType,
        biometricData
      );
      
      setFormState({
        ...formState,
        loading: false,
        step: 'behavioral',
        token: response.token
      });
      
      // Start behavioral monitoring
      startBehavioralMonitoring();
      
    } catch (error) {
      setFormState({
        ...formState,
        loading: false,
        error: error.message || 'Biometric verification failed. Please try again.'
      });
    }
  };
  
  // Handle behavioral authentication
  const handleBehavioralAuth = () => {
    setFormState({ ...formState, behavioralMonitoring: true, error: null });
    
    // Start keystroke monitoring
    behaviorService.startKeystrokeMonitoring(formState.userId, formState.token);
    
    // Start mouse monitoring
    behaviorService.startMouseMonitoring(formState.userId, formState.token);
    
    // Start device monitoring
    behaviorService.startDeviceMonitoring(formState.userId, formState.token);
    
    // After a short period, transition to complete step with void animation
    setTimeout(() => {
      setFormState({
        ...formState,
        behavioralMonitoring: false
      });
      
      // Transition to complete step with void animation
      transitionToStep('complete', 'forward');
      
      // Store authentication token and redirect to dashboard
      localStorage.setItem('authToken', formState.token);
      localStorage.setItem('userId', formState.userId);
      navigate('/dashboard');
    }, 3000);
  };
  
  // Add back navigation capability
  const goBack = () => {
    const stepOrder = ['credentials', 'biometric', 'behavioral', 'complete'];
    const currentIndex = stepOrder.indexOf(formState.step);
    
    if (currentIndex > 0) {
      transitionToStep(stepOrder[currentIndex - 1], 'backward');
    }
  };
  
  // Generate advanced ambient energy particles
  const generateAdvancedEnergyParticles = () => {
    const particles = [];
    for (let i = 0; i < 30; i++) {
      const size = Math.random() * 4 + 1;
      const duration = Math.random() * 8 + 4;
      const delay = Math.random() * 5;
      const colors = ['neon-cyan', 'neon-purple', 'neon-pink', 'neon-blue', 'neon-green'];
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      particles.push(
        <div
          key={`advanced-particle-${i}`}
          className="advanced-energy-particle"
          style={{
            position: 'absolute',
            width: `${size}px`,
            height: `${size}px`,
            background: `var(--${color})`,
            borderRadius: '50%',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `advancedParticleFloat ${duration}s ease-in-out infinite`,
            animationDelay: `${delay}s`,
            boxShadow: `0 0 ${size * 2}px var(--${color})`,
            opacity: Math.random() * 0.8 + 0.2
          }}
        />
      );
    }
    return particles;
  };

  // Generate energy streams that flow across the screen
  const generateEnergyStreams = () => {
    const streams = [];
    for (let i = 0; i < 6; i++) {
      const width = Math.random() * 3 + 1;
      const duration = Math.random() * 10 + 8;
      const delay = Math.random() * 3;
      const colors = ['neon-cyan', 'neon-purple', 'neon-pink'];
      const color = colors[i % colors.length];
      const isHorizontal = Math.random() > 0.5;
      
      streams.push(
        <div
          key={`energy-stream-${i}`}
          className="energy-stream"
          style={{
            position: 'absolute',
            width: isHorizontal ? '200px' : `${width}px`,
            height: isHorizontal ? `${width}px` : '200px',
            background: `linear-gradient(${isHorizontal ? '90deg' : '0deg'}, 
              transparent, 
              var(--${color}), 
              transparent)`,
            left: isHorizontal ? '-200px' : `${Math.random() * 100}%`,
            top: isHorizontal ? `${Math.random() * 100}%` : '-200px',
            animation: isHorizontal ? 
              `energyStreamHorizontal ${duration}s linear infinite` : 
              `energyStreamVertical ${duration}s linear infinite`,
            animationDelay: `${delay}s`,
            opacity: 0.6
          }}
        />
      );
    }
    return streams;
  };

  // Generate floating energy orbs
  const generateEnergyOrbs = () => {
    const orbs = [];
    for (let i = 0; i < 8; i++) {
      const size = Math.random() * 20 + 10;
      const duration = Math.random() * 12 + 8;
      const delay = Math.random() * 4;
      const colors = ['neon-cyan', 'neon-purple', 'neon-pink'];
      const color = colors[i % colors.length];
      
      orbs.push(
        <div
          key={`energy-orb-${i}`}
          className="energy-orb"
          style={{
            position: 'absolute',
            width: `${size}px`,
            height: `${size}px`,
            background: `radial-gradient(circle, var(--${color}), transparent)`,
            borderRadius: '50%',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `orbFloat ${duration}s ease-in-out infinite`,
            animationDelay: `${delay}s`,
            boxShadow: `0 0 ${size}px var(--${color})`,
            opacity: 0.4
          }}
        />
      );
    }
    return orbs;
  };

  // Generate digital rain effect
  const generateDigitalRain = () => {
    const rain = [];
    for (let i = 0; i < 15; i++) {
      const duration = Math.random() * 3 + 2;
      const delay = Math.random() * 5;
      const left = `${Math.random() * 100}%`;
      
      rain.push(
        <div
          key={`digital-rain-${i}`}
          className="digital-rain"
          style={{
            position: 'absolute',
            left: left,
            top: '-50px',
            fontFamily: 'Orbitron, monospace',
            fontSize: '12px',
            color: 'var(--neon-cyan)',
            animation: `digitalRain ${duration}s linear infinite`,
            animationDelay: `${delay}s`,
            opacity: 0.7,
            textShadow: '0 0 5px var(--neon-cyan)',
            writingMode: 'vertical-rl',
            textOrientation: 'mixed'
          }}
        >
          {Array.from({ length: 20 }, (_, j) => (
            <div key={`rain-char-${i}-${j}`} style={{ marginBottom: '2px' }}>
              {Math.random().toString(36).substring(2, 3).toUpperCase()}
            </div>
          ))}
        </div>
      );
    }
    return rain;
  };

  // Generate pulsing energy waves
  const generateEnergyWaves = () => {
    const waves = [];
    for (let i = 0; i < 4; i++) {
      const duration = Math.random() * 6 + 4;
      const delay = Math.random() * 3;
      const colors = ['neon-cyan', 'neon-purple', 'neon-pink'];
      const color = colors[i % colors.length];
      
      waves.push(
        <div
          key={`energy-wave-${i}`}
          className="energy-wave"
          style={{
            position: 'absolute',
            width: '100px',
            height: '100px',
            border: `2px solid var(--${color})`,
            borderRadius: '50%',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `energyWaveExpand ${duration}s ease-out infinite`,
            animationDelay: `${delay}s`,
            opacity: 0
          }}
        />
      );
    }
    return waves;
  };

  // Generate enhanced energy particles for biometric capture
  const generateBiometricParticles = () => {
    const particles = [];
    for (let i = 0; i < 20; i++) {
      particles.push(
        <div
          key={`biometric-${i}`}
          className="biometric-particle"
          style={{
            position: 'absolute',
            width: '3px',
            height: '3px',
            background: `var(--${['neon-cyan', 'neon-purple', 'neon-pink', 'neon-blue'][i % 4]})`,
            borderRadius: '50%',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `biometricFloat ${2 + Math.random() * 3}s ease-in-out infinite`,
            animationDelay: `${Math.random() * 2}s`,
            boxShadow: '0 0 6px currentColor',
            opacity: 0.7
          }}
        />
      );
    }
    return particles;
  };

  // Generate neon vein effects for digital city aesthetics
  const generateNeonVeinsEnhanced = () => {
    const veins = [];
    for (let i = 0; i < 8; i++) {
      veins.push(
        <div
          key={`vein-${i}`}
          className="neon-vein-enhanced"
          style={{
            position: 'absolute',
            width: '2px',
            height: '100%',
            background: `linear-gradient(0deg, 
              transparent, 
              var(--${['neon-cyan', 'neon-purple', 'neon-pink'][i % 3]}), 
              transparent)`,
            left: `${(i + 1) * (100 / 9)}%`,
            animation: `veinFlowEnhanced ${4 + i * 0.5}s linear infinite`,
            animationDelay: `${i * 0.3}s`,
            opacity: 0.4
          }}
        />
      );
    }
    return veins;
  };

  // Capture face data from webcam
  const captureFace = async () => {
    console.log('Starting face capture...');
    if (!videoRef.current) {
      throw new Error('Webcam not available');
    }
    
    // Capture frame from video
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    
    context.drawImage(videoRef.current, 0, 0);
    
    // Convert to base64 (in a real app, this would be processed by a face recognition model)
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Simulate face recognition processing
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return imageData;
  };
  
  // Capture fingerprint data (simulated)
  const captureFingerprint = async () => {
    console.log('Starting fingerprint capture...');
    // In a real app, this would interface with a fingerprint scanner
    // For demo purposes, we'll simulate the process
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Return mock fingerprint data
    return 'mock_fingerprint_data_' + Date.now();
  };
  
  // Start behavioral monitoring
  const startBehavioralMonitoring = () => {
    console.log('Starting behavioral monitoring...');
    if (formState.userId && formState.token) {
      behaviorService.startKeystrokeMonitoring(formState.userId, formState.token);
      behaviorService.startMouseMonitoring(formState.userId, formState.token);
      behaviorService.startDeviceMonitoring(formState.userId, formState.token);
    }
  };

  // Generate fingerprint scanner visualization
  const generateFingerprintScanner = () => {
    return (
      <div style={{
        position: 'relative',
        width: '200px',
        height: '200px',
        margin: '0 auto',
        background: 'radial-gradient(circle, rgba(138, 43, 226, 0.1), transparent)',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {/* Fingerprint ridges */}
        {Array.from({ length: 5 }, (_, i) => (
          <div
            key={`ridge-${i}`}
            style={{
              position: 'absolute',
              width: `${40 + i * 30}px`,
              height: `${40 + i * 30}px`,
              border: '2px solid var(--neon-purple)',
              borderRadius: '50%',
              opacity: 0.6 - i * 0.1,
              animation: `pulse ${1 + i * 0.2}s ease-in-out infinite`
            }}
          />
        ))}
        <Fingerprint style={{ 
          fontSize: '60px', 
          color: 'var(--neon-purple)',
          animation: 'pulse 2s ease-in-out infinite'
        }} />
      </div>
    );
  };

  // Generate neural network visualization
  const generateNeuralNetwork = () => {
    const nodes = [];
    const connections = [];
    
    // Generate nodes
    for (let i = 0; i < 15; i++) {
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      nodes.push(
        <div
          key={`node-${i}`}
          style={{
            position: 'absolute',
            width: '8px',
            height: '8px',
            background: 'var(--neon-pink)',
            borderRadius: '50%',
            left: `${x}%`,
            top: `${y}%`,
            animation: `pulse ${2 + Math.random() * 2}s ease-in-out infinite`,
            animationDelay: `${Math.random() * 2}s`
          }}
        />
      );
    }
    
    // Generate connections
    for (let i = 0; i < 10; i++) {
      connections.push(
        <div
          key={`connection-${i}`}
          style={{
            position: 'absolute',
            width: `${50 + Math.random() * 50}px`,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, var(--neon-pink), transparent)',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            transform: `rotate(${Math.random() * 360}deg)`,
            opacity: 0.3,
            animation: `pulse ${3 + Math.random() * 2}s ease-in-out infinite`
          }}
        />
      );
    }
    
    return [...connections, ...nodes];
  };

  // Generate digital city grid background
  const generateCityGrid = () => {
    const grid = [];
    for (let i = 0; i < 12; i++) {
      grid.push(
        <div
          key={`grid-h-${i}`}
          className="city-grid-line"
          style={{
            position: 'absolute',
            width: '100%',
            height: '1px',
            background: 'linear-gradient(90deg, transparent, var(--neon-cyan), transparent)',
            top: `${(i + 1) * (100 / 13)}%`,
            animation: `cityPulse ${3 + i * 0.2}s ease-in-out infinite`,
            animationDelay: `${i * 0.1}s`,
            opacity: 0.3
          }}
        />
      );
      
      grid.push(
        <div
          key={`grid-v-${i}`}
          className="city-grid-line"
          style={{
            position: 'absolute',
            width: '1px',
            height: '100%',
            background: 'linear-gradient(0deg, transparent, var(--neon-purple), transparent)',
            left: `${(i + 1) * (100 / 13)}%`,
            animation: `cityPulse ${3 + i * 0.2}s ease-in-out infinite`,
            animationDelay: `${i * 0.15}s`,
            opacity: 0.3
          }}
        />
      );
    }
    return grid;
  };
  
  // Generate scanning reticle for face recognition
  const generateScanningReticle = () => {
    // This function is currently a placeholder to fix a compilation error.
    // It can be implemented later to provide a visual effect.
    return null;
  };

  const renderFormStep = () => {
    // Apply transition classes based on current state
    const stepClasses = {
      credentials: 'form-step-credentials',
      biometric: 'form-step-biometric',
      behavioral: 'form-step-behavioral',
      complete: 'form-step-complete'
    };
    
    const transitionClass = formState.transitioning 
      ? `transitioning-${formState.transitionDirection}` 
      : 'step-active';
    
    const stepClass = `${stepClasses[formState.step]} ${transitionClass}`;
    
    switch (formState.step) {
      case 'credentials':
        return (
          <div className={stepClass} style={{
            animation: formState.transitioning ? 'stepFadeOut 0.4s ease-out forwards' : 'stepFadeIn 0.6s ease-out forwards'
          }}>
            <div className="auth-header">
              <h1 style={{
                fontFamily: 'Orbitron, sans-serif',
                fontSize: '2.5rem',
                fontWeight: 700,
                background: 'linear-gradient(45deg, var(--neon-cyan), var(--neon-purple))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 0 30px rgba(0, 255, 255, 0.5)',
                marginBottom: '0.5rem',
                animation: 'textPulse 2s ease-in-out infinite'
              }}>
                {isRegister ? 'ENTER THE VOID' : 'VOID ACCESS'}
              </h1>
              <p style={{
                fontFamily: 'Rajdhani, sans-serif',
                fontSize: '1.1rem',
                color: 'var(--neon-cyan)',
                opacity: 0.8,
                marginBottom: '2rem'
              }}>
                {isRegister 
                  ? 'Initialize your digital consciousness...' 
                  : 'Authenticate your presence in the void...'}
              </p>
            </div>
            
            <form onSubmit={handleCredentialSubmit} className="void-form">
              <div className="form-group">
                <label style={{
                  fontFamily: 'Rajdhani, sans-serif',
                  color: 'var(--neon-cyan)',
                  fontWeight: 600,
                  marginBottom: '0.5rem',
                  display: 'block',
                  textTransform: 'uppercase',
                  fontSize: '0.9rem',
                  letterSpacing: '1px'
                }}>
                  Digital Identity
                </label>
                <input
                  type="text"
                  value={formState.username}
                  onChange={(e) => setFormState({ ...formState, username: e.target.value })}
                  className="void-input"
                  placeholder="Enter your digital signature..."
                  required
                  style={{
                    width: '100%',
                    padding: '1rem',
                    background: 'rgba(0, 0, 0, 0.7)',
                    border: '2px solid var(--neon-cyan)',
                    borderRadius: '10px',
                    color: 'var(--neon-cyan)',
                    fontFamily: 'Rajdhani, sans-serif',
                    fontSize: '1rem',
                    outline: 'none',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 0 20px rgba(0, 255, 255, 0.2)'
                  }}
                />
              </div>
              
              <div className="form-group">
                <label style={{
                  fontFamily: 'Rajdhani, sans-serif',
                  color: 'var(--neon-purple)',
                  fontWeight: 600,
                  marginBottom: '0.5rem',
                  display: 'block',
                  textTransform: 'uppercase',
                  fontSize: '0.9rem',
                  letterSpacing: '1px'
                }}>
                  Void Key
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={formState.showPassword ? "text" : "password"}
                    value={formState.password}
                    onChange={(e) => setFormState({ ...formState, password: e.target.value })}
                    className="void-input"
                    placeholder="Enter your void key..."
                    required
                    style={{
                      width: '100%',
                      padding: '1rem',
                      background: 'rgba(0, 0, 0, 0.7)',
                      border: '2px solid var(--neon-purple)',
                      borderRadius: '10px',
                      color: 'var(--neon-purple)',
                      fontFamily: 'Rajdhani, sans-serif',
                      fontSize: '1rem',
                      outline: 'none',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 0 20px rgba(138, 43, 226, 0.2)'
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setFormState({ ...formState, showPassword: !formState.showPassword })}
                    style={{
                      position: 'absolute',
                      right: '10px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      color: 'var(--neon-purple)',
                      cursor: 'pointer',
                      fontSize: '1.2rem'
                    }}
                  >
                    {formState.showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>
              
              {isRegister && (
                <>
                  <div className="form-group">
                    <label style={{
                      fontFamily: 'Rajdhani, sans-serif',
                      color: 'var(--neon-pink)',
                      fontWeight: 600,
                      marginBottom: '0.5rem',
                      display: 'block',
                      textTransform: 'uppercase',
                      fontSize: '0.9rem',
                      letterSpacing: '1px'
                    }}>
                      Consciousness Link
                    </label>
                    <input
                      type="email"
                      value={formState.email}
                      onChange={(e) => setFormState({ ...formState, email: e.target.value })}
                      className="void-input"
                      placeholder="Connect your consciousness..."
                      required
                      style={{
                        width: '100%',
                        padding: '1rem',
                        background: 'rgba(0, 0, 0, 0.7)',
                        border: '2px solid var(--neon-pink)',
                        borderRadius: '10px',
                        color: 'var(--neon-pink)',
                        fontFamily: 'Rajdhani, sans-serif',
                        fontSize: '1rem',
                        outline: 'none',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 0 20px rgba(255, 20, 147, 0.2)'
                      }}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label style={{
                      fontFamily: 'Rajdhani, sans-serif',
                      color: 'var(--neon-blue)',
                      fontWeight: 600,
                      marginBottom: '0.5rem',
                      display: 'block',
                      textTransform: 'uppercase',
                      fontSize: '0.9rem',
                      letterSpacing: '1px'
                    }}>
                      True Name
                    </label>
                    <input
                      type="text"
                      value={formState.full_name}
                      onChange={(e) => setFormState({ ...formState, full_name: e.target.value })}
                      className="void-input"
                      placeholder="Reveal your true name..."
                      required
                      style={{
                        width: '100%',
                        padding: '1rem',
                        background: 'rgba(0, 0, 0, 0.7)',
                        border: '2px solid var(--neon-blue)',
                        borderRadius: '10px',
                        color: 'var(--neon-blue)',
                        fontFamily: 'Rajdhani, sans-serif',
                        fontSize: '1rem',
                        outline: 'none',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 0 20px rgba(0, 191, 255, 0.2)'
                      }}
                    />
                  </div>
                </>
              )}
              
              <div className="form-actions" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginTop: '2rem'
              }}>
                <button
                  type="button"
                  onClick={() => setIsRegister(!isRegister)}
                  className="void-button-secondary"
                  style={{
                    padding: '1rem 2rem',
                    background: 'transparent',
                    border: '2px solid var(--neon-cyan)',
                    borderRadius: '10px',
                    color: 'var(--neon-cyan)',
                    fontFamily: 'Rajdhani, sans-serif',
                    fontSize: '1rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}
                >
                  {isRegister ? 'EXISTING CONSCIOUSNESS' : 'NEW CONSCIOUSNESS'}
                </button>
                
                <button
                  type="submit"
                  disabled={formState.loading}
                  className="void-button-primary"
                  style={{
                    padding: '1rem 2rem',
                    background: 'linear-gradient(45deg, var(--neon-cyan), var(--neon-purple))',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#000',
                    fontFamily: 'Orbitron, sans-serif',
                    fontSize: '1rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)'
                  }}
                >
                  {formState.loading ? (
                    <LoadingSpinner size={20} message="" />
                  ) : (
                    isRegister ? 'INITIALIZE' : 'ACCESS VOID'
                  )}
                </button>
              </div>
            </form>
          </div>
        );
        
      case 'biometric':
        return (
          <div className={stepClass} style={{
            animation: formState.transitioning ? 'stepFadeOut 0.4s ease-out forwards' : 'stepFadeIn 0.6s ease-out forwards'
          }}>
            <div className="auth-header">
              <h1 style={{
                fontFamily: 'Orbitron, sans-serif',
                fontSize: '2.5rem',
                fontWeight: 700,
                background: 'linear-gradient(45deg, var(--neon-purple), var(--neon-pink))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 0 30px rgba(138, 43, 226, 0.5)',
                marginBottom: '0.5rem',
                animation: 'textPulse 2s ease-in-out infinite'
              }}>
                BIOMETRIC VOID
              </h1>
              <p style={{
                fontFamily: 'Rajdhani, sans-serif',
                fontSize: '1.1rem',
                color: 'var(--neon-purple)',
                opacity: 0.8,
                marginBottom: '2rem'
              }}>
                Merge your essence with the digital void...
              </p>
            </div>
            
            <div className="biometric-type-selector" style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <button
                onClick={() => setFormState({ ...formState, biometricType: 'face' })}
                className={`biometric-type-btn ${formState.biometricType === 'face' ? 'active' : ''}`}
                style={{
                  padding: '1rem 2rem',
                  background: formState.biometricType === 'face' 
                    ? 'linear-gradient(45deg, var(--neon-purple), var(--neon-pink))' 
                    : 'transparent',
                  border: '2px solid var(--neon-purple)',
                  borderRadius: '10px',
                  color: formState.biometricType === 'face' ? '#000' : 'var(--neon-purple)',
                  fontFamily: 'Rajdhani, sans-serif',
                  fontSize: '1rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}
              >
                Facial Essence
              </button>
              <button
                onClick={() => setFormState({ ...formState, biometricType: 'fingerprint' })}
                className={`biometric-type-btn ${formState.biometricType === 'fingerprint' ? 'active' : ''}`}
                style={{
                  padding: '1rem 2rem',
                  background: formState.biometricType === 'fingerprint' 
                    ? 'linear-gradient(45deg, var(--neon-purple), var(--neon-pink))' 
                    : 'transparent',
                  border: '2px solid var(--neon-purple)',
                  borderRadius: '10px',
                  color: formState.biometricType === 'fingerprint' ? '#000' : 'var(--neon-purple)',
                  fontFamily: 'Rajdhani, sans-serif',
                  fontSize: '1rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}
              >
                Digital Essence
              </button>
            </div>
            
            <div className="biometric-capture-enhanced" style={{ 
              position: 'relative', 
              marginBottom: '2rem',
              height: '350px',
              borderRadius: '20px',
              overflow: 'hidden',
              background: 'rgba(0, 0, 0, 0.8)',
              border: '2px solid var(--neon-cyan)',
              boxShadow: '0 0 40px rgba(0, 255, 255, 0.3)'
            }}>
              {/* Digital city grid background */}
              <div className="city-grid" style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                opacity: 0.3
              }}>
                {generateCityGrid()}
              </div>
              
              {/* Enhanced neon veins */}
              <div className="neon-veins-enhanced" style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                opacity: 0.5
              }}>
                {generateNeonVeinsEnhanced()}
              </div>
              
              {formState.biometricType === 'face' ? (
                <div className="camera-container-enhanced" style={{ 
                  position: 'relative', 
                  height: '100%', 
                  overflow: 'hidden', 
                  borderRadius: '20px' 
                }}>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="camera-feed"
                    style={{ 
                      width: '100%', 
                      height: '100%', 
                      objectFit: 'cover',
                      filter: 'contrast(1.2) brightness(1.1)'
                    }}
                  />
                  <canvas
                    ref={canvasRef}
                    width="640"
                    height="480"
                    style={{ display: 'none' }}
                  />
                  
                  {/* Enhanced scan line */}
                  <div className="scan-line-enhanced" style={{
                    position: 'absolute',
                    width: '100%',
                    height: '3px',
                    background: 'linear-gradient(90deg, transparent, var(--neon-cyan), transparent)',
                    top: '0%',
                    animation: 'scanLine 2s linear infinite',
                    boxShadow: '0 0 20px var(--neon-cyan)'
                  }} />
                  
                  {/* Scanning reticle */}
                  {generateScanningReticle()}
                  
                  {/* Biometric particles */}
                  {generateBiometricParticles()}
                  
                  {/* Data stream overlay */}
                  <div className="data-stream" style={{
                    position: 'absolute',
                    top: '10px',
                    left: '10px',
                    right: '10px',
                    bottom: '10px',
                    pointerEvents: 'none',
                    fontFamily: 'Orbitron, monospace',
                    fontSize: '10px',
                    color: 'var(--neon-cyan)',
                    opacity: 0.6
                  }}>
                    <div style={{ position: 'absolute', top: '0', left: '0' }}>
                      {Array.from({ length: 20 }, (_, i) => (
                        <div key={`data-${i}`} style={{ marginBottom: '2px' }}>
                          {Math.random().toString(36).substring(2, 15).toUpperCase()}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="fingerprint-container-enhanced" style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '100%', 
                  borderRadius: '20px',
                  background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(75, 0, 130, 0.3))',
                  border: '2px solid var(--neon-purple)',
                  position: 'relative'
                }}>
                  {/* Fingerprint scanner */}
                  {generateFingerprintScanner()}
                  
                  {/* Status text */}
                  <div style={{ 
                    position: 'absolute',
                    bottom: '30px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    textAlign: 'center',
                    fontFamily: 'Rajdhani, sans-serif'
                  }}>
                    <p style={{ 
                      color: 'var(--neon-purple)', 
                      opacity: 0.9,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      textShadow: '0 0 10px var(--neon-purple)',
                      animation: 'textPulse 2s ease-in-out infinite'
                    }}>
                      PLACE YOUR ESSENCE
                    </p>
                    <p style={{ 
                      color: 'var(--neon-pink)', 
                      opacity: 0.7,
                      fontSize: '0.9rem',
                      marginTop: '5px'
                    }}>
                      Finger recognition active
                    </p>
                  </div>
                </div>
              )}
            </div>
            
            <button 
              className="neon-button"
              onClick={handleBiometricAuth}
              disabled={formState.loading}
            >
              {formState.loading ? (
                <div className="void-loader" style={{ width: '24px', height: '24px' }} />
              ) : (
                'SYNC ESSENCE'
              )}
            </button>
          </div>
        );
        
      case 'behavioral':
        return (
          <div className={stepClass} style={{
            animation: formState.transitioning ? 'stepFadeOut 0.4s ease-out forwards' : 'stepFadeIn 0.6s ease-out forwards'
          }}>
            <div className="auth-header">
              <h1 style={{
                fontFamily: 'Orbitron, sans-serif',
                fontSize: '2.5rem',
                fontWeight: 700,
                background: 'linear-gradient(45deg, var(--neon-pink), var(--neon-blue))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 0 30px rgba(255, 20, 147, 0.5)',
                marginBottom: '0.5rem',
                animation: 'textPulse 2s ease-in-out infinite'
              }}>
                BEHAVIORAL VOID
              </h1>
              <p style={{
                fontFamily: 'Rajdhani, sans-serif',
                fontSize: '1.1rem',
                color: 'var(--neon-pink)',
                opacity: 0.8,
                marginBottom: '2rem'
              }}>
                Your digital signature is being analyzed...
              </p>
            </div>
            
            <div className="behavioral-monitoring" style={{
              position: 'relative',
              height: '300px',
              background: 'rgba(0, 0, 0, 0.8)',
              border: '2px solid var(--neon-pink)',
              borderRadius: '20px',
              padding: '2rem',
              marginBottom: '2rem',
              overflow: 'hidden'
            }}>
              {/* Neural network background */}
              <div className="neural-network" style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                opacity: 0.3
              }}>
                {generateNeuralNetwork()}
              </div>
              
              <div style={{ position: 'relative', zIndex: 2 }}>
                <div className="monitoring-status" style={{
                  textAlign: 'center',
                  marginBottom: '2rem'
                }}>
                  <div style={{
                    width: '80px',
                    height: '80px',
                    margin: '0 auto 1rem',
                    border: '3px solid var(--neon-pink)',
                    borderRadius: '50%',
                    animation: formState.behavioralMonitoring ? 'pulse 1s ease-in-out infinite' : 'none'
                  }}>
                    <span style={{ fontSize: '2rem' }}>🧠</span>
                  </div>
                  <h3 style={{
                    fontFamily: 'Orbitron, sans-serif',
                    color: 'var(--neon-pink)',
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    marginBottom: '0.5rem'
                  }}>
                    {formState.behavioralMonitoring ? 'ANALYZING...' : 'ANALYSIS COMPLETE'}
                  </h3>
                  <p style={{
                    fontFamily: 'Rajdhani, sans-serif',
                    color: 'var(--neon-pink)',
                    opacity: 0.8,
                    fontSize: '1rem'
                  }}>
                    {formState.behavioralMonitoring 
                      ? 'Monitoring your digital patterns...' 
                      : 'Behavioral signature verified'}
                  </p>
                </div>
                
                <div className="monitoring-metrics" style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '1rem'
                }}>
                  {[
                    { name: 'Keystroke', value: formState.behavioralMonitoring ? '98%' : '100%', color: 'var(--neon-cyan)' },
                    { name: 'Mouse', value: formState.behavioralMonitoring ? '95%' : '100%', color: 'var(--neon-purple)' },
                    { name: 'Device', value: formState.behavioralMonitoring ? '97%' : '100%', color: 'var(--neon-pink)' },
                    { name: 'Location', value: formState.behavioralMonitoring ? '99%' : '100%', color: 'var(--neon-blue)' }
                  ].map((metric, index) => (
                    <div key={index} style={{
                      background: 'rgba(0, 0, 0, 0.5)',
                      border: '1px solid ' + metric.color,
                      borderRadius: '10px',
                      padding: '1rem',
                      textAlign: 'center'
                    }}>
                      <div style={{
                        fontFamily: 'Rajdhani, sans-serif',
                        color: metric.color,
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        marginBottom: '0.5rem'
                      }}>
                        {metric.name}
                      </div>
                      <div style={{
                        fontFamily: 'Orbitron, sans-serif',
                        color: metric.color,
                        fontSize: '1.5rem',
                        fontWeight: 700
                      }}>
                        {metric.value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {!formState.behavioralMonitoring && (
              <div className="form-actions" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginTop: '2rem'
              }}>
                <button
                  onClick={goBack}
                  className="void-button-secondary"
                  style={{
                    padding: '1rem 2rem',
                    background: 'transparent',
                    border: '2px solid var(--neon-pink)',
                    borderRadius: '10px',
                    color: 'var(--neon-pink)',
                    fontFamily: 'Rajdhani, sans-serif',
                    fontSize: '1rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}
                >
                  ← RETURN
                </button>
                
                <button
                  onClick={handleBehavioralAuth}
                  className="void-button-primary"
                  style={{
                    padding: '1rem 2rem',
                    background: 'linear-gradient(45deg, var(--neon-pink), var(--neon-blue))',
                    border: 'none',
                    borderRadius: '10px',
                    color: '#000',
                    fontFamily: 'Orbitron, sans-serif',
                    fontSize: '1rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                    boxShadow: '0 0 30px rgba(255, 20, 147, 0.5)'
                  }}
                >
                  COMPLETE VOID
                </button>
              </div>
            )}
          </div>
        );
        
      case 'complete':
        return (
          <div className={stepClass} style={{
            animation: formState.transitioning ? 'stepFadeOut 0.4s ease-out forwards' : 'stepFadeIn 0.6s ease-out forwards'
          }}>
            <div className="auth-header">
              <h1 style={{
                fontFamily: 'Orbitron, sans-serif',
                fontSize: '2.5rem',
                fontWeight: 700,
                background: 'linear-gradient(45deg, var(--neon-blue), var(--neon-green))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 0 30px rgba(0, 191, 255, 0.5)',
                marginBottom: '0.5rem',
                animation: 'textPulse 2s ease-in-out infinite'
              }}>
                VOID COMPLETE
              </h1>
              <p style={{
                fontFamily: 'Rajdhani, sans-serif',
                fontSize: '1.1rem',
                color: 'var(--neon-blue)',
                opacity: 0.8,
                marginBottom: '2rem'
              }}>
                Your consciousness has been merged with the void...
              </p>
            </div>
            
            <div className="completion-animation" style={{
              position: 'relative',
              height: '300px',
              background: 'rgba(0, 0, 0, 0.8)',
              border: '2px solid var(--neon-blue)',
              borderRadius: '20px',
              marginBottom: '2rem',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Success animation */}
              <div style={{
                position: 'relative',
                width: '120px',
                height: '120px'
              }}>
                <div style={{
                  position: 'absolute',
                  width: '100%',
                  height: '100%',
                  border: '4px solid var(--neon-blue)',
                  borderRadius: '50%',
                  animation: 'voidSpin 2s linear infinite'
                }} />
                <div style={{
                  position: 'absolute',
                  width: '80%',
                  height: '80%',
                  top: '10%',
                  left: '10%',
                  border: '3px solid var(--neon-green)',
                  borderRadius: '50%',
                  animation: 'voidSpin 1.5s linear infinite reverse'
                }} />
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  fontSize: '3rem',
                  animation: 'pulse 1s ease-in-out infinite'
                }}>
                  ✨
                </div>
              </div>
              
              {/* Energy waves */}
              {Array.from({ length: 5 }, (_, i) => (
                <div
                  key={`wave-${i}`}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: '50px',
                    height: '50px',
                    border: `2px solid var(--${['neon-blue', 'neon-green'][i % 2]})`,
                    borderRadius: '50%',
                    transform: 'translate(-50%, -50%)',
                    animation: `energyWaveExpand ${2 + i * 0.5}s ease-out infinite`,
                    animationDelay: `${i * 0.3}s`
                  }}
                />
              ))}
            </div>
            
            <div className="completion-message" style={{
              textAlign: 'center',
              marginBottom: '2rem'
            }}>
              <h3 style={{
                fontFamily: 'Orbitron, sans-serif',
                color: 'var(--neon-blue)',
                fontSize: '1.5rem',
                fontWeight: 600,
                marginBottom: '1rem'
              }}>
                AUTHENTICATION SUCCESSFUL
              </h3>
              <p style={{
                fontFamily: 'Rajdhani, sans-serif',
                color: 'var(--neon-green)',
                opacity: 0.8,
                fontSize: '1.1rem',
                lineHeight: '1.6'
              }}>
                Welcome to the void, {formState.username}.<br />
                Your digital consciousness is now active.
              </p>
            </div>
            
            <div className="form-actions" style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              marginTop: '2rem'
            }}>
              <button
                onClick={() => {
                  localStorage.setItem('authToken', formState.token);
                  localStorage.setItem('userId', formState.userId);
                  navigate('/dashboard');
                }}
                className="void-button-primary"
                style={{
                  padding: '1rem 3rem',
                  background: 'linear-gradient(45deg, var(--neon-blue), var(--neon-green))',
                  border: 'none',
                  borderRadius: '10px',
                  color: '#000',
                  fontFamily: 'Orbitron, sans-serif',
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  boxShadow: '0 0 30px rgba(0, 191, 255, 0.5)'
                }}
              >
                ENTER DASHBOARD
              </button>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  // Initialize webcam when in biometric step and using face authentication
  useEffect(() => {
    if (formState.step === 'biometric' && formState.biometricType === 'face') {
      const startWebcam = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (error) {
          console.error('Error accessing webcam:', error);
          setFormState({
            ...formState,
            error: 'Could not access webcam. Please check permissions.'
          });
        }
      };
      
      startWebcam();
      
      // Cleanup function to stop webcam when component unmounts
      return () => {
        if (videoRef.current && videoRef.current.srcObject) {
          videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
      };
    }
  }, [formState.step, formState.biometricType]);
  
  // Render different form steps
  return (
    <div className="void-auth-container">
      {/* Advanced ambient background layers */}
      <div className="ambient-background" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
        pointerEvents: 'none'
      }}>
        {/* Advanced energy particles */}
        <div className="advanced-energy-particles">
          {generateAdvancedEnergyParticles()}
        </div>
        
        {/* Energy streams */}
        <div className="energy-streams">
          {generateEnergyStreams()}
        </div>
        
        {/* Floating energy orbs */}
        <div className="energy-orbs">
          {generateEnergyOrbs()}
        </div>
        
        {/* Digital rain */}
        <div className="digital-rain-container">
          {generateDigitalRain()}
        </div>
        
        {/* Energy waves */}
        <div className="energy-waves">
          {generateEnergyWaves()}
        </div>
        
        {/* Original energy particles */}
        <div className="energy-particles">
          {generateEnergyParticles()}
        </div>
        
        {/* Original neon veins */}
        <div className="neon-veins">
          {generateNeonVeins()}
        </div>
      </div>
      
      <div className="auth-wrapper" style={{ 
        position: 'relative', 
        zIndex: 10, 
        width: '100%', 
        maxWidth: '500px', 
        margin: '0 auto',
        padding: '2rem'
      }}>
        {formState.error && (
          <div style={{
            background: 'rgba(255, 0, 64, 0.1)',
            border: '1px solid var(--neon-red)',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1rem',
            color: 'var(--neon-red)',
            textAlign: 'center',
            fontFamily: 'Rajdhani, sans-serif',
            fontWeight: 600,
            boxShadow: '0 0 20px rgba(255, 0, 64, 0.3)'
          }}>
            {formState.error}
          </div>
        )}
        {renderFormStep()}
      </div>
    </div>
  );
};

export default AuthForm;