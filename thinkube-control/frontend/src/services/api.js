// src/services/api.js
import axios from 'axios';
import { getToken } from './auth';

// Base URL for API requests
const API_URL = '/api/v1';

// Setup axios defaults
axios.defaults.baseURL = API_URL;

// Add a request interceptor to include the auth token
axios.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // For auth errors, let the auth service handle them
    // Don't redirect here as we're using direct Keycloak auth
    return Promise.reject(error);
  }
);

/**
 * Get all available dashboards
 */
export const getDashboards = async () => {
  try {
    const response = await axios.get('/dashboards/');
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
    const response = await axios.get('/dashboards/categories/');
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
    const response = await axios.get(`/dashboards/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get dashboard with ID ${id}`, error);
    throw error;
  }
};