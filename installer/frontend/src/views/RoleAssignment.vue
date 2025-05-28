<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Kubernetes Role Assignment</h1>
    
    <!-- Role Requirements -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Role Requirements</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h3 class="font-semibold mb-2">Control Plane Node</h3>
            <ul class="text-sm space-y-1 text-base-content/70">
              <li>• Manages Kubernetes API and cluster state</li>
              <li>• Requires at least 4 CPU cores and 8GB RAM</li>
              <li>• Single node setup for homelab use</li>
              <li>• Can run on baremetal or VM</li>
            </ul>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2">Worker Nodes</h3>
            <ul class="text-sm space-y-1 text-base-content/70">
              <li>• Run application workloads</li>
              <li>• Can be baremetal or VMs</li>
              <li>• GPU nodes for AI workloads</li>
              <li>• More resources = more capacity</li>
            </ul>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2">DNS Server</h3>
            <ul class="text-sm space-y-1 text-base-content/70">
              <li>• Provides internal DNS resolution</li>
              <li>• Can run on baremetal or VM</li>
              <li>• Requires at least 2 CPU cores and 2GB RAM</li>
              <li>• Only one DNS server needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Node List with Role Assignment -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Assign Roles to Nodes</h2>
        
        <div class="space-y-4">
          <!-- Baremetal Servers -->
          <div v-if="baremetalNodes.length > 0">
            <h3 class="font-semibold mb-2">Baremetal Servers</h3>
            <div class="space-y-2">
              <div 
                v-for="node in baremetalNodes" 
                :key="node.id"
                class="flex items-center justify-between p-3 rounded-lg bg-base-200"
              >
                <div class="flex items-center gap-3">
                  <div>
                    <p class="font-medium">{{ node.hostname }}</p>
                    <p class="text-sm text-base-content/70">
                      {{ node.cpu }} CPU, {{ node.memory }} GB RAM
                      <span v-if="getNodeGPUStatus(node)" class="badge badge-success badge-sm ml-2">
                        {{ getNodeGPUStatus(node) }}
                      </span>
                    </p>
                  </div>
                </div>
                
                <select 
                  v-model="node.role" 
                  class="select select-bordered select-sm"
                  @change="validateRoles"
                  :disabled="controlPlaneNodes.length > 0 && node.role !== 'control_plane'"
                >
                  <option value="">No Role</option>
                  <option value="worker">Worker</option>
                  <option value="control_plane" :disabled="!canBeControlPlane(node) || (controlPlaneNodes.length > 0 && node.role !== 'control_plane')">Control Plane</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Virtual Machines -->
          <div v-if="vmNodes.length > 0">
            <h3 class="font-semibold mb-2">Virtual Machines</h3>
            <div class="space-y-2">
              <!-- DNS VM Special Case -->
              <div 
                v-for="node in vmNodes.filter(n => n.hostname === 'dns')" 
                :key="node.id"
                class="flex items-center justify-between p-3 rounded-lg bg-base-200"
              >
                <div class="flex items-center gap-3">
                  <div>
                    <p class="font-medium">{{ node.hostname }}</p>
                    <p class="text-sm text-base-content/70">
                      {{ node.cpu }} CPU, {{ node.memory }} GB RAM
                      <span class="badge badge-info badge-sm ml-2">VM on {{ node.host }}</span>
                    </p>
                  </div>
                </div>
                
                <div class="text-sm font-semibold">
                  DNS Server (Fixed Role)
                </div>
              </div>
              
              <!-- Other VMs -->
              <div 
                v-for="node in vmNodes.filter(n => n.hostname !== 'dns')" 
                :key="node.id"
                class="flex items-center justify-between p-3 rounded-lg bg-base-200"
              >
                <div class="flex items-center gap-3">
                  <div>
                    <p class="font-medium">{{ node.hostname }}</p>
                    <p class="text-sm text-base-content/70">
                      {{ node.cpu }} CPU, {{ node.memory }} GB RAM
                      <span class="badge badge-info badge-sm ml-2">VM on {{ node.host }}</span>
                      <span v-if="canVMHaveGPU(node)" class="badge badge-warning badge-sm ml-2">
                        GPU Available
                      </span>
                    </p>
                  </div>
                </div>
                
                <div class="flex items-center gap-3">
                  <select 
                    v-model="node.role" 
                    class="select select-bordered select-sm"
                    @change="validateRoles"
                    :disabled="controlPlaneNodes.length > 0 && node.role !== 'control_plane'"
                  >
                    <option value="">No Role</option>
                    <option value="worker">Worker</option>
                    <option value="control_plane" :disabled="!canBeControlPlane(node) || (controlPlaneNodes.length > 0 && node.role !== 'control_plane')">Control Plane</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Validation Messages -->
    <div v-if="validationErrors.length > 0" class="alert alert-warning mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <p v-for="error in validationErrors" :key="error">{{ error }}</p>
      </div>
    </div>
    
    <!-- Actions -->
    <div class="flex justify-between">
      <button class="btn btn-ghost gap-2" @click="$router.push('/vm-planning')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Back
      </button>
      
      <button 
        class="btn btn-primary gap-2"
        @click="saveAndContinue"
        :disabled="!isValid"
      >
        Continue to Configuration
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

const router = useRouter()

// State
const allNodes = ref([])
const validationErrors = ref([])

// Computed
const baremetalNodes = computed(() => {
  return allNodes.value.filter(n => n.type === 'baremetal')
})

const vmNodes = computed(() => {
  return allNodes.value.filter(n => n.type === 'vm')
})

const controlPlaneNodes = computed(() => {
  return allNodes.value.filter(n => n.role === 'control_plane')
})

const workerNodes = computed(() => {
  return allNodes.value.filter(n => n.role === 'worker')
})

const dnsNodes = computed(() => {
  return allNodes.value.filter(n => n.role === 'dns')
})

const isValid = computed(() => {
  return validationErrors.value.length === 0 &&
         controlPlaneNodes.value.length > 0 &&
         workerNodes.value.length > 0
})

// Check if node can be control plane
const canBeControlPlane = (node) => {
  return node.cpu >= 4 && node.memory >= 8
}

// Get GPU status for baremetal nodes
const getNodeGPUStatus = (node) => {
  if (!node.hasGPU || !node.gpuInfo) return null
  
  // Get passthrough info for this node
  const passthroughInfo = node.gpuInfo.gpu_passthrough_info || []
  const totalGPUs = node.gpuInfo.gpu_count || 0
  const passthroughEligible = passthroughInfo.filter(g => g.passthrough_eligible).length
  
  // Check if this node hosts VMs (other than DNS)
  const hostedVMs = allNodes.value.filter(n => 
    n.type === 'vm' && 
    n.host === node.hostname && 
    n.hostname !== 'dns'
  )
  
  if (hostedVMs.length === 0) {
    // No VMs, all GPUs assigned to this node
    return `${totalGPUs} GPU${totalGPUs > 1 ? 's' : ''}`
  } else {
    // Has VMs, only non-passthrough-eligible GPUs assigned
    const assignedGPUs = totalGPUs - passthroughEligible
    return assignedGPUs > 0 ? `${assignedGPUs} GPU${assignedGPUs > 1 ? 's' : ''}` : null
  }
}

// Check if VM can have GPU passthrough
const canVMHaveGPU = (vm) => {
  // Find the host server
  const host = allNodes.value.find(n => n.type === 'baremetal' && n.hostname === vm.host)
  if (!host || !host.hasGPU || !host.gpuInfo) return false
  
  // Check if host has passthrough-eligible GPUs
  const passthroughInfo = host.gpuInfo.gpu_passthrough_info || []
  const eligibleGPUs = passthroughInfo.filter(g => g.passthrough_eligible)
  
  // VM can have GPU if host has at least one passthrough-eligible GPU
  return eligibleGPUs.length > 0
}

// Validate role assignment
const validateRoles = () => {
  validationErrors.value = []
  
  // Check control plane count (only allow ONE)
  const cpCount = controlPlaneNodes.value.length
  if (cpCount === 0) {
    validationErrors.value.push('Exactly one control plane node is required')
  } else if (cpCount > 1) {
    validationErrors.value.push('Only one control plane node is allowed for Thinkube')
  }
  
  // Check worker count
  if (workerNodes.value.length === 0) {
    validationErrors.value.push('At least one worker node is required')
  }
  
  // Check DNS server exists (either as dedicated node or VM)
  const hasDnsServer = allNodes.value.some(n => n.hostname === 'dns' || n.role === 'dns')
  if (!hasDnsServer) {
    validationErrors.value.push('DNS server is required (either as VM or dedicated node)')
  }
  
  // Check unassigned nodes (excluding DNS VM which has fixed role)
  const unassignedCount = allNodes.value.filter(n => !n.role && n.hostname !== 'dns').length
  if (unassignedCount > 0) {
    validationErrors.value.push(`${unassignedCount} nodes have no role assigned`)
  }
}

// Save and continue
const saveAndContinue = () => {
  // Store the complete node configuration
  const clusterNodes = allNodes.value.filter(n => n.role).map(n => ({
    hostname: n.hostname,
    ip: n.ip,
    role: n.role,
    type: n.type,
    host: n.host,  // Important for VMs
    cpu: n.cpu,
    memory: n.memory,
    disk: n.disk,
    gpu: n.gpu,
    hasGPU: n.hasGPU,
    gpuInfo: n.gpuInfo
  }))
  
  sessionStorage.setItem('clusterNodes', JSON.stringify(clusterNodes))
  router.push('/configuration')
}

// Load all nodes
onMounted(() => {
  // Load baremetal servers
  const serverHardware = JSON.parse(sessionStorage.getItem('serverHardware') || '[]')
  const baremetalList = serverHardware.map(s => ({
    id: `bm-${s.hostname}`,
    hostname: s.hostname,
    ip: s.ip,
    type: 'baremetal',
    cpu: s.hardware?.cpu_cores || 0,
    memory: s.hardware?.memory_gb || 0,
    disk: s.hardware?.disk_gb || 0,
    hasGPU: s.hardware?.gpu_detected || false,
    gpuInfo: {
      gpu_count: s.hardware?.gpu_count || 0,
      gpu_model: s.hardware?.gpu_model || '',
      gpu_passthrough_info: s.hardware?.gpu_passthrough_info || [],
      iommu_enabled: s.hardware?.iommu_enabled || false
    },
    role: ''
  }))
  
  // Load planned VMs
  const vmPlan = JSON.parse(sessionStorage.getItem('vmPlan') || '[]')
  const vmList = vmPlan.map((vm, idx) => ({
    id: `vm-${idx}`,
    hostname: vm.name,
    ip: null, // Will be assigned later
    type: 'vm',
    host: vm.host,
    cpu: vm.cpu,
    memory: vm.memory,
    disk: vm.disk,
    gpu: false,
    role: ''
  }))
  
  allNodes.value = [...baremetalList, ...vmList]
  
  // Auto-assign recommended roles
  // DNS VM has fixed role (not changeable)
  const dnsVm = allNodes.value.find(n => n.type === 'vm' && n.hostname === 'dns')
  if (dnsVm) {
    dnsVm.role = 'dns'
  }
  
  // Only ONE control plane allowed - prefer VM if available
  const eligibleForCP = allNodes.value.filter(n => canBeControlPlane(n) && n.hostname !== 'dns')
  const vmCandidates = eligibleForCP.filter(n => n.type === 'vm')
  const baremetalCandidates = eligibleForCP.filter(n => n.type === 'baremetal')
  
  if (vmCandidates.length > 0) {
    vmCandidates[0].role = 'control_plane'
  } else if (baremetalCandidates.length > 0) {
    baremetalCandidates[0].role = 'control_plane'
  }
  
  // Everything else as workers
  allNodes.value.forEach(node => {
    if (!node.role && node.hostname !== 'dns' && (node.type === 'baremetal' || node.cpu >= 2)) {
      node.role = 'worker'
    }
  })
  
  validateRoles()
})
</script>