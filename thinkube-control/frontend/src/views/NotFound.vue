<!-- src/views/NotFound.vue -->
<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-base-200 p-4">
    <div class="text-9xl font-bold text-primary mb-4">404</div>
    <h1 class="text-2xl font-bold mb-4">Page Not Found</h1>
    <p class="text-center mb-6">The page you're looking for doesn't exist or has been moved.</p>
    
    <router-link to="/" class="btn btn-primary">
      Return to Dashboard
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>