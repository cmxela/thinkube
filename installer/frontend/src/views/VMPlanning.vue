<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Virtual Machine Planning</h1>
    
    <!-- VM Capable Servers -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">VM Host Servers</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="server in vmCapableServers" 
            :key="server.ip"
            class="border rounded-lg p-4"
          >
            <h3 class="font-semibold mb-2">{{ server.hostname }}</h3>
            <div class="text-sm space-y-1">
              <p>Available CPU: {{ server.availableCpu }} cores</p>
              <p>Available RAM: {{ server.availableRam }} GB</p>
              <p>Available Disk: {{ server.availableDisk }} GB</p>
            </div>
            
            <!-- VMs on this server -->
            <div class="mt-4">
              <h4 class="font-medium mb-2">Planned VMs:</h4>
              <div class="space-y-2">
                <div 
                  v-for="vm in getVMsForServer(server.hostname)" 
                  :key="vm.name"
                  class="bg-base-200 rounded p-2 text-sm"
                >
                  <p class="font-medium">{{ vm.name }}</p>
                  <p class="text-xs">{{ vm.cpu }} CPU, {{ vm.memory }} GB RAM, {{ vm.disk }} GB Disk</p>
                </div>
                <button 
                  class="btn btn-sm btn-ghost w-full"
                  @click="addVM(server.hostname)"
                >
                  + Add VM
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- VM Configuration -->
    <div v-if="plannedVMs.length > 0" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Virtual Machine Configuration</h2>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>VM Name</th>
                <th>Host Server</th>
                <th>CPU Cores</th>
                <th>Memory (GB)</th>
                <th>Disk (GB)</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vm, idx) in plannedVMs" :key="idx">
                <td>
                  <input 
                    v-model="vm.name" 
                    type="text" 
                    class="input input-bordered input-sm"
                    placeholder="vm-name"
                  />
                </td>
                <td>{{ vm.host }}</td>
                <td>
                  <input 
                    v-model.number="vm.cpu" 
                    type="number" 
                    min="2" 
                    max="16"
                    class="input input-bordered input-sm w-20"
                  />
                </td>
                <td>
                  <input 
                    v-model.number="vm.memory" 
                    type="number" 
                    min="4" 
                    max="64"
                    step="4"
                    class="input input-bordered input-sm w-20"
                  />
                </td>
                <td>
                  <input 
                    v-model.number="vm.disk" 
                    type="number" 
                    min="20" 
                    max="500"
                    step="10"
                    class="input input-bordered input-sm w-20"
                  />
                </td>
                <td>
                  <button 
                    class="btn btn-ghost btn-sm btn-circle"
                    @click="removeVM(idx)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Recommendations -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Recommendations</h2>
        
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>For high availability, create 3 control plane VMs on different hosts</p>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>Control plane VMs should have at least 4 CPU cores and 8GB RAM</p>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p>Worker VMs can be sized based on your workload requirements</p>
          </div>
        </div>
        
        <button 
          class="btn btn-sm btn-primary mt-4"
          @click="addRecommendedVMs"
        >
          Add Recommended Control Plane VMs
        </button>
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
        class="btn btn-primary gap-2"
        @click="createVMs"
        :disabled="plannedVMs.length === 0 || !isValid"
      >
        Create VMs & Continue
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
const servers = ref([])
const plannedVMs = ref([])

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

const getVMsForServer = (hostname) => {
  return plannedVMs.value.filter(vm => vm.host === hostname)
}

const isValid = computed(() => {
  return plannedVMs.value.every(vm => {
    return vm.name && 
           vm.cpu >= 2 && 
           vm.memory >= 4 && 
           vm.disk >= 20 &&
           /^[a-z0-9-]+$/.test(vm.name)
  })
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

// Add recommended VMs
const addRecommendedVMs = () => {
  // Clear existing VMs
  plannedVMs.value = []
  
  // Add control plane VMs
  const numControlPlanes = Math.min(3, vmCapableServers.value.length)
  for (let i = 0; i < numControlPlanes; i++) {
    const host = vmCapableServers.value[i % vmCapableServers.value.length]
    plannedVMs.value.push({
      name: `tkc${i === 0 ? '' : i + 1}`,
      host: host.hostname,
      cpu: 4,
      memory: 8,
      disk: 50
    })
  }
  
  // Add a couple of worker VMs
  for (let i = 0; i < Math.min(2, vmCapableServers.value.length); i++) {
    const host = vmCapableServers.value[i % vmCapableServers.value.length]
    plannedVMs.value.push({
      name: `tkw${i + 1}`,
      host: host.hostname,
      cpu: 4,
      memory: 16,
      disk: 100
    })
  }
}

// Create VMs
const createVMs = async () => {
  try {
    // Store VM plan
    sessionStorage.setItem('vmPlan', JSON.stringify(plannedVMs.value))
    
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
})
</script>