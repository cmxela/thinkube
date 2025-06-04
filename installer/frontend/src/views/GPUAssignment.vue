<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Configure GPU</h1>
    
    <!-- GPU Configuration Card -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Configure GPU</h2>
        <p class="text-sm text-base-content text-opacity-70 mb-6">
          Configure GPU assignment for your cluster. GPUs can stay on the baremetal host or be passed through to VMs.
        </p>

        <!-- No GPUs available message -->
        <div v-if="!hasGPUs" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-base-content text-opacity-30 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p class="text-base-content text-opacity-70">No GPU-capable nodes detected. Proceeding without GPU configuration.</p>
        </div>

        <!-- GPU Configuration -->
        <div v-else class="space-y-4">
          <div v-for="gpu in allGPUs" :key="gpu.address" class="border border-base-300 rounded-lg p-4">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-lg font-semibold flex items-center">
                  <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                  {{ gpu.model }}
                </h3>
                <p class="text-sm text-base-content text-opacity-70 ml-7">{{ gpu.hostname }} • PCI: {{ gpu.address }}</p>
                <p class="text-sm text-base-content text-opacity-70 ml-7">IOMMU Group: {{ gpu.iommu_group }}</p>
              </div>
              
              <div class="ml-4 space-y-2">
                <!-- Show options only if GPU is eligible AND has VMs to pass to -->
                <div v-if="gpu.passthrough_eligible && gpu.vms.length > 0">
                  <label class="flex items-center">
                    <input 
                      type="radio" 
                      :name="`gpu-${gpu.address}`"
                      :value="'baremetal'"
                      v-model="gpuAssignments[gpu.address]"
                      class="radio radio-primary mr-2"
                    >
                    <span class="text-sm">Keep on {{ gpu.hostname }}</span>
                  </label>
                  
                  <!-- Show VM options -->
                  <div class="ml-6 space-y-2 mt-2">
                    <label v-for="vm in gpu.vms" :key="vm.name" class="flex items-center">
                      <input 
                        type="radio" 
                        :name="`gpu-${gpu.address}`"
                        :value="vm.name"
                        v-model="gpuAssignments[gpu.address]"
                        class="radio radio-primary mr-2"
                      >
                      <span class="text-sm">Pass to {{ vm.name }}</span>
                    </label>
                  </div>
                </div>
                <!-- GPU stays on host (either not eligible or no VMs) -->
                <div v-else class="p-3 bg-base-200 rounded">
                  <p class="text-sm font-medium">Remains on {{ gpu.hostname }}</p>
                  <p class="text-xs text-base-content text-opacity-70">
                    {{ gpu.passthrough_eligible ? 'No VMs on this host' : 'Not eligible for passthrough' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div v-if="hasGPUs && Object.keys(gpuAssignments).length > 0" class="mt-6 p-4 bg-info bg-opacity-10 rounded-lg">
          <h4 class="font-semibold mb-2">GPU Assignment Summary</h4>
          <div class="text-sm">
            <p v-if="baremetalGPUs > 0">{{ baremetalGPUs }} GPU(s) assigned to baremetal hosts</p>
            <p v-if="vmGPUs > 0">{{ vmGPUs }} GPU(s) assigned for VM passthrough</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="flex justify-between">
        <button 
          type="button" 
          @click="goBack"
          class="btn btn-ghost gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Network Configuration
        </button>
        
        <button
          type="button"
          @click="saveAndContinue"
          class="btn btn-primary gap-2"
        >
          Continue to Review
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const gpuNodes = ref([])
const allGPUs = ref([])
const gpuAssignments = ref({})

const hasGPUs = computed(() => allGPUs.value.length > 0)

// Debug assignments when they change
watch(gpuAssignments, (newVal) => {
  console.log('GPU assignments changed:', newVal)
}, { deep: true })

const baremetalGPUs = computed(() => {
  return Object.values(gpuAssignments.value).filter(assignment => assignment === 'baremetal').length
})

const vmGPUs = computed(() => {
  return Object.values(gpuAssignments.value).filter(assignment => assignment !== 'baremetal').length
})

onMounted(() => {
  // Load server hardware and cluster nodes
  const serverHardware = JSON.parse(sessionStorage.getItem('serverHardware') || '[]')
  const clusterNodes = JSON.parse(sessionStorage.getItem('clusterNodes') || '[]')
  const vmPlan = JSON.parse(sessionStorage.getItem('vmPlan') || '[]')
  
  // Get all GPU-capable baremetal nodes
  const gpuCapableNodes = serverHardware.filter(server => 
    server.hardware?.gpu_detected && 
    server.hardware?.gpu_passthrough_info && 
    server.hardware.gpu_passthrough_info.length > 0
  )
  
  // Create flat list of ALL GPUs (both eligible and non-eligible)
  allGPUs.value = []
  gpuCapableNodes.forEach(server => {
    const node = clusterNodes.find(n => n.hostname === server.hostname)
    const vmsOnHost = vmPlan.filter(vm => vm.host === server.hostname && vm.name !== 'dns')
    
    server.hardware.gpu_passthrough_info.forEach(gpu => {
      allGPUs.value.push({
        address: gpu.pci_address,
        model: server.hardware.gpu_model?.replace(/^\d+x\s*/, '') || 'Unknown GPU',
        hostname: server.hostname,
        iommu_group: gpu.iommu_group,
        driver: gpu.driver || 'none',
        passthrough_eligible: gpu.passthrough_eligible,
        vms: vmsOnHost.map(vm => ({
          name: vm.name,
          role: clusterNodes.find(n => n.hostname === vm.name)?.role || 'worker'
        }))
      })
    })
  })
  
  // Keep legacy gpuNodes for backward compatibility
  gpuNodes.value = gpuCapableNodes.map(server => {
    const node = clusterNodes.find(n => n.hostname === server.hostname)
    const vmsOnHost = vmPlan.filter(vm => vm.host === server.hostname && vm.name !== 'dns')
    
    return {
      hostname: server.hostname,
      role: node?.role || 'unassigned',
      totalGPUs: server.hardware.gpu_count || 0,
      gpus: server.hardware.gpu_passthrough_info.filter(gpu => gpu.passthrough_eligible).map(gpu => ({
        address: gpu.pci_address,
        model: server.hardware.gpu_model?.replace(/^\d+x\s*/, '') || 'Unknown GPU',
        iommu_group: gpu.iommu_group,
        driver: gpu.driver || 'none'
      })),
      vms: vmsOnHost.map(vm => ({
        name: vm.name,
        role: clusterNodes.find(n => n.hostname === vm.name)?.role || 'worker'
      }))
    }
  }).filter(node => node.gpus.length > 0)
  
  // Load existing assignments if any
  const savedAssignments = JSON.parse(sessionStorage.getItem('gpuAssignments') || '{}')
  
  // Initialize assignments with saved values or defaults
  allGPUs.value.forEach(gpu => {
    const key = gpu.address  // Use PCI address as key to match Review component
    if (gpu.passthrough_eligible) {
      if (savedAssignments[key]) {
        gpuAssignments.value[key] = savedAssignments[key]
      } else {
        // Default to baremetal for all eligible GPUs
        gpuAssignments.value[key] = 'baremetal'
      }
    }
    // Non-eligible GPUs don't get assignments since they can't be configured
  })
  
  // If no GPUs available, skip to Review
  if (!hasGPUs.value) {
    setTimeout(() => {
      router.push('/review')
    }, 2000)
  }
})

const goBack = () => {
  router.push('/configuration')
}

const saveAndContinue = () => {
  // Save GPU assignments
  console.log('Saving GPU assignments:', gpuAssignments.value)
  sessionStorage.setItem('gpuAssignments', JSON.stringify(gpuAssignments.value))
  
  // Verify it was saved
  const saved = sessionStorage.getItem('gpuAssignments')
  console.log('Verified saved GPU assignments:', saved)
  
  // Navigate to review
  router.push('/review')
}
</script>