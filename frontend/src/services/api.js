// src/services/api.js
import axios from 'axios';

// Base URL for API requests
const API_URL = '/api/v1';

// Setup axios defaults
axios.defaults.baseURL = API_URL;

// With OAuth2 Proxy we don't need to set auth headers manually
// as the proxy will handle this for us

// Add a response interceptor to handle errors
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401/403 errors (should be rare with OAuth2 Proxy)
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // Redirect to OAuth2 Proxy auth
      window.location.href = '/oauth2/start?rd=' + encodeURIComponent(window.location.pathname);
    }
    return Promise.reject(error);
  }
);

/**
 * Get all available dashboards
 */
export const getDashboards = async () => {
  try {
    const response = await axios.get('/dashboards/dashboards');
    return response.data;
  } catch (error) {
    console.error('Failed to get dashboards', error);
    throw error;
  }
};

/**
 * Get dashboard categories
 */
export const getDashboardCategories = async () => {
  try {
    const response = await axios.get('/dashboards/dashboards/categories');
    return response.data.categories;
  } catch (error) {
    console.error('Failed to get dashboard categories', error);
    throw error;
  }
};

/**
 * Get a specific dashboard by ID
 */
export const getDashboard = async (id) => {
  try {
    const response = await axios.get(`/dashboards/dashboards/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get dashboard with ID ${id}`, error);
    throw error;
  }
};