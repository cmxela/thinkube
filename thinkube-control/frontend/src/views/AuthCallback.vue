<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
      <p class="text-gray-600">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { handleAuthCallback } from '@/services/auth';

export default {
  name: 'AuthCallback',
  data() {
    return {
      message: 'Completing authentication...'
    };
  },
  async mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');
    
    if (error) {
      this.message = `Authentication failed: ${error}`;
      setTimeout(() => {
        this.$router.push('/');
      }, 3000);
      return;
    }
    
    if (!code) {
      this.message = 'No authorization code received';
      setTimeout(() => {
        this.$router.push('/');
      }, 3000);
      return;
    }
    
    try {
      await handleAuthCallback(code);
      this.message = 'Authentication successful. Redirecting to dashboard...';
      // Small delay to ensure token is properly stored
      setTimeout(() => {
        // Redirect to dashboard after successful authentication
        this.$router.push('/dashboard');
      }, 100);
    } catch (error) {
      console.error('Auth callback failed:', error);
      this.message = 'Authentication failed. Redirecting...';
      setTimeout(() => {
        this.$router.push('/');
      }, 3000);
    }
  }
};
</script>