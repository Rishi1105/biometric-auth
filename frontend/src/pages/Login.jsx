import React from 'react';
import { Box, Container, Typography, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import '../styles/void-auth.css';

const Login = () => {
  return (
    <Box className="void-auth-container">
      <AuthForm />
      <Box sx={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
        <Typography variant="body2" sx={{ color: 'rgba(0,0,0,0.6)', mb: 1 }}>
          Don't have an account?{' '}
          <Link component={RouterLink} to="/register" underline="hover" sx={{ color: '#667eea', fontWeight: 600 }}>
            Sign up here
          </Link>
        </Typography>
        <Typography variant="caption" sx={{ color: 'rgba(0,0,0,0.4)', display: 'block' }}>
          Demo: Use username "user1" with password "password1"
        </Typography>
      </Box>
    </Box>
  );
};

export default Login;