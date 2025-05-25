<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Deploying Thinkube</h1>
    
    <!-- Deployment Progress -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <div class="text-center mb-6">
          <div class="radial-progress text-primary" 
               :style="`--value:${progress}; --size:12rem; --thickness:1rem;`">
            <span class="text-4xl font-bold progress-text">{{ progress }}%</span>
          </div>
        </div>
        
        <div class="flex justify-center gap-2 mb-4">
          <div class="badge" :class="getPhaseClass(phase)">
            {{ phase }}
          </div>
        </div>
        
        <p class="text-center text-lg mb-4">{{ currentTask }}</p>
        
        <progress class="progress progress-primary w-full" :value="progress" max="100"></progress>
      </div>
    </div>
    
    <!-- Deployment Logs -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <div class="flex items-center justify-between mb-4">
          <h2 class="card-title">Deployment Logs</h2>
          <button 
            class="btn btn-ghost btn-sm btn-circle"
            @click="autoScroll = !autoScroll"
            :class="{ 'btn-active': autoScroll }"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    :d="autoScroll ? 'M19 14l-7 7m0 0l-7-7m7 7V3' : 'M5 10l7-7m0 0l7 7m-7-7v18'"></path>
            </svg>
          </button>
        </div>
        
        <div ref="logContainer" class="log-container bg-base-200 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
          <div v-for="(log, index) in logs" :key="index" class="mb-1">
            <span class="text-base-content/60">{{ formatTime(log.timestamp) }}</span>
            <span class="ml-2" :class="getLogClass(log.level)">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Completion Actions -->
    <div v-if="isComplete" class="mt-6">
      <div v-if="phase === 'failed'" class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Deployment failed. Please check the logs for details.</span>
      </div>
      
      <button 
        class="btn btn-primary btn-block btn-lg gap-2"
        @click="$router.push('/complete')"
      >
        View Cluster Details
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const progress = ref(0)
const phase = ref('initializing')
const currentTask = ref('Preparing deployment...')
const logs = ref([])
const logContainer = ref(null)
const autoScroll = ref(true)

// Computed
const isComplete = computed(() => {
  return phase.value === 'completed' || phase.value === 'failed'
})

// Get phase badge class
const getPhaseClass = (phase) => {
  switch (phase) {
    case 'initializing': return 'badge-info'
    case 'infrastructure': return 'badge-warning'
    case 'kubernetes': return 'badge-primary'
    case 'services': return 'badge-secondary'
    case 'completed': return 'badge-success'
    case 'failed': return 'badge-error'
    default: return 'badge-ghost'
  }
}

// Get log message class
const getLogClass = (level) => {
  switch (level) {
    case 'error': return 'text-error'
    case 'warning': return 'text-warning'
    case 'success': return 'text-success'
    case 'info': return 'text-info'
    default: return ''
  }
}

// Format timestamp
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toTimeString().split(' ')[0]
}

// Add log entry
const addLog = (message, level = 'info') => {
  logs.value.push({
    timestamp: new Date(),
    message,
    level
  })
}

// Simulate deployment
const simulateDeployment = async () => {
  // Phase 1: Infrastructure
  phase.value = 'infrastructure'
  addLog('Starting infrastructure setup...')
  
  const tasks = [
    { msg: 'Setting up SSH keys between servers', progress: 10 },
    { msg: 'Configuring network bridges', progress: 20 },
    { msg: 'Setting up LXD cluster', progress: 30 },
    { msg: 'Creating virtual machines', progress: 40 },
    { msg: 'Configuring ZeroTier overlay network', progress: 50 }
  ]
  
  for (const task of tasks) {
    currentTask.value = task.msg
    progress.value = task.progress
    addLog(task.msg)
    await new Promise(resolve => setTimeout(resolve, 2000))
  }
  
  // Phase 2: Kubernetes
  phase.value = 'kubernetes'
  addLog('Starting Kubernetes installation...', 'info')
  
  const k8sTasks = [
    { msg: 'Installing MicroK8s on control plane', progress: 60 },
    { msg: 'Joining worker nodes to cluster', progress: 70 },
    { msg: 'Installing GPU operator', progress: 75 },
    { msg: 'Configuring ingress controller', progress: 80 }
  ]
  
  for (const task of k8sTasks) {
    currentTask.value = task.msg
    progress.value = task.progress
    addLog(task.msg)
    await new Promise(resolve => setTimeout(resolve, 2000))
  }
  
  // Phase 3: Services
  phase.value = 'services'
  addLog('Installing Thinkube services...', 'info')
  
  const serviceTasks = [
    { msg: 'Deploying Keycloak for authentication', progress: 85 },
    { msg: 'Setting up Harbor registry', progress: 90 },
    { msg: 'Installing ArgoCD for GitOps', progress: 95 },
    { msg: 'Configuring DNS and certificates', progress: 99 }
  ]
  
  for (const task of serviceTasks) {
    currentTask.value = task.msg
    progress.value = task.progress
    addLog(task.msg)
    await new Promise(resolve => setTimeout(resolve, 1500))
  }
  
  // Complete
  phase.value = 'completed'
  progress.value = 100
  currentTask.value = 'Deployment completed successfully!'
  addLog('Thinkube cluster deployed successfully!', 'success')
}

// Auto-scroll logs
watch(() => logs.value.length, async () => {
  if (autoScroll.value && logContainer.value) {
    await nextTick()
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})

// Start deployment
onMounted(() => {
  // In real implementation, this would connect to WebSocket
  // and monitor actual ansible playbook execution
  simulateDeployment()
})
</script>

<style scoped>
.progress-text {
  animation: fade-pulse 1.5s ease-in-out infinite;
}

@keyframes fade-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.log-container {
  font-family: 'Courier New', monospace;
}
</style>