// src/router.js
import { createRouter, createWebHistory } from 'vue-router';

// Import views
import Dashboard from './views/Dashboard.vue';
import NotFound from './views/NotFound.vue';

// Define routes
const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard
    // No auth check needed - OAuth2 Proxy handles this
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound
  }
];

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes
});

// No auth check needed in router - OAuth2 Proxy handles authentication

export default router;