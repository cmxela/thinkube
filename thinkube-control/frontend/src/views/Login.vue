<!-- src/views/Login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-96 bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-center justify-center mb-4">K8s Dashboard Hub</h2>
        <p class="text-center mb-6">Please sign in to access the dashboard</p>
        
        <div v-if="loading" class="flex justify-center mb-4">
          <span class="loading loading-spinner loading-md"></span>
        </div>
        
        <div v-if="error" class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>
        
        <div class="card-actions justify-center">
          <button 
            class="btn btn-primary w-full" 
            @click="login"
            :disabled="loading"
          >
            Sign in with Keycloak
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { login } from '@/services/auth';

export default {
  name: 'LoginView',
  data() {
    return {
      loading: false,
      error: false,
      errorMessage: ''
    };
  },
  methods: {
    async login() {
      this.loading = true;
      this.error = false;
      
      try {
        await login(window.location.origin + '/dashboard');
        // Successful login redirects to dashboard
      } catch (error) {
        this.error = true;
        this.errorMessage = error.message || 'Failed to login. Please try again.';
        this.loading = false;
      }
    }
  }
}
</script>