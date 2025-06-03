<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Baremetal Server Discovery</h1>
    
    <!-- Discovery Controls -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Scan Network for Ubuntu Servers</h2>
        
        <div class="mb-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Network CIDR</span>
            </label>
            <input 
              v-model="networkCIDR" 
              type="text" 
              placeholder="192.168.1.0/24" 
              class="input"
              :disabled="isScanning"
            />
          </div>
          
        </div>
        
        <div class="flex items-center gap-4">
          <button 
            class="btn btn-primary"
            @click="startDiscovery"
            :disabled="isScanning"
          >
            <span v-if="isScanning" class="loading loading-spinner"></span>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            {{ isScanning ? 'Scanning...' : 'Start Network Scan' }}
          </button>
          
          <button 
            class="btn btn-ghost"
            @click="addManualServer"
            :disabled="isScanning"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Add Server Manually
          </button>
        </div>
      </div>
    </div>
    
    <!-- Scanning Progress -->
    <div v-if="isScanning" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <div class="flex items-center gap-4">
          <div class="radial-progress text-primary" :style="`--value:${Math.round(scanProgress)};`">
            {{ Math.round(scanProgress) }}%
          </div>
          <div class="flex-1">
            <p class="text-lg font-semibold">Scanning Network...</p>
            <p class="text-sm text-base-content/70">{{ scanStatus }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Discovered Servers -->
    <div v-if="discoveredServers.length > 0" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">
          Discovered Servers
          <div class="badge badge-primary">{{ discoveredServers.length }}</div>
        </h2>
        
        <div class="space-y-4">
          <div 
            v-for="server in discoveredServers" 
            :key="server.ip"
            class="card bg-base-200 shadow-sm"
          >
            <div class="card-body p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <!-- Confidence Icon -->
                  <div class="flex-shrink-0">
                    <div v-if="server.confidence === 'confirmed'" class="tooltip" data-tip="Confirmed Ubuntu">
                      <svg class="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                    <div v-else-if="server.confidence === 'possible'" class="tooltip" data-tip="Possible Ubuntu">
                      <svg class="w-8 h-8 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                    <div v-else class="tooltip" data-tip="Unknown OS">
                      <svg class="w-8 h-8 text-base-content/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  
                  <!-- Server Info -->
                  <div>
                    <h3 class="font-semibold text-lg">
                      {{ server.ip }}
                      <span v-if="server.hostname" class="text-sm text-base-content/70 ml-2">
                        ({{ server.hostname }})
                      </span>
                    </h3>
                    <div class="text-sm text-base-content/70">
                      <span v-if="server.os_info">{{ server.os_info }}</span>
                      <span v-else-if="server.ssh_available">SSH Available</span>
                      <span v-else>No SSH Access</span>
                      <span v-if="server.banner" class="ml-2 font-mono text-xs">
                        • {{ server.banner.substring(0, 30) }}...
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Actions -->
                <div class="flex items-center gap-2">
                  <button 
                    v-if="server.confidence === 'possible'"
                    class="btn btn-sm btn-ghost"
                    @click="verifyServer(server)"
                  >
                    Verify
                  </button>
                  <button 
                    v-if="server.ssh_available && !selectedServers.find(s => s.ip === server.ip)"
                    class="btn btn-sm btn-primary"
                    @click="selectServer(server)"
                  >
                    Select
                  </button>
                  <div v-else-if="selectedServers.find(s => s.ip === server.ip)" class="badge badge-success">
                    Selected
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Manual Server Entry Modal -->
    <dialog ref="manualServerModal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Add Server Manually</h3>
        
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">IP Address</span>
          </label>
          <input 
            v-model="manualServer.ip" 
            type="text" 
            placeholder="192.168.1.101" 
            class="input input-bordered"
          />
        </div>
        
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Hostname (optional)</span>
          </label>
          <input 
            v-model="manualServer.hostname" 
            type="text" 
            placeholder="server-name" 
            class="input input-bordered"
          />
        </div>
        
        <div class="modal-action">
          <button class="btn btn-ghost" @click="closeManualModal">Cancel</button>
          <button class="btn btn-primary" @click="addManualServerConfirm">Add Server</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
    
    <!-- Navigation -->
    <div class="flex justify-between mt-6">
      <button class="btn btn-ghost gap-2" @click="$router.push('/installation')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Back
      </button>
      <button 
        class="btn btn-primary gap-2"
        @click="proceedToNodeConfig"
        :disabled="selectedServers.length === 0"
      >
        Continue with {{ selectedServers.length }} Server{{ selectedServers.length !== 1 ? 's' : '' }}
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
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
const networkCIDR = ref('192.168.1.0/24')
const testMode = ref(true)
const isScanning = ref(false)
const scanProgress = ref(0)
const scanStatus = ref('')
const discoveredServers = ref([])
const selectedServers = ref([])

// Manual server entry
const manualServerModal = ref(null)
const manualServer = ref({
  ip: '',
  hostname: ''
})

// Methods
const startDiscovery = async () => {
  isScanning.value = true
  scanProgress.value = 0
  scanStatus.value = 'Initializing scan...'
  discoveredServers.value = []
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    if (scanProgress.value < 90) {
      scanProgress.value = Math.min(90, scanProgress.value + Math.random() * 20)
      scanStatus.value = `Scanning ${networkCIDR.value} - Checking ${Math.floor(scanProgress.value * 2.54)} of 254 hosts`
    }
  }, 500)
  
  try {
    const response = await axios.post('/api/discover-servers', {
      network_cidr: networkCIDR.value,
      test_mode: testMode.value
    })
    
    discoveredServers.value = response.data.servers || []
    scanProgress.value = 100
    scanStatus.value = `Scan complete - Found ${discoveredServers.value.length} servers`
    
  } catch (error) {
    console.error('Discovery failed:', error)
    scanStatus.value = 'Scan failed: ' + error.message
  } finally {
    clearInterval(progressInterval)
    setTimeout(() => {
      isScanning.value = false
    }, 1000)
  }
}

const verifyServer = async (server) => {
  try {
    // Get password from sessionStorage
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    
    const response = await axios.post('/api/verify-server-ssh', {
      ip_address: server.ip,
      password: sudoPassword,
      test_mode: testMode.value
    })
    
    // Update server info based on verification
    const idx = discoveredServers.value.findIndex(s => s.ip === server.ip)
    if (idx >= 0) {
      if (response.data.connected) {
        discoveredServers.value[idx] = {
          ...discoveredServers.value[idx],
          hostname: response.data.hostname || server.hostname,
          os_info: response.data.os_info,
          confidence: response.data.os_info?.includes('24.04') ? 'confirmed' : 'possible'
        }
      }
    }
  } catch (error) {
    console.error('Verification failed:', error)
  }
}

const selectServer = (server) => {
  if (!selectedServers.value.find(s => s.ip === server.ip)) {
    selectedServers.value.push(server)
  }
}

const addManualServer = () => {
  manualServer.value = { ip: '', hostname: '' }
  manualServerModal.value.showModal()
}

const closeManualModal = () => {
  manualServerModal.value.close()
}

const addManualServerConfirm = () => {
  if (manualServer.value.ip) {
    const newServer = {
      ip: manualServer.value.ip,
      hostname: manualServer.value.hostname || null,
      confidence: 'unknown',
      ssh_available: true,
      os_info: null,
      banner: null
    }
    
    // Add to discovered servers if not already there
    if (!discoveredServers.value.find(s => s.ip === newServer.ip)) {
      discoveredServers.value.push(newServer)
    }
    
    // Auto-select it
    selectServer(newServer)
    
    closeManualModal()
  }
}

const proceedToNodeConfig = () => {
  // Debug log to see what we're storing
  console.log('Selected servers:', selectedServers.value)
  
  // Store selected servers in a shared store or pass via router
  sessionStorage.setItem('selectedServers', JSON.stringify(selectedServers.value))
  sessionStorage.setItem('testMode', testMode.value)
  // Store discovered servers - these should have full server objects with hostnames
  sessionStorage.setItem('discoveredServers', JSON.stringify(selectedServers.value))
  // Store network CIDR for inventory generation
  sessionStorage.setItem('networkCIDR', networkCIDR.value)
  router.push('/ssh-setup')
}

// Auto-detect network on mount
onMounted(async () => {
  try {
    const response = await axios.get('/api/local-network')
    if (response.data.detected) {
      networkCIDR.value = response.data.network_cidr
      console.log(`Auto-detected network: ${response.data.network_cidr}`)
    }
  } catch (error) {
    console.error('Failed to auto-detect network:', error)
    // Keep default value
  }
})
</script>

<style scoped>
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: slide-in 0.3s ease-out;
}
</style>