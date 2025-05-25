<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <div class="card w-full max-w-2xl bg-base-100 shadow-xl">
      <div class="card-body text-center">
        <div class="flex justify-center mb-6">
          <img src="/logo.svg" alt="thinkube" class="w-20 h-20" />
        </div>
        
        <h1 class="text-4xl font-bold mb-4">Welcome to thinkube</h1>
        <p class="text-lg text-base-content/70 mb-8">
          Let's set up your AI-focused Kubernetes homelab platform
        </p>
        
        <div class="alert alert-info mb-8">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>This installer will guide you through configuring and deploying thinkube on your Ubuntu systems.</span>
        </div>

        <div class="space-y-4 text-left mb-8">
          <div class="flex items-center gap-3">
            <svg class="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>System requirements check</span>
          </div>
          <div class="flex items-center gap-3">
            <svg class="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>Cluster configuration</span>
          </div>
          <div class="flex items-center gap-3">
            <svg class="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>Automated deployment</span>
          </div>
        </div>

        <div class="card-actions justify-center">
          <button class="btn btn-primary btn-lg gap-2" @click="$router.push('/requirements')">
            Get Started
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 🤖 AI-generated
</script>