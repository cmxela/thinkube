<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">SSH Connectivity Check</h1>
    
    <!-- SSH Info -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Verifying SSH Access</h2>
        
        <div class="alert alert-info mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <p>Checking SSH connectivity to all discovered servers.</p>
            <p class="text-sm mt-1">Using credentials: <span class="font-mono">{{ currentUser }}</span> with the sudo password provided earlier.</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Discovered Servers -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Servers to Configure</h2>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>Hostname</th>
                <th>IP Address</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="server in servers" :key="server.ip">
                <td class="font-medium">{{ server.hostname }}</td>
                <td>{{ server.ip }}</td>
                <td>
                  <div class="badge" :class="getStatusClass(server.status)">
                    {{ server.status || 'Pending' }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Progress -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Setup Progress</h2>
        <progress class="progress progress-primary w-full" :value="progress" max="100"></progress>
        <p class="text-sm mt-2">{{ currentTask }}</p>
      </div>
    </div>
    
    <!-- Actions -->
    <div v-if="!isChecking" class="flex justify-between">
      <button class="btn btn-ghost gap-2" @click="$router.push('/server-discovery')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Back
      </button>
      
      <button 
        v-if="servers.every(s => s.status === 'failed')"
        class="btn btn-primary gap-2"
        @click="checkAndSetupSSH"
      >
        Retry
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// State
const servers = ref([])
const currentUser = ref('')
const isChecking = ref(false)
const progress = ref(0)
const currentTask = ref('')

// Status class helper
const getStatusClass = (status) => {
  switch (status) {
    case 'connected': return 'badge-success'
    case 'failed': return 'badge-error'
    case 'configuring': return 'badge-warning'
    default: return 'badge-ghost'
  }
}

// Check SSH connectivity and setup keys
const checkAndSetupSSH = async () => {
  isChecking.value = true
  progress.value = 0
  currentTask.value = 'Checking SSH connectivity...'
  
  try {
    // Get the sudo password from session storage
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    
    // Check connectivity to each server
    for (let i = 0; i < servers.value.length; i++) {
      const server = servers.value[i]
      currentTask.value = `Checking ${server.hostname}...`
      progress.value = ((i + 1) / servers.value.length) * 50
      
      try {
        const response = await axios.post('/api/verify-ssh', {
          server: server.ip,
          username: currentUser.value,
          password: sudoPassword
        })
        
        if (response.data.success) {
          server.status = 'connected'
        } else {
          server.status = 'failed'
          throw new Error(`Cannot connect to ${server.hostname}`)
        }
      } catch (error) {
        server.status = 'failed'
        throw new Error(`SSH check failed for ${server.hostname}: ${error.message}`)
      }
    }
    
    // Now setup passwordless SSH between all servers
    currentTask.value = 'Setting up passwordless SSH between servers...'
    progress.value = 75
    
    const response = await axios.post('/api/setup-ssh-keys', {
      servers: servers.value,
      username: currentUser.value,
      password: sudoPassword
    })
    
    if (response.data.status === 'success') {
      progress.value = 100
      currentTask.value = 'SSH setup completed!'
      
      // Store SSH info for later use
      sessionStorage.setItem('sshCredentials', JSON.stringify({
        username: currentUser.value,
        password: sudoPassword
      }))
      
      // Navigate to hardware detection
      setTimeout(() => {
        router.push('/hardware-detection')
      }, 1000)
    } else {
      throw new Error(response.data.message || 'SSH setup failed')
    }
  } catch (error) {
    console.error('SSH setup failed:', error)
    alert('Failed to setup SSH: ' + error.message)
  } finally {
    isChecking.value = false
  }
}

// Load discovered servers and start check
onMounted(async () => {
  const discoveredServers = JSON.parse(sessionStorage.getItem('discoveredServers') || '[]')
  servers.value = discoveredServers.map(s => ({
    hostname: s.hostname,
    ip: s.ip_address || s.ip,
    status: null
  }))
  
  // Get current user from API
  try {
    const response = await axios.get('/api/current-user')
    currentUser.value = response.data.username
  } catch (error) {
    console.error('Failed to get current user:', error)
    // Fallback to OS user
    currentUser.value = 'ubuntu'
  }
  
  // Start SSH check automatically
  if (servers.value.length > 0) {
    checkAndSetupSSH()
  }
})
</script>