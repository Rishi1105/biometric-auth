/**
 * Authentication Service
 * Handles user authentication, biometric verification, and token management
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

class AuthService {
  /**
   * Authenticate user with username and password
   * @param {string} username - User's username
   * @param {string} password - User's password
   * @returns {Promise<Object>} - Authentication response with token and userId
   */
  async login(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Network error' }));
        throw new Error(errorData.message || 'Authentication failed');
      }

      const data = await response.json();
      
      // Store token and userId immediately upon successful login
      if (data.token && data.userId) {
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('userId', data.userId);
      }
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      // Provide more user-friendly error messages
      if (error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw error;
    }
  }

  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} - Registration response
   */
  async register(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Network error' }));
        throw new Error(errorData.message || 'Registration failed');
      }

      const data = await response.json();
      
      // Store token and userId immediately upon successful registration
      if (data.token && data.userId) {
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('userId', data.userId);
      }
      
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      // Provide more user-friendly error messages
      if (error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw error;
    }
  }

  /**
   * Verify user's biometric data
   * @param {string} userId - User ID
   * @param {string} token - Authentication token
   * @param {string} biometricType - Type of biometric (face, fingerprint, voice)
   * @param {string} biometricData - Base64 encoded biometric data
   * @returns {Promise<Object>} - Verification response
   */
  async verifyBiometric(userId, token, biometricType, biometricData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-biometric`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          userId,
          biometricType,
          biometricData,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Network error' }));
        throw new Error(errorData.message || 'Biometric verification failed');
      }

      const data = await response.json();
      
      // Update token if a new one is provided
      if (data.token) {
        localStorage.setItem('authToken', data.token);
      }
      
      return data;
    } catch (error) {
      console.error('Biometric verification error:', error);
      if (error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check your connection.');
      }
      throw error;
    }
  }

  /**
   * Enroll user's biometric data
   * @param {string} userId - User ID
   * @param {string} token - Authentication token
   * @param {string} biometricType - Type of biometric (face, fingerprint, voice)
   * @param {string} biometricData - Base64 encoded biometric data
   * @returns {Promise<Object>} - Enrollment response
   */
  async enrollBiometric(userId, token, biometricType, biometricData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/enroll-biometric`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          userId,
          biometricType,
          biometricData,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Biometric enrollment failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Biometric enrollment error:', error);
      throw error;
    }
  }

  /**
   * Logout the current user
   */
  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    window.location.href = '/login';
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} - True if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }

  /**
   * Get current user's authentication token
   * @returns {string|null} - Authentication token or null if not authenticated
   */
  getToken() {
    return localStorage.getItem('authToken');
  }

  /**
   * Get current user's ID
   * @returns {string|null} - User ID or null if not authenticated
   */
  getUserId() {
    return localStorage.getItem('userId');
  }
}

export const authService = new AuthService();