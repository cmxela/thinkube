// src/services/auth.js
import axios from 'axios';

// Token storage keys
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRY_KEY = 'token_expiry';

/**
 * Store authentication tokens
 */
const storeTokens = (tokens) => {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  if (tokens.refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  }
  // Calculate and store token expiry time
  const expiryTime = new Date().getTime() + (tokens.expires_in * 1000);
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
};

/**
 * Clear stored tokens
 */
const clearTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
};

/**
 * Get stored access token
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Check if token is expired
 */
const isTokenExpired = () => {
  const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiryTime) return true;
  return new Date().getTime() > parseInt(expiryTime);
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
 * Build authorization URL for Keycloak login
 */
export const getAuthorizationUrl = async () => {
  const config = await getAuthConfig();
  const params = new URLSearchParams({
    client_id: config.client_id,
    redirect_uri: `${window.location.origin}/auth/callback`,
    response_type: 'code',
    scope: 'openid profile email'
  });
  
  return `${config.auth_url}?${params.toString()}`;
};

/**
 * Handle OAuth2 callback - exchange code for token
 */
export const handleAuthCallback = async (code) => {
  try {
    const response = await axios.post('/api/v1/auth/token', {
      code,
      redirect_uri: `${window.location.origin}/auth/callback`
    });
    
    storeTokens(response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to exchange code for token', error);
    throw error;
  }
};

/**
 * Get user information from backend
 */
export const getUserInfo = async () => {
  try {
    const token = getToken();
    if (!token) {
      throw new Error('No access token available');
    }
    
    const response = await axios.get('/api/v1/auth/user-info', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('User info response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get user info', error);
    // If unauthorized, clear tokens and redirect to login
    if (error.response && error.response.status === 401) {
      clearTokens();
      await redirectToLogin();
    }
    throw error;
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
 * Redirect to Keycloak login
 */
export const redirectToLogin = async () => {
  const authUrl = await getAuthorizationUrl();
  window.location.href = authUrl;
};

/**
 * Log out the user
 */
export const logout = async () => {
  clearTokens();
  
  try {
    const config = await getAuthConfig();
    const logoutUrl = `${config.logout_url}?redirect_uri=${encodeURIComponent(window.location.origin)}`;
    window.location.href = logoutUrl;
  } catch (error) {
    // If we can't get config, just redirect to home
    window.location.href = '/';
  }
};

/**
 * Check authentication status
 */
export const isAuthenticated = () => {
  const token = getToken();
  return token && !isTokenExpired();
};

/**
 * Refresh access token using refresh token
 */
export const refreshToken = async () => {
  const refreshTokenValue = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshTokenValue) {
    throw new Error('No refresh token available');
  }
  
  try {
    const response = await axios.post('/api/v1/auth/refresh-token', {
      refresh_token: refreshTokenValue
    });
    
    storeTokens(response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to refresh token', error);
    clearTokens();
    throw error;
  }
};

/**
 * Setup axios interceptor to add auth token to requests
 */
export const setupAxiosInterceptors = () => {
  // Request interceptor to add token
  axios.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token && !config.url.includes('/auth/')) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Response interceptor to handle 401 errors
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          await refreshToken();
          const token = getToken();
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return axios(originalRequest);
        } catch (refreshError) {
          await redirectToLogin();
          return Promise.reject(refreshError);
        }
      }
      
      return Promise.reject(error);
    }
  );
};

// Initialize interceptors
setupAxiosInterceptors();