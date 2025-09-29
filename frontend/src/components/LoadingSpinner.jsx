import React from 'react';
import '../styles/void-auth.css';

const LoadingSpinner = ({ message = 'Entering the Void...', size = 80 }) => {
  // Generate energy particles for the loading animation
  const generateEnergyParticles = () => {
    const particles = [];
    for (let i = 0; i < 12; i++) {
      particles.push(
        <div
          key={i}
          className="energy-particle"
          style={{
            position: 'absolute',
            width: '4px',
            height: '4px',
            background: `var(--${['neon-cyan', 'neon-purple', 'neon-pink', 'neon-blue'][i % 4]})`,
            borderRadius: '50%',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            animation: `energyFlow ${1 + i * 0.2}s linear infinite`,
            animationDelay: `${i * 0.1}s`,
            boxShadow: '0 0 10px currentColor'
          }}
        />
      );
    }
    return particles;
  };

  // Generate shifting light beams
  const generateLightBeams = () => {
    const beams = [];
    for (let i = 0; i < 6; i++) {
      beams.push(
        <div
          key={i}
          style={{
            position: 'absolute',
            width: '2px',
            height: `${size * 0.8}px`,
            background: `linear-gradient(0deg, transparent, var(--${['neon-cyan', 'neon-purple', 'neon-pink'][i % 3]}), transparent)`,
            left: '50%',
            top: '50%',
            transform: `translate(-50%, -50%) rotate(${i * 60}deg)`,
            animation: `beamRotate ${3 + i * 0.5}s linear infinite`,
            opacity: 0.6
          }}
        />
      );
    }
    return beams;
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '200px',
      gap: '2rem'
    }}>
      <div style={{
        position: 'relative',
        width: `${size}px`,
        height: `${size}px`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {/* Outer energy ring */}
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          border: '3px solid transparent',
          borderTopColor: 'var(--neon-cyan)',
          borderRadius: '50%',
          animation: 'voidSpin 2s linear infinite',
          boxShadow: '0 0 20px var(--neon-cyan)'
        }} />
        
        {/* Middle energy ring */}
        <div style={{
          position: 'absolute',
          width: '80%',
          height: '80%',
          border: '2px solid transparent',
          borderRightColor: 'var(--neon-purple)',
          borderRadius: '50%',
          animation: 'voidSpin 1.5s linear infinite reverse',
          boxShadow: '0 0 15px var(--neon-purple)'
        }} />
        
        {/* Inner energy core */}
        <div style={{
          position: 'absolute',
          width: '40%',
          height: '40%',
          background: 'radial-gradient(circle, var(--neon-pink), transparent)',
          borderRadius: '50%',
          animation: 'corePulse 1s ease-in-out infinite',
          boxShadow: '0 0 30px var(--neon-pink)'
        }} />
        
        {/* Shifting light beams */}
        {generateLightBeams()}
        
        {/* Energy particles */}
        {generateEnergyParticles()}
        
        {/* Central void symbol */}
        <div style={{
          position: 'relative',
          zIndex: 10,
          color: 'var(--neon-cyan)',
          fontFamily: 'Orbitron, monospace',
          fontSize: `${size * 0.2}px`,
          fontWeight: 'bold',
          textShadow: '0 0 10px var(--neon-cyan)',
          animation: 'symbolGlow 2s ease-in-out infinite'
        }}>
          ∞
        </div>
      </div>
      
      <div style={{
        color: 'var(--neon-cyan)',
        fontFamily: 'Rajdhani, sans-serif',
        fontSize: '1.1rem',
        fontWeight: 500,
        textAlign: 'center',
        textShadow: '0 0 10px var(--neon-cyan)',
        animation: 'textPulse 2s ease-in-out infinite'
      }}>
        {message}
      </div>
    </div>
  );
};

export default LoadingSpinner;
