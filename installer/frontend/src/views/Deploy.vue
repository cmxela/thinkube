<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Deploying Thinkube Infrastructure</h1>
      <button 
        class="btn btn-ghost btn-sm gap-2" 
        @click="resetDeployment"
        title="Clear deployment state and start over"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Reset
      </button>
    </div>
    
    <!-- Deployment Progress Overview -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Deployment Progress</h2>
        
        <!-- Phase Indicators -->
        <div class="flex flex-wrap gap-2 mb-6">
          <div v-for="(phase, index) in deploymentPhases" :key="phase.id"
               class="badge gap-2"
               :class="getPhaseClass(phase)">
            <svg v-if="phase.status === 'completed'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <svg v-else-if="phase.status === 'active'" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ phase.name }}
          </div>
        </div>
        
        <progress class="progress progress-primary w-full" :value="overallProgress" max="100"></progress>
        <p class="text-sm text-center mt-2">{{ overallProgress }}% Complete</p>
      </div>
    </div>
    
    <!-- Current Playbook Execution -->
    <div v-if="currentPlaybook">
      <PlaybookExecutorStream 
        ref="currentPlaybookExecutor"
        :key="currentPlaybook.id"
        :title="currentPlaybook.title"
        :playbook-name="currentPlaybook.name"
        :extra-vars="currentPlaybook.extraVars"
        :on-retry="retryCurrentPlaybook"
        @complete="handlePlaybookComplete"
        @continue="handlePlaybookContinue"
      />
    </div>
    
    <!-- Machine Restart Notice -->
    <div v-if="showRestartNotice" class="card bg-warning/10 border-warning mb-6">
      <div class="card-body">
        <h2 class="card-title text-warning mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          System Restart Required
        </h2>
        
        <div class="space-y-4">
          <div>
            <p class="font-semibold mb-2">The network bridge configuration requires all baremetal servers to be restarted.</p>
            <p class="text-sm text-base-content/70">Click the button below to begin the automated restart process.</p>
          </div>
          
          <div class="text-center">
            <button class="btn btn-primary btn-lg gap-2" @click="automatedRestart">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Restart All Servers
            </button>
            <p class="text-sm text-base-content/70 mt-3">
              Remote servers will restart first, followed by this server.<br/>
              The installer will automatically continue after all servers are back online.
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Completion -->
    <div v-if="deploymentComplete" class="card bg-base-100 shadow-xl">
      <div class="card-body text-center">
        <div class="text-6xl mb-4">🎉</div>
        <h2 class="card-title justify-center mb-4">Deployment Complete!</h2>
        <p class="mb-6">Your Thinkube infrastructure has been successfully deployed.</p>
        <button 
          class="btn btn-primary btn-lg gap-2"
          @click="$router.push('/complete')"
        >
          View Cluster Details
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Error State -->
    <div v-if="deploymentError" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div>
        <h3 class="font-bold">Deployment Failed</h3>
        <p>{{ deploymentError }}</p>
        <div class="flex gap-2 mt-2">
          <button class="btn btn-sm btn-outline" @click="retryDeployment">Retry</button>
          <button class="btn btn-sm btn-ghost" @click="resetDeployment">Reset & Start Over</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import PlaybookExecutorStream from '@/components/PlaybookExecutorStream.vue'
import axios from '@/utils/axios'

const router = useRouter()

// Load saved deployment state
const loadDeploymentState = () => {
  const saved = localStorage.getItem('thinkube-deployment-state')
  if (saved) {
    return JSON.parse(saved)
  }
  return null
}

// Save deployment state
const saveDeploymentState = () => {
  const state = {
    phases: deploymentPhases.value,
    queue: playbookQueue.value,
    currentPhase: currentPhase.value,
    awaitingRestart: showRestartNotice.value,
    timestamp: new Date().toISOString()
  }
  localStorage.setItem('thinkube-deployment-state', JSON.stringify(state))
}

// Clear deployment state
const clearDeploymentState = () => {
  localStorage.removeItem('thinkube-deployment-state')
}

// Deployment phases
const deploymentPhases = ref([
  { id: 'initial', name: 'Initial Setup', status: 'pending' },
  { id: 'network', name: 'Network Configuration', status: 'pending' },
  { id: 'lxd', name: 'LXD & VMs', status: 'pending' },
  { id: 'dns', name: 'DNS & Networking', status: 'pending' },
  { id: 'kubernetes', name: 'Kubernetes', status: 'pending' }
])

// Playbook queue
const playbookQueue = ref([])
const currentPlaybook = ref(null)
const currentPhase = ref(null)
const showRestartNotice = ref(false)
const deploymentComplete = ref(false)
const deploymentError = ref('')

// Progress calculation
const overallProgress = computed(() => {
  const completed = deploymentPhases.value.filter(p => p.status === 'completed').length
  const total = deploymentPhases.value.length
  return Math.round((completed / total) * 100)
})

// Get phase class for styling
const getPhaseClass = (phase) => {
  switch (phase.status) {
    case 'completed': return 'badge-success'
    case 'active': return 'badge-warning'
    case 'failed': return 'badge-error'
    default: return 'badge-ghost'
  }
}

// Build playbook queue based on deployment type
const buildPlaybookQueue = () => {
  const queue = []
  console.log('Building playbook queue...')
  
  // Phase 1: Initial Setup (00_initial_setup)
  // Skip SSH keys - already done in SSHSetup step
  queue.push({
    id: 'env-setup',
    phase: 'initial', 
    title: 'Setting up Environment',
    name: 'ansible/00_initial_setup/20_setup_env.yaml'
  })
  
  // Check if GPU reservation is needed
  const serverHardware = JSON.parse(sessionStorage.getItem('serverHardware') || '[]')
  const hasGPUs = serverHardware.some(s => s.hardware?.gpu_detected)
  if (hasGPUs) {
    queue.push({
      id: 'gpu-reservation',
      phase: 'initial',
      title: 'Reserving GPUs for Passthrough',
      name: 'ansible/00_initial_setup/30_reserve_gpus.yaml'
    })
  }
  
  queue.push({
    id: 'github-cli',
    phase: 'initial',
    title: 'Setting up GitHub CLI',
    name: 'ansible/00_initial_setup/40_setup_github_cli.yaml'
  })
  
  // Phase 2: Network Configuration (10_baremetal_infra)
  queue.push({
    id: 'network-bridge-prepare',
    phase: 'network',
    title: 'Preparing Network Bridge Configuration',
    name: 'ansible/10_baremetal_infra/10-1_configure_network_bridge_prepare.yaml'
  })
  queue.push({
    id: 'network-bridge-apply',
    phase: 'network',
    title: 'Applying Network Bridge Configuration',
    name: 'ansible/10_baremetal_infra/10-2_configure_network_bridge_apply.yaml',
    requiresRestart: true
  })
  
  // Phase 3: LXD Setup (20_lxd_setup)
  queue.push({
    id: 'lxd-cluster',
    phase: 'lxd',
    title: 'Setting up LXD Cluster',
    name: 'ansible/20_lxd_setup/10_setup_lxd_cluster.yaml'
  })
  queue.push({
    id: 'lxd-profiles',
    phase: 'lxd',
    title: 'Setting up LXD Profiles',
    name: 'ansible/20_lxd_setup/20_setup_lxd_profiles.yaml'
  })
  
  // Check if VMs are needed
  const deploymentType = sessionStorage.getItem('deploymentType')
  if (deploymentType !== 'baremetal-only') {
    queue.push({
      id: 'create-vms',
      phase: 'lxd',
      title: 'Creating Virtual Machines',
      name: 'ansible/20_lxd_setup/30-1_create_base_vms.yaml'
    })
    queue.push({
      id: 'vm-networking',
      phase: 'lxd',
      title: 'Configuring VM Networking',
      name: 'ansible/20_lxd_setup/30-2_configure_vm_networking.yaml'
    })
    queue.push({
      id: 'vm-users',
      phase: 'lxd',
      title: 'Configuring VM Users',
      name: 'ansible/20_lxd_setup/30-3_configure_vm_users.yaml'
    })
    queue.push({
      id: 'vm-packages',
      phase: 'lxd',
      title: 'Installing VM Packages',
      name: 'ansible/20_lxd_setup/30-4_install_vm_packages.yaml'
    })
    queue.push({
      id: 'vm-python',
      phase: 'lxd',
      title: 'Configuring VM Python',
      name: 'ansible/20_lxd_setup/35_configure_vm_python.yaml'
    })
    
    // GPU passthrough if needed
    const gpuAssignments = JSON.parse(sessionStorage.getItem('gpuAssignments') || '{}')
    const hasVMGPUs = Object.values(gpuAssignments).some(v => v !== 'baremetal')
    if (hasVMGPUs) {
      queue.push({
        id: 'vm-gpu-passthrough',
        phase: 'lxd',
        title: 'Configuring GPU Passthrough',
        name: 'ansible/20_lxd_setup/60_configure_vm_gpu_passthrough.yaml'
      })
      queue.push({
        id: 'vm-gpu-drivers',
        phase: 'lxd',
        title: 'Installing GPU Drivers in VMs',
        name: 'ansible/20_lxd_setup/65_configure_vm_gpu_drivers.yaml'
      })
    }
  }
  
  // Phase 4: DNS and Networking (30_networking)
  queue.push({
    id: 'zerotier',
    phase: 'dns',
    title: 'Setting up ZeroTier Network',
    name: 'ansible/30_networking/10_setup_zerotier.yaml'
  })
  queue.push({
    id: 'dns',
    phase: 'dns',
    title: 'Setting up DNS Server',
    name: 'ansible/30_networking/20_setup_dns.yaml'
  })
  
  playbookQueue.value = queue
  console.log('Final playbook queue:', queue.map(p => `${p.id}: ${p.title}`))
  console.log('Total playbooks in queue:', queue.length)
}

// Reference to current playbook executor
const currentPlaybookExecutor = ref(null)

// Execute next playbook in queue
const executeNextPlaybook = async () => {
  console.log('executeNextPlaybook called, queue length:', playbookQueue.value.length)
  console.log('Current queue:', playbookQueue.value.map(p => p.title))
  
  if (playbookQueue.value.length === 0) {
    console.log('Queue empty, deployment complete')
    // Mark final phase as completed
    if (currentPhase.value) {
      const phase = deploymentPhases.value.find(p => p.id === currentPhase.value)
      if (phase) phase.status = 'completed'
    }
    deploymentComplete.value = true
    clearDeploymentState()
    return
  }
  
  const playbook = playbookQueue.value.shift()
  console.log('Next playbook to execute:', playbook.id, '-', playbook.title, '-', playbook.name)
  currentPlaybook.value = playbook
  
  // Update phase status
  if (currentPhase.value !== playbook.phase) {
    if (currentPhase.value) {
      const prevPhase = deploymentPhases.value.find(p => p.id === currentPhase.value)
      if (prevPhase) prevPhase.status = 'completed'
    }
    currentPhase.value = playbook.phase
    const phase = deploymentPhases.value.find(p => p.id === playbook.phase)
    if (phase) phase.status = 'active'
  }
  
  // Save state after each change
  saveDeploymentState()
  
  // Wait for Vue to update the DOM and component to mount
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Start playbook execution
  if (currentPlaybookExecutor.value && currentPlaybookExecutor.value.startExecution) {
    console.log('Starting playbook execution for:', playbook.name)
    
    // Get sudo password from sessionStorage
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    
    currentPlaybookExecutor.value.startExecution({
      environment: {
        ANSIBLE_BECOME_PASSWORD: sudoPassword,
        ANSIBLE_SSH_PASSWORD: sudoPassword
      },
      extra_vars: playbook.extraVars || {}
    })
  } else {
    console.error('PlaybookExecutor not ready', currentPlaybookExecutor.value)
  }
}

// Handle playbook completion
const handlePlaybookComplete = async (result) => {
  console.log('=== PLAYBOOK COMPLETE ===')
  console.log('Completed playbook:', currentPlaybook.value?.title)
  console.log('Result:', result)
  console.log('Queue before continuing:', playbookQueue.value.map(p => p.title))
  
  // Check if playbook succeeded (status can be 'success' or 'ok')
  if (result.status === 'error' || result.status === 'failed' || result.status === 'cancelled') {
    console.log('Playbook failed or cancelled, stopping deployment')
    
    if (result.status === 'cancelled') {
      deploymentError.value = `Deployment cancelled during: ${currentPlaybook.value.title}`
    } else {
      deploymentError.value = `Playbook ${currentPlaybook.value.title} failed: ${result.message || 'Check the logs for details'}`
    }
    
    const phase = deploymentPhases.value.find(p => p.id === currentPhase.value)
    if (phase) phase.status = 'failed'
    
    // Keep the playbook component visible so user can see the error/cancel modal
    // Don't set currentPlaybook to null here
    return
  }
  
  console.log('Playbook succeeded, checking for restart requirement...')
  // Check if restart is required
  if (currentPlaybook.value.requiresRestart) {
    console.log('Restart required, saving state...')
    showRestartNotice.value = true
    saveDeploymentState() // Save state before restart
    return
  }
  
  console.log('No restart required, waiting for user to click Continue...')
  // Don't automatically continue - wait for user to click Continue button
  // The PlaybookExecutorStream component will emit 'continue' event when user clicks Continue
}

// Handle user clicking Continue button in playbook modal
const handlePlaybookContinue = () => {
  console.log('User clicked Continue...')
  
  // Check if the just-completed playbook requires restart
  if (currentPlaybook.value?.requiresRestart) {
    console.log('Playbook requires restart, showing restart notice...')
    currentPlaybook.value = null
    showRestartNotice.value = true
    saveDeploymentState() // Save state before restart
    return
  }
  
  console.log('No restart required, clearing current playbook and executing next...')
  currentPlaybook.value = null
  executeNextPlaybook()
}

// Automated restart of all servers in correct order
const automatedRestart = async () => {
  // Save state BEFORE restart with awaitingRestart flag
  showRestartNotice.value = true  // Keep this true so it saves properly
  saveDeploymentState()
  
  // Now hide the restart notice for UI
  showRestartNotice.value = false
  
  // Create a special restart playbook entry
  const restartPlaybook = {
    id: 'restart-servers',
    phase: 'network',
    title: 'Restarting Servers (Ordered)',
    name: 'ansible/10_baremetal_infra/10-3_restart_servers_ordered.yaml',
    isRestart: true  // Special flag to handle differently
  }
  
  // Show the playbook executor for the restart
  currentPlaybook.value = restartPlaybook
  
  // Wait for component to mount
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Start the restart playbook
  if (currentPlaybookExecutor.value && currentPlaybookExecutor.value.startExecution) {
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    
    currentPlaybookExecutor.value.startExecution({
      environment: {
        ANSIBLE_BECOME_PASSWORD: sudoPassword,
        ANSIBLE_SSH_PASSWORD: sudoPassword
      }
    })
  }
}

// Check systems after restart
const checkSystemsAfterRestart = async () => {
  try {
    // Check if all servers are reachable
    const servers = JSON.parse(sessionStorage.getItem('servers') || '[]')
    const checks = servers.map(server => 
      axios.post('/api/test-ssh', { ip_address: server.ip })
    )
    
    const results = await Promise.all(checks)
    const allOnline = results.every(r => r.data.success)
    
    if (allOnline) {
      showRestartNotice.value = false
      saveDeploymentState() // Update state
      executeNextPlaybook()
    } else {
      alert('Some servers are not yet reachable. Please wait and try again.')
    }
  } catch (error) {
    console.error('Error checking systems:', error)
    alert('Error checking system status. Please try again.')
  }
}


// Retry current playbook
const retryCurrentPlaybook = () => {
  if (currentPlaybookExecutor.value && currentPlaybookExecutor.value.startExecution) {
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    currentPlaybookExecutor.value.startExecution({
      environment: {
        ANSIBLE_BECOME_PASSWORD: sudoPassword,
        ANSIBLE_SSH_PASSWORD: sudoPassword
      },
      extra_vars: currentPlaybook.value?.extraVars || {}
    })
  }
}

// Retry deployment from beginning
const retryDeployment = () => {
  deploymentError.value = ''
  deploymentComplete.value = false
  deploymentPhases.value.forEach(p => p.status = 'pending')
  buildPlaybookQueue()
  executeNextPlaybook()
}

// Reset deployment completely and go back to configuration
const resetDeployment = () => {
  clearDeploymentState()
  deploymentError.value = ''
  deploymentComplete.value = false
  currentPlaybook.value = null
  playbookQueue.value = []
  currentPhase.value = null
  showRestartNotice.value = false
  router.push('/configuration')
}

// Start deployment on mount
onMounted(async () => {
  // Check if we're resuming after restart
  const savedState = loadDeploymentState()
  
  if (savedState && savedState.awaitingRestart) {
    // Only resume from saved state if we're coming back from a restart
    deploymentPhases.value = savedState.phases
    playbookQueue.value = savedState.queue
    currentPhase.value = savedState.currentPhase
    showRestartNotice.value = false  // Don't show notice again
    
    console.log('Resuming deployment after system restart...')
    // Clear the restart flag but keep the progress
    savedState.awaitingRestart = false
    localStorage.setItem('thinkube-deployment-state', JSON.stringify(savedState))
    
    // Automatically continue after a delay to ensure all services are ready
    setTimeout(() => {
      executeNextPlaybook()
    }, 5000)  // 5 second delay to ensure everything is ready
  } else {
    // Any other case (fresh start or re-opening installer): start from beginning
    clearDeploymentState()
    buildPlaybookQueue()
    // Add small delay to ensure component is ready
    await new Promise(resolve => setTimeout(resolve, 500))
    executeNextPlaybook()
  }
})
</script>

<style scoped>
/* Custom styles for deployment view */
</style>