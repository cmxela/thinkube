// src/services/auth.js
import axios from 'axios';

/**
 * Get user information from backend
 * (The backend gets this from OAuth2 Proxy headers)
 */
export const getUserInfo = async () => {
  try {
    console.log('Fetching user info from backend');
    const response = await axios.get('/api/v1/auth/user-info');
    console.log('User info response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get user info', error);
    // Return a default user in case of error for UI to display something
    return {
      preferred_username: 'Default User',
      email: 'default@example.com',
      name: 'Default User',
      roles: ['dashboard-user']
    };
  }
};

/**
 * Check if user has a specific role
 */
export const hasRole = (userInfo, role) => {
  if (!userInfo || !userInfo.roles) {
    return false;
  }
  
  return userInfo.roles.includes(role);
};

/**
 * Log out the user by redirecting to OAuth2 Proxy logout
 */
export const logout = () => {
  // Redirect to OAuth2 Proxy logout endpoint
  window.location.href = '/oauth2/sign_out';
};

/**
 * Check authentication status
 * With OAuth2 Proxy, if we can access the page, we're already authenticated
 */
export const isAuthenticated = () => {
  // With OAuth2 Proxy, if we're on the page, we're authenticated
  return true;
};

/**
 * Get authentication configuration from backend
 */
export const getAuthConfig = async () => {
  try {
    const response = await axios.get('/api/v1/auth/auth-config');
    return response.data;
  } catch (error) {
    console.error('Failed to get auth config', error);
    throw error;
  }
};

/**
 * Get the access token from OAuth2 Proxy
 * This is a stub function since we're no longer managing tokens directly
 * but api.js still imports this function
 */
export const getToken = () => {
  // We don't manage tokens directly anymore with OAuth2 Proxy
  return null;
};