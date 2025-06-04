<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Virtual Machine Planning (Optional)</h1>
    
    <!-- Baremetal-First Recommendation -->
    <div class="alert alert-info mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <div>
        <h3 class="font-bold">Thinkube recommends a baremetal-first approach!</h3>
        <div class="text-sm mt-2 space-y-1">
          <p>• <strong>Use baremetal nodes directly</strong> for better performance and simpler architecture</p>
          <p>• <strong>GPU workloads</strong> run best on baremetal - avoid complex GPU passthrough</p>
          <p>• <strong>Consider VMs only when needed</strong> for isolation or specific requirements</p>
          <p>• <strong>Alternative: Raspberry Pi</strong> can serve as a low-power DNS server</p>
        </div>
      </div>
    </div>

    <!-- When to Use VMs -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">When Should You Use VMs?</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-3">
            <h3 class="font-semibold text-success">✓ Good Use Cases for VMs</h3>
            <ul class="text-sm space-y-1 text-base-content text-opacity-70">
              <li>• Learning Kubernetes with multi-node simulation on limited hardware</li>
              <li>• Maximizing use of powerful servers (32+ cores, 128+ GB RAM)</li>
              <li>• Testing cluster configurations before deploying to production</li>
              <li>• Isolating the control plane from experimental workloads</li>
              <li>• Running lightweight services (DNS, monitoring) without dedicating hardware</li>
            </ul>
          </div>
          
          <div class="space-y-3">
            <h3 class="font-semibold text-warning">✗ Avoid VMs For</h3>
            <ul class="text-sm space-y-1 text-base-content text-opacity-70">
              <li>• GPU-accelerated AI/ML workloads</li>
              <li>• Real-time applications or gaming servers</li>
              <li>• Storage-intensive applications (use baremetal)</li>
              <li>• When you have multiple physical servers available</li>
              <li>• Production workloads requiring predictable performance</li>
            </ul>
          </div>
        </div>

        <div class="mt-4 p-3 bg-info bg-opacity-10 rounded-lg">
          <p class="text-sm"><strong>Homelab Tip:</strong> If you have older servers with 8-16GB RAM, use them as dedicated nodes instead of cramming VMs onto one powerful server. This gives better performance and real distributed system experience.</p>
        </div>
      </div>
    </div>

    <!-- DNS Configuration Decision -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">DNS Server Configuration</h2>
        <p class="mb-4">Thinkube requires a DNS server that is isolated from the MicroK8s cluster network.</p>
        
        <div class="space-y-4">
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-start gap-3">
                <input 
                  type="radio" 
                  name="dns-option" 
                  class="radio radio-primary mt-1" 
                  value="baremetal"
                  v-model="dnsOption"
                />
                <div>
                  <span class="label-text font-semibold">Dedicate a server for DNS</span>
                  <p class="text-sm text-base-content text-opacity-70 mt-1">
                    Use one of your discovered servers exclusively for DNS (recommended if you have 3+ servers)
                  </p>
                </div>
              </div>
            </label>
          </div>
          
          <div class="form-control">
            <label class="label cursor-pointer">
              <div class="flex items-start gap-3">
                <input 
                  type="radio" 
                  name="dns-option" 
                  class="radio radio-primary mt-1" 
                  value="vm"
                  v-model="dnsOption"
                />
                <div>
                  <span class="label-text font-semibold">Create a VM for DNS</span>
                  <p class="text-sm text-base-content text-opacity-70 mt-1">
                    Create a lightweight VM (2 CPU, 2GB RAM) to run DNS services
                  </p>
                </div>
              </div>
            </label>
          </div>
        </div>
        
        <div v-if="dnsOption === 'baremetal' && servers.length < 3" class="mt-4 p-3 bg-warning bg-opacity-10 rounded-lg">
          <p class="text-sm"><strong>Note:</strong> With {{ servers.length }} server(s), dedicating one to DNS leaves {{ servers.length - 1 }} for your cluster. Consider using a VM instead to maximize cluster resources.</p>
        </div>
      </div>
    </div>

    <!-- Skip VMs Option (only if baremetal DNS) -->
    <div v-if="dnsOption === 'baremetal'" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Continue without VMs?</h2>
        <p class="mb-4">Since you're using a dedicated server for DNS, you can proceed with a baremetal-only deployment.</p>
        <button 
          class="btn btn-success gap-2"
          @click="skipVMs"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
          </svg>
          Continue with Baremetal Only
        </button>
      </div>
    </div>
    
    <!-- Create DNS VM -->
    <div v-if="dnsOption === 'vm' && !hasDnsVM" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Create DNS Virtual Machine</h2>
        <p class="mb-4">Select which server should host the DNS VM:</p>
        
        <div class="space-y-3">
          <div 
            v-for="server in vmCapableServers" 
            :key="server.ip"
            class="border rounded-lg p-4 hover:border-primary cursor-pointer"
            @click="createDnsVM(server.hostname)"
          >
            <div class="flex justify-between items-center">
              <div>
                <h3 class="font-semibold">{{ server.hostname }}</h3>
                <p class="text-sm text-base-content text-opacity-70">
                  {{ server.availableCpu }} CPU cores, {{ server.availableRam }} GB RAM available
                </p>
              </div>
              <button class="btn btn-primary btn-sm">
                Create DNS VM Here
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Planned VMs Overview -->
    <div v-if="plannedVMs.length > 0" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Planned Virtual Machines</h2>
        
        <div class="space-y-3">
          <div 
            v-for="(vm, idx) in plannedVMs" 
            :key="idx"
            class="border rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="mb-2">
                  <input 
                    v-if="vm.name !== 'dns'"
                    v-model="vm.name" 
                    type="text" 
                    class="input input-sm font-semibold text-lg"
                    :class="{ 'input-error': vm.name && !/^[a-z0-9-]+$/.test(vm.name) }"
                    placeholder="vm-name"
                    pattern="[a-z0-9\\x2D]+"
                  />
                  <h3 v-else class="font-semibold text-lg">{{ vm.name }}</h3>
                  <p v-if="vm.name && !/^[a-z0-9-]+$/.test(vm.name)" class="text-xs text-error mt-1">
                    Name must contain only lowercase letters, numbers, and hyphens
                  </p>
                </div>
                <p class="text-sm text-base-content text-opacity-70 mb-2">Host: {{ vm.host }}</p>
                
                <div class="grid grid-cols-3 gap-4 mt-3">
                  <div>
                    <label class="label p-0">
                      <span class="label-text text-xs">CPU Cores</span>
                    </label>
                    <input 
                      v-model.number="vm.cpu" 
                      type="number" 
                      min="2" 
                      max="16"
                      class="input input-bordered input-sm w-full"
                      :disabled="vm.name === 'dns'"
                    />
                  </div>
                  <div>
                    <label class="label p-0">
                      <span class="label-text text-xs">Memory (GB)</span>
                    </label>
                    <input 
                      v-model.number="vm.memory" 
                      type="number" 
                      min="2" 
                      max="64"
                      step="2"
                      class="input input-bordered input-sm w-full"
                      :disabled="vm.name === 'dns'"
                    />
                  </div>
                  <div>
                    <label class="label p-0">
                      <span class="label-text text-xs">Disk (GB)</span>
                    </label>
                    <input 
                      v-model.number="vm.disk" 
                      type="number" 
                      min="20" 
                      max="500"
                      step="10"
                      class="input input-bordered input-sm w-full"
                      :disabled="vm.name === 'dns'"
                    />
                  </div>
                </div>
              </div>
              
              <button 
                class="btn btn-ghost btn-sm btn-circle ml-4"
                @click="removeVM(idx)"
                :disabled="vm.name === 'dns' && dnsOption === 'vm'"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Add Additional VM -->
        <div v-if="vmCapableServers.length > 0" class="mt-6">
          <h3 class="font-semibold mb-3">Add Additional VM (Optional)</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button 
              v-for="server in vmCapableServers" 
              :key="server.ip"
              class="btn btn-outline"
              @click="addVM(server.hostname)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              Add VM on {{ server.hostname }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recommendations -->
    <div v-if="dnsOption !== ''" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">VM Planning Guidance</h2>
        
        <div class="space-y-2">
          <div v-if="dnsOption === 'vm'" class="flex items-center gap-2">
            <svg class="w-5 h-5 text-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <p>DNS VM required: 2 CPU cores, 2GB RAM minimum</p>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>Production clusters should use baremetal nodes for best performance</p>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>VMs are useful for testing multi-node scenarios before production</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- LXD Primary Selection (shown when VMs span multiple servers) -->
    <div v-if="needsLxdPrimarySelection" class="card bg-warning bg-opacity-10 border-warning shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title text-warning mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          LXD Primary Node Selection Required
        </h2>
        
        <div class="mb-4">
          <p class="mb-2">Your VMs will be distributed across multiple servers, requiring an LXD cluster.</p>
          <p class="text-sm text-base-content text-opacity-70">Choose which server should be the LXD primary node (manages the cluster):</p>
        </div>
        
        <div class="space-y-3">
          <div 
            v-for="server in serversWithVMs" 
            :key="server.hostname"
            class="border rounded-lg p-4 cursor-pointer transition-colors"
            :class="lxdPrimary === server.hostname ? 'border-primary bg-primary bg-opacity-10' : 'border-base-300 hover:border-primary'"
            @click="lxdPrimary = server.hostname"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center gap-3">
                  <input 
                    type="radio" 
                    :value="server.hostname"
                    v-model="lxdPrimary"
                    class="radio radio-primary" 
                  />
                  <div>
                    <h3 class="font-bold">{{ server.hostname }}</h3>
                    <p class="text-sm text-base-content text-opacity-70">{{ server.ip }}</p>
                  </div>
                </div>
                <div class="mt-2 text-sm">
                  <span class="badge badge-outline mr-2">{{ server.hardware.cpu_cores }} cores</span>
                  <span class="badge badge-outline mr-2">{{ Math.round(server.hardware.memory_gb) }}GB RAM</span>
                  <span class="badge badge-outline">{{ getVMsForServer(server.hostname).length }} VMs</span>
                </div>
              </div>
              <div v-if="lxdPrimary === server.hostname" class="text-primary">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mt-4 text-sm text-base-content text-opacity-70">
          <p><strong>Recommendation:</strong> Choose the server with moderate resources for cluster management, reserving powerful servers for AI workloads.</p>
        </div>
      </div>
    </div>
    
    <!-- Actions -->
    <div class="flex justify-between">
      <button class="btn btn-ghost gap-2" @click="$router.push('/hardware-detection')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Back
      </button>
      
      <button 
        v-if="dnsOption === 'vm' && !hasDnsVM"
        class="btn btn-primary gap-2"
        disabled
      >
        Please Select DNS VM Host
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </button>
      
      <button 
        v-else-if="plannedVMs.length > 0"
        class="btn btn-primary gap-2"
        @click="createVMs"
        :disabled="!isValid"
      >
        Continue with {{ plannedVMs.length }} VM{{ plannedVMs.length > 1 ? 's' : '' }}
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </button>
      
      <button 
        v-else
        class="btn btn-ghost gap-2"
        disabled
      >
        Select DNS Option Above
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
const plannedVMs = ref([])
const dnsOption = ref('')
const lxdPrimary = ref('')

// Computed
const vmCapableServers = computed(() => {
  return servers.value.filter(s => s.canHostVMs).map(s => ({
    ...s,
    // Reserve some resources for the host
    availableCpu: Math.max(0, s.hardware.cpu_cores - 4),
    availableRam: Math.max(0, s.hardware.memory_gb - 8),
    availableDisk: Math.max(0, s.hardware.disk_gb - 50)
  }))
})

const hasDnsVM = computed(() => {
  return plannedVMs.value.some(vm => vm.name === 'dns')
})

const getVMsForServer = (hostname) => {
  return plannedVMs.value.filter(vm => vm.host === hostname)
}

// Servers that have VMs planned
const serversWithVMs = computed(() => {
  const hostnames = [...new Set(plannedVMs.value.map(vm => vm.host))]
  return servers.value.filter(s => hostnames.includes(s.hostname))
})

// Check if LXD primary selection is needed (VMs span multiple servers)
const needsLxdPrimarySelection = computed(() => {
  return serversWithVMs.value.length > 1
})

const isValid = computed(() => {
  const vmsValid = plannedVMs.value.every(vm => {
    return vm.name && 
           vm.cpu >= 2 && 
           vm.memory >= 2 && 
           vm.disk >= 20 &&
           /^[a-z0-9-]+$/.test(vm.name)
  })
  
  // If LXD primary selection is needed, ensure one is selected
  const lxdPrimaryValid = !needsLxdPrimarySelection.value || lxdPrimary.value !== ''
  
  return vmsValid && lxdPrimaryValid
})

// Add VM
const addVM = (hostname) => {
  plannedVMs.value.push({
    name: `vm-${plannedVMs.value.length + 1}`,
    host: hostname,
    cpu: 4,
    memory: 8,
    disk: 50
  })
}

// Remove VM
const removeVM = (idx) => {
  plannedVMs.value.splice(idx, 1)
}

// Skip VMs and go directly to role assignment
const skipVMs = () => {
  // Store that we're using baremetal only with dedicated DNS server
  sessionStorage.setItem('deploymentType', 'baremetal-only')
  sessionStorage.setItem('dnsOption', 'baremetal')
  sessionStorage.setItem('vmPlan', JSON.stringify([]))  // No VMs
  sessionStorage.setItem('lxdPrimary', '')  // No LXD cluster needed for baremetal-only
  router.push('/role-assignment')
}

// Create DNS VM on specific host
const createDnsVM = (hostname) => {
  // Remove any existing DNS VM
  plannedVMs.value = plannedVMs.value.filter(vm => vm.name !== 'dns')
  
  // Add DNS VM on selected host
  plannedVMs.value.push({
    name: 'dns',
    host: hostname,
    cpu: 2,
    memory: 2,
    disk: 20
  })
}

// Create VMs
const createVMs = async () => {
  try {
    // Determine LXD primary automatically if only one server has VMs
    let selectedLxdPrimary = lxdPrimary.value
    if (serversWithVMs.value.length === 1) {
      selectedLxdPrimary = serversWithVMs.value[0].hostname
    }
    
    // Store VM plan, DNS option, and LXD primary selection
    sessionStorage.setItem('vmPlan', JSON.stringify(plannedVMs.value))
    sessionStorage.setItem('dnsOption', dnsOption.value)
    sessionStorage.setItem('lxdPrimary', selectedLxdPrimary)
    sessionStorage.setItem('deploymentType', 'mixed')  // Has VMs
    
    // In a real implementation, this would call the backend to create VMs
    // For now, we'll just continue to role assignment
    router.push('/role-assignment')
  } catch (error) {
    console.error('Failed to create VMs:', error)
    alert('Failed to create VMs: ' + error.message)
  }
}

// Load server hardware info
onMounted(() => {
  const serverHardware = JSON.parse(sessionStorage.getItem('serverHardware') || '[]')
  servers.value = serverHardware
  
  // Load existing VM plan if any
  const existingVMPlan = sessionStorage.getItem('vmPlan')
  if (existingVMPlan) {
    plannedVMs.value = JSON.parse(existingVMPlan)
  }
  
  // Load DNS option if set
  const savedDnsOption = sessionStorage.getItem('dnsOption')
  if (savedDnsOption) {
    dnsOption.value = savedDnsOption
  }
})
</script>