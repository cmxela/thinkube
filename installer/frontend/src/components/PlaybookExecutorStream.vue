<template>
  <div class="playbook-executor">
    <!-- Progress Modal -->
    <div v-if="isExecuting" class="modal modal-open">
      <div class="modal-box max-w-4xl max-h-[90vh]">
        <h3 class="font-bold text-lg mb-4">{{ title }}</h3>
        
        <!-- Task Progress -->
        <div v-if="currentTask" class="mb-4">
          <div class="flex justify-between text-sm mb-1">
            <span class="font-semibold">{{ currentTask }}</span>
            <span v-if="taskCount > 0" class="text-sm text-base-content/70">
              Task {{ taskCount }}
            </span>
          </div>
        </div>
        
        <!-- Live Output Log -->
        <div class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-gray-600">Live Output:</span>
            <div class="flex items-center gap-2">
              <button 
                class="btn btn-ghost btn-xs gap-1"
                @click="copyOutput"
                :class="{ 'btn-success': copySuccess }"
              >
                <svg v-if="!copySuccess" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                {{ copySuccess ? 'Copied!' : 'Copy' }}
              </button>
              <label class="label cursor-pointer gap-2">
                <span class="label-text text-xs">Auto-scroll</span>
                <input type="checkbox" v-model="autoScroll" class="checkbox checkbox-xs" />
              </label>
            </div>
          </div>
          <div 
            class="bg-gray-900 text-gray-100 rounded p-4 h-96 overflow-y-auto font-mono text-xs leading-relaxed"
            ref="logContainer"
          >
            <div v-if="logOutput.length === 0" class="text-gray-500">
              Waiting for output...
            </div>
            <div 
              v-for="(log, idx) in logOutput" 
              :key="idx" 
              :class="getLogClass(log.type)"
              class="whitespace-pre-wrap"
            >{{ log.message }}</div>
          </div>
        </div>
        
        <!-- Status Summary -->
        <div v-if="taskSummary.total > 0" class="stats stats-horizontal w-full mb-4">
          <div class="stat place-items-center py-2">
            <div class="stat-title text-xs">Tasks</div>
            <div class="stat-value text-lg">{{ taskSummary.total }}</div>
          </div>
          <div class="stat place-items-center py-2">
            <div class="stat-title text-xs">OK</div>
            <div class="stat-value text-lg text-success">{{ taskSummary.ok }}</div>
          </div>
          <div class="stat place-items-center py-2">
            <div class="stat-title text-xs">Changed</div>
            <div class="stat-value text-lg text-warning">{{ taskSummary.changed }}</div>
          </div>
          <div v-if="taskSummary.failed > 0" class="stat place-items-center py-2">
            <div class="stat-title text-xs">Failed</div>
            <div class="stat-value text-lg text-error">{{ taskSummary.failed }}</div>
          </div>
        </div>
        
        <!-- Cancel Button (only during execution) -->
        <div v-if="status === 'running'" class="modal-action">
          <button class="btn btn-outline btn-sm" @click="cancelExecution" :disabled="isCancelling">
            <span v-if="isCancelling" class="loading loading-spinner loading-xs"></span>
            {{ isCancelling ? 'Cancelling...' : 'Cancel' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Result Modal -->
    <div v-if="showResult" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="font-bold text-lg mb-4">{{ title }} - Complete</h3>
        
        <!-- Success Result -->
        <div v-if="status === 'success'" class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ message || 'Playbook completed successfully' }}</span>
        </div>
        
        <!-- Error Result -->
        <div v-if="status === 'error'">
          <div class="alert alert-error mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ message || 'Playbook execution failed' }}</span>
          </div>
          
          <!-- GitHub Issue Helper -->
          <div class="alert alert-info mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <p class="font-semibold">Need help?</p>
              <p class="text-sm">Copy the log output and create an issue on GitHub for assistance.</p>
            </div>
          </div>
        </div>
        
        <!-- Final Summary -->
        <div v-if="taskSummary.totalTasks > 0" class="mb-4">
          <p class="text-sm text-gray-600 mb-2">Execution Summary:</p>
          <div class="text-sm">
            <p>Total Tasks: {{ taskSummary.totalTasks }}</p>
            <p class="text-success">Completed: {{ taskSummary.completedTasks }}</p>
            <p v-if="taskSummary.failedTasks > 0" class="text-error">Failed: {{ taskSummary.failedTasks }}</p>
          </div>
        </div>
        
        <!-- Execution Time -->
        <div v-if="duration" class="mb-4">
          <div class="text-sm text-gray-600">
            Completed in {{ formatDuration(duration) }}
          </div>
        </div>
        
        <!-- Actions -->
        <div class="modal-action">
          <button 
            class="btn btn-ghost btn-sm gap-1"
            @click="copyOutput"
            :class="{ 'btn-success': copySuccess }"
          >
            <svg v-if="!copySuccess" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            {{ copySuccess ? 'Copied!' : 'Copy Log' }}
          </button>
          <button class="btn btn-primary" @click="closeResult">
            {{ status === 'success' ? 'Continue' : 'Close' }}
          </button>
          <button v-if="status === 'error' && onRetry" class="btn btn-outline" @click="retry">
            Retry
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

interface PlaybookExecutorProps {
  title: string
  playbookName: string
  onRetry?: () => void
  onComplete?: (result: any) => void
}

interface LogEntry {
  type: 'start' | 'play' | 'task' | 'ok' | 'changed' | 'failed' | 'output' | 'error' | 'complete'
  message: string
  task?: string
  task_number?: number
}

const props = defineProps<PlaybookExecutorProps>()
const emit = defineEmits(['complete', 'continue'])

// Reactive state
const isExecuting = ref(false)
const showResult = ref(false)
const status = ref<'pending' | 'running' | 'success' | 'error' | 'cancelled'>('pending')
const message = ref('')
const currentTask = ref('')
const taskCount = ref(0)
const duration = ref<number | null>(null)
const isCancelling = ref(false)
const logOutput = ref<LogEntry[]>([])
const logContainer = ref<HTMLElement>()
const autoScroll = ref(true)
const websocket = ref<WebSocket | null>(null)
const startTime = ref<number>(0)
const copySuccess = ref(false)

// Task summary - track unique tasks rather than host executions
const taskSummary = ref({
  totalTasks: 0,
  completedTasks: 0,
  failedTasks: 0
})
const seenTasks = ref(new Set())

// Methods
const startExecution = (params: any = {}) => {
  isExecuting.value = true
  showResult.value = false
  status.value = 'running'
  message.value = ''
  currentTask.value = 'Connecting...'
  taskCount.value = 0
  duration.value = null
  isCancelling.value = false
  logOutput.value = []
  taskSummary.value = { totalTasks: 0, completedTasks: 0, failedTasks: 0 }
  seenTasks.value = new Set()
  startTime.value = Date.now()
  
  // Connect WebSocket
  connectWebSocket(params)
}

const connectWebSocket = (params: any) => {
  const encodedPlaybookName = encodeURIComponent(props.playbookName)
  const wsUrl = `ws://localhost:8000/ws/playbook/${encodedPlaybookName}`
  websocket.value = new WebSocket(wsUrl)
  
  websocket.value.onopen = async () => {
    console.log('WebSocket connected')
    
    let inventoryYAML = ''
    
    // Check if this is SSH-related playbook - use minimal inventory
    if (props.playbookName === 'setup-ssh-keys' || props.playbookName === 'test-ssh-connectivity') {
      const { generateMinimalInventory, minimalInventoryToYAML } = await import('../utils/minimalInventory.js')
      const minimalInventory = generateMinimalInventory()
      inventoryYAML = minimalInventoryToYAML(minimalInventory)
    } else {
      // Use full inventory for other playbooks
      const { generateDynamicInventory, inventoryToYAML } = await import('../utils/inventoryGenerator.js')
      const dynamicInventory = generateDynamicInventory()
      inventoryYAML = inventoryToYAML(dynamicInventory)
    }
    
    // Add inventory to parameters
    const paramsWithInventory = {
      ...params,
      inventory: inventoryYAML
    }
    
    // Add ZeroTier-specific environment variables if this is a ZeroTier playbook
    if (props.playbookName.includes('zerotier')) {
      const zerotierApiToken = sessionStorage.getItem('zerotierApiToken')
      const zerotierNetworkId = sessionStorage.getItem('zerotierNetworkId')
      
      if (zerotierApiToken || zerotierNetworkId) {
        paramsWithInventory.environment = {
          ...paramsWithInventory.environment
        }
        
        if (zerotierApiToken) {
          paramsWithInventory.environment.ZEROTIER_API_TOKEN = zerotierApiToken
        }
        if (zerotierNetworkId) {
          paramsWithInventory.environment.ZEROTIER_NETWORK_ID = zerotierNetworkId
        }
      }
    }
    
    // Add Cloudflare token if needed
    if (props.playbookName.includes('cert-manager') || props.playbookName.includes('dns')) {
      const cloudflareToken = sessionStorage.getItem('cloudflareToken')
      if (cloudflareToken) {
        paramsWithInventory.environment = {
          ...paramsWithInventory.environment,
          CLOUDFLARE_TOKEN: cloudflareToken
        }
      }
    }
    
    // Add GitHub token if needed
    if (props.playbookName.includes('github') || props.playbookName.includes('devpi')) {
      const githubToken = sessionStorage.getItem('githubToken')
      if (githubToken) {
        paramsWithInventory.environment = {
          ...paramsWithInventory.environment,
          GITHUB_TOKEN: githubToken
        }
      }
    }
    
    // Send execution parameters with dynamic inventory
    websocket.value?.send(JSON.stringify(paramsWithInventory))
  }
  
  websocket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWebSocketMessage(data)
  }
  
  websocket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    logOutput.value.push({
      type: 'error',
      message: 'Connection error occurred'
    })
  }
  
  websocket.value.onclose = () => {
    console.log('WebSocket disconnected')
    if (status.value === 'running') {
      status.value = 'error'
      message.value = 'Connection lost'
      completeExecution({
        status: 'error',
        message: 'Connection to server lost'
      })
    }
  }
}

const handleWebSocketMessage = (data: any) => {
  // Add to log
  logOutput.value.push({
    type: data.type,
    message: data.message,
    task: data.task,
    task_number: data.task_number
  })
  
  // Auto-scroll to bottom
  if (autoScroll.value) {
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })
  }
  
  // Handle different message types
  switch (data.type) {
    case 'start':
      currentTask.value = 'Starting playbook execution...'
      break
      
    case 'task':
      currentTask.value = data.task_name
      taskCount.value = data.task_number
      
      // Track unique tasks only
      if (data.task_name && !seenTasks.value.has(data.task_name)) {
        seenTasks.value.add(data.task_name)
        taskSummary.value.totalTasks++
      }
      break
      
    case 'ok':
    case 'changed':
      // Mark task as completed (count unique tasks, not individual host results)
      if (data.task && !seenTasks.value.has(data.task + '_completed')) {
        seenTasks.value.add(data.task + '_completed')
        taskSummary.value.completedTasks++
      }
      break
      
    case 'failed':
      // Mark task as failed
      if (data.task && !seenTasks.value.has(data.task + '_failed')) {
        seenTasks.value.add(data.task + '_failed')
        taskSummary.value.failedTasks++
      }
      break
      
    case 'complete':
      duration.value = (Date.now() - startTime.value) / 1000
      status.value = data.status
      message.value = data.message
      completeExecution({
        status: data.status,
        message: data.message,
        duration: duration.value
      })
      break
      
    case 'error':
      status.value = 'error'
      message.value = data.message
      break
  }
}

const completeExecution = (result: any) => {
  isExecuting.value = false
  showResult.value = true
  websocket.value?.close()
  websocket.value = null
  
  // Emit completion event
  emit('complete', result)
  
  // Call onComplete prop if provided
  if (props.onComplete) {
    props.onComplete(result)
  }
}

const cancelExecution = () => {
  isCancelling.value = true
  websocket.value?.close()
  status.value = 'cancelled'
  message.value = 'Execution was cancelled'
  isExecuting.value = false
  showResult.value = true
  isCancelling.value = false
  
  // Emit completion event with cancelled status
  const result = {
    status: 'cancelled',
    message: 'Execution was cancelled by user',
    duration: duration.value
  }
  emit('complete', result)
  
  // Call onComplete prop if provided
  if (props.onComplete) {
    props.onComplete(result)
  }
}

const closeResult = () => {
  showResult.value = false
  
  // Only emit continue if the playbook was successful
  if (status.value === 'success') {
    emit('continue')
  }
  
  // Reset state
  status.value = 'pending'
  message.value = ''
  currentTask.value = ''
  taskCount.value = 0
  duration.value = null
  logOutput.value = []
  taskSummary.value = { totalTasks: 0, completedTasks: 0, failedTasks: 0 }
  seenTasks.value = new Set()
}

const retry = () => {
  if (props.onRetry) {
    // Close the result modal without emitting continue
    showResult.value = false
    
    // Reset state
    status.value = 'pending'
    message.value = ''
    currentTask.value = ''
    taskCount.value = 0
    duration.value = null
    logOutput.value = []
    taskSummary.value = { totalTasks: 0, completedTasks: 0, failedTasks: 0 }
    seenTasks.value = new Set()
    
    // Call the retry handler
    props.onRetry()
  }
}

const copyOutput = async () => {
  try {
    // Build the output text with metadata
    const header = `Thinkube Installer - Playbook Execution Log
=====================================
Playbook: ${props.playbookName}
Title: ${props.title}
Status: ${status.value}
Duration: ${duration.value ? formatDuration(duration.value) : 'N/A'}
Tasks: Total ${taskSummary.value.total}, OK ${taskSummary.value.ok}, Changed ${taskSummary.value.changed}, Failed ${taskSummary.value.failed}
Timestamp: ${new Date().toISOString()}
=====================================

`
    
    // Combine all log messages
    const logText = logOutput.value
      .map(log => log.message)
      .join('\n')
    
    const fullText = header + logText
    
    // Copy to clipboard
    await navigator.clipboard.writeText(fullText)
    
    // Show success feedback
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy output:', err)
    alert('Failed to copy output to clipboard')
  }
}

const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds.toFixed(1)} seconds`
  } else {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }
}

const getLogClass = (type: string): string => {
  switch (type) {
    case 'task':
      return 'text-blue-400 font-semibold mt-2'
    case 'play':
      return 'text-purple-400 font-semibold mt-3'
    case 'ok':
      return 'text-green-400'
    case 'changed':
      return 'text-yellow-400'
    case 'failed':
      return 'text-red-400 font-semibold'
    case 'error':
      return 'text-red-500 font-semibold'
    case 'start':
    case 'complete':
      return 'text-gray-300 font-semibold'
    default:
      return 'text-gray-400'
  }
}

// Expose methods to parent component
defineExpose({
  startExecution,
  completeExecution,
  cancelExecution
})
</script>

<style scoped>
/* Custom scrollbar for log container */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Terminal-like appearance */
.bg-gray-900 {
  background-color: #1a1a1a;
}
</style>