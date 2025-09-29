import React from 'react';
import { Box, Container, Typography, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import '../styles/modern-auth.css';

const Register = () => {
  return (
    <Box className="modern-auth-container">
      <AuthForm isRegister={true} />
      <Box sx={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
        <Typography variant="body2" sx={{ color: 'rgba(0,0,0,0.6)' }}>
          Already have an account?{' '}
          <Link component={RouterLink} to="/login" underline="hover" sx={{ color: '#667eea', fontWeight: 600 }}>
            Sign in here
          </Link>
        </Typography>
      </Box>
    </Box>
  );
};

export default Register;