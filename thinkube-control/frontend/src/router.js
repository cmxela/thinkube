// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated, redirectToLogin } from './services/auth';

// Import views
import Dashboard from './views/Dashboard.vue';
import NotFound from './views/NotFound.vue';
import AuthCallback from './views/AuthCallback.vue';

// Define routes
const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/dashboard'
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: AuthCallback,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: { requiresAuth: false }
  }
];

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to check authentication
router.beforeEach(async (to, from, next) => {
  console.log('Navigating to:', to.path, 'Requires auth:', to.meta.requiresAuth);
  
  // Skip auth check for routes that don't require it
  if (to.meta.requiresAuth === false) {
    next();
    return;
  }
  
  // Check if user is authenticated
  const authenticated = isAuthenticated();
  console.log('Is authenticated:', authenticated);
  
  if (!authenticated) {
    console.log('Not authenticated, redirecting to login');
    // Redirect to Keycloak login
    await redirectToLogin();
    return;
  }
  
  console.log('Authenticated, proceeding to route');
  next();
});

export default router;