<template>
  <div class="navbar bg-base-100 shadow-lg mb-6">
    <div class="navbar-start">
      <div class="flex items-center gap-4">
        <img src="/logo.svg" alt="Thinkube" class="h-8 w-8" />
        <h1 class="text-xl font-bold">Thinkube Installer</h1>
      </div>
    </div>
    
    <div class="navbar-center">
      <!-- Progress indicator -->
      <div v-if="currentStep" class="text-sm text-base-content/70">
        Step {{ currentStepIndex + 1 }} of {{ totalSteps }}
      </div>
    </div>
    
    <div class="navbar-end">
      <!-- Start Over button (only show after first step) -->
      <button 
        v-if="showStartOver"
        class="btn btn-ghost btn-sm gap-2"
        @click="confirmStartOver"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Start Over
      </button>
    </div>
    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Start Over?</h3>
        <p class="py-4">
          This will reset all installation progress and return to the welcome screen.
        </p>
        <div class="alert alert-warning mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>All configuration and progress will be lost!</span>
        </div>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="showConfirmModal = false">Cancel</button>
          <button class="btn btn-error" @click="startOver">Yes, Start Over</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { clearAllCheckpoints } from '@/utils/installerState'

const router = useRouter()
const route = useRoute()

const showConfirmModal = ref(false)

// Step order for progress tracking
const stepOrder = [
  'welcome',
  'requirements', 
  'sudo-password',
  'installation',
  'server-discovery',
  'ssh-setup',
  'hardware-detection',
  'vm-planning',
  'role-assignment',
  'configuration',
  'network-configuration',
  'gpu-assignment',
  'review',
  'deploy',
  'complete'
]

// Computed properties
const currentStep = computed(() => route.name)

const currentStepIndex = computed(() => {
  return stepOrder.indexOf(route.name) || 0
})

const totalSteps = computed(() => stepOrder.length - 2) // Exclude welcome and complete

const showStartOver = computed(() => {
  // Show after welcome screen
  return currentStepIndex.value > 0 && currentStepIndex.value < stepOrder.length - 1
})

// Methods
const confirmStartOver = () => {
  showConfirmModal.value = true
}

const startOver = () => {
  // Clear all stored state
  clearAllCheckpoints()
  
  // Close modal
  showConfirmModal.value = false
  
  // Navigate to welcome
  router.push('/')
}
</script>