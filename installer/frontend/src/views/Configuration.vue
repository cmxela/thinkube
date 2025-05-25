<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Cluster Configuration</h1>
    
    <form @submit.prevent="saveAndContinue">
      <!-- Basic Settings -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title mb-4">Basic Settings</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text">Cluster Name</span>
              </label>
              <input 
                v-model="config.clusterName" 
                type="text" 
                placeholder="thinkube" 
                class="input input-bordered"
                :class="{ 'input-error': errors.clusterName }"
                required
              />
              <label v-if="errors.clusterName" class="label">
                <span class="label-text-alt text-error">{{ errors.clusterName }}</span>
              </label>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text">Domain Name</span>
              </label>
              <input 
                v-model="config.domainName" 
                type="text" 
                placeholder="thinkube.local" 
                class="input input-bordered"
                :class="{ 'input-error': errors.domainName }"
                required
              />
              <label v-if="errors.domainName" class="label">
                <span class="label-text-alt text-error">{{ errors.domainName }}</span>
              </label>
            </div>



            <div class="form-control">
              <label class="label">
                <span class="label-text">Cloudflare API Token</span>
                <span class="label-text-alt">For SSL certificate generation</span>
              </label>
              <div class="relative">
                <input 
                  v-model="config.cloudflareToken" 
                  :type="showCloudflareToken ? 'text' : 'password'" 
                  placeholder="Cloudflare API Token" 
                  class="input input-bordered w-full pr-24"
                  :class="{ 'input-error': errors.cloudflareToken, 'input-success': cloudflareVerified }"
                />
                <div class="absolute inset-y-0 right-0 flex items-center pr-3 gap-2">
                  <button 
                    v-if="config.cloudflareToken && config.domainName"
                    type="button"
                    class="btn btn-xs btn-ghost"
                    @click="verifyCloudflare"
                    :disabled="verifyingCloudflare"
                  >
                    <span v-if="verifyingCloudflare" class="loading loading-spinner loading-xs"></span>
                    <span v-else-if="cloudflareVerified" class="text-success">✓</span>
                    <span v-else>Verify</span>
                  </button>
                  <button 
                    type="button"
                    class="flex items-center"
                    @click="showCloudflareToken = !showCloudflareToken"
                  >
                    <svg v-if="showCloudflareToken" class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                    </svg>
                    <svg v-else class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <label v-if="errors.cloudflareToken" class="label">
                <span class="label-text-alt text-error">{{ errors.cloudflareToken }}</span>
              </label>
              <label v-else-if="cloudflareVerified" class="label">
                <span class="label-text-alt text-success">✓ Token has access to {{ config.domainName }}</span>
              </label>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text">ZeroTier Network ID</span>
                <span class="label-text-alt">For overlay networking</span>
              </label>
              <input 
                v-model="config.zerotierNetworkId" 
                type="text" 
                placeholder="16-character network ID" 
                class="input input-bordered"
                :class="{ 'input-error': errors.zerotierNetworkId }"
              />
              <label v-if="errors.zerotierNetworkId" class="label">
                <span class="label-text-alt text-error">{{ errors.zerotierNetworkId }}</span>
              </label>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text">ZeroTier API Token</span>
                <span class="label-text-alt">For node authorization</span>
              </label>
              <div class="relative">
                <input 
                  v-model="config.zerotierApiToken" 
                  :type="showZerotierToken ? 'text' : 'password'" 
                  placeholder="ZeroTier Central API Token" 
                  class="input input-bordered w-full pr-12"
                  :class="{ 'input-error': errors.zerotierApiToken }"
                />
                <button 
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center pr-3"
                  @click="showZerotierToken = !showZerotierToken"
                >
                  <svg v-if="showZerotierToken" class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                  </svg>
                  <svg v-else class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
              </div>
              <label v-if="errors.zerotierApiToken" class="label">
                <span class="label-text-alt text-error">{{ errors.zerotierApiToken }}</span>
              </label>
            </div>

          </div>
        </div>
      </div>

      <!-- Nodes -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between mb-4">
            <h2 class="card-title">Nodes</h2>
            <button type="button" class="btn btn-primary btn-sm gap-2" @click="addNode">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              Add Node
            </button>
          </div>

          <div class="space-y-4">
            <div v-for="(node, index) in config.nodes" :key="index" 
                 class="card bg-base-200 shadow-sm">
              <div class="card-body p-4">
                <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div class="form-control">
                    <label class="label">
                      <span class="label-text text-sm">Hostname</span>
                    </label>
                    <input 
                      v-model="node.hostname" 
                      type="text" 
                      placeholder="tkc" 
                      class="input input-bordered input-sm"
                      required
                    />
                  </div>

                  <div class="form-control">
                    <label class="label">
                      <span class="label-text text-sm">IP Address</span>
                    </label>
                    <input 
                      v-model="node.ipAddress" 
                      type="text" 
                      placeholder="192.168.1.100" 
                      class="input input-bordered input-sm"
                      :class="{ 'input-error': !isValidIP(node.ipAddress) && node.ipAddress }"
                      required
                    />
                  </div>

                  <div class="form-control">
                    <label class="label">
                      <span class="label-text text-sm">Role</span>
                    </label>
                    <select v-model="node.role" class="select select-bordered select-sm">
                      <option value="control_plane">Control Plane</option>
                      <option value="worker">Worker</option>
                    </select>
                  </div>

                  <div class="form-control">
                    <label class="label cursor-pointer">
                      <span class="label-text text-sm">Has GPU</span>
                      <input type="checkbox" v-model="node.hasGpu" class="checkbox checkbox-primary checkbox-sm" />
                    </label>
                  </div>

                  <div class="flex items-end">
                    <button 
                      type="button"
                      class="btn btn-error btn-sm btn-circle"
                      @click="removeNode(index)"
                      :disabled="config.nodes.length === 1"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex justify-between">
        <button type="button" class="btn btn-ghost gap-2" @click="$router.push('/requirements')">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          Back
        </button>
        <button 
          type="submit"
          class="btn btn-primary gap-2"
          :disabled="!isValid"
        >
          Configure Servers
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const config = ref({
  clusterName: 'thinkube',
  domainName: 'my-homelab.com',
  cloudflareToken: '',
  zerotierNetworkId: '',
  zerotierApiToken: '',
  deploymentType: 'lxd',
  nodes: [
    {
      hostname: 'tkc',
      ipAddress: '192.168.1.100',
      role: 'control_plane',
      cpuCores: 8,
      memoryGb: 16,
      hasGpu: false
    }
  ]
})

const errors = ref({
  clusterName: '',
  domainName: '',
  cloudflareToken: '',
  zerotierNetworkId: '',
  zerotierApiToken: ''
})

const showCloudflareToken = ref(false)
const showZerotierToken = ref(false)
const verifyingCloudflare = ref(false)
const cloudflareVerified = ref(false)

// Validation functions
const isValidClusterName = (name) => /^[a-z0-9-]+$/.test(name)
const isValidDomain = (domain) => /^[a-z0-9.-]+$/.test(domain)
const isValidIP = (ip) => /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(ip)

// Watch for changes and validate
watch(() => config.value.clusterName, (val) => {
  errors.value.clusterName = val && !isValidClusterName(val) 
    ? 'Only lowercase letters, numbers, and hyphens' 
    : ''
})

watch(() => config.value.domainName, (val) => {
  errors.value.domainName = val && !isValidDomain(val) 
    ? 'Invalid domain name' 
    : ''
})


const isValid = computed(() => {
  return config.value.clusterName &&
         config.value.domainName &&
         config.value.cloudflareToken &&
         config.value.zerotierNetworkId &&
         config.value.zerotierApiToken &&
         !errors.value.clusterName &&
         !errors.value.domainName &&
         config.value.nodes.every(n => n.hostname && n.ipAddress && isValidIP(n.ipAddress)) &&
         config.value.nodes.filter(n => n.role === 'control_plane').length === 1
})

const addNode = () => {
  config.value.nodes.push({
    hostname: '',
    ipAddress: '',
    role: 'worker',
    cpuCores: 4,
    memoryGb: 8,
    hasGpu: false
  })
}

const removeNode = (index) => {
  config.value.nodes.splice(index, 1)
}

const verifyCloudflare = async () => {
  verifyingCloudflare.value = true
  cloudflareVerified.value = false
  errors.value.cloudflareToken = ''
  
  try {
    const response = await axios.post('/api/verify-cloudflare', {
      token: config.value.cloudflareToken,
      domain: config.value.domainName
    })
    
    if (response.data.valid) {
      cloudflareVerified.value = true
      errors.value.cloudflareToken = ''
    } else {
      errors.value.cloudflareToken = response.data.message || 'Token does not have access to this domain'
      cloudflareVerified.value = false
    }
  } catch (error) {
    errors.value.cloudflareToken = error.response?.data?.detail || 'Failed to verify Cloudflare token'
    cloudflareVerified.value = false
  } finally {
    verifyingCloudflare.value = false
  }
}

// Reset verification when token or domain changes
watch([() => config.value.cloudflareToken, () => config.value.domainName], () => {
  cloudflareVerified.value = false
  errors.value.cloudflareToken = ''
})

const saveAndContinue = () => {
  if (isValid.value) {
    // Get the already-verified sudo password from sessionStorage
    const sudoPassword = sessionStorage.getItem('sudoPassword')
    
    // Save config including sudo password (will be used as ANSIBLE_SUDO_PASS)
    const configToSave = {
      ...config.value,
      sudoPassword: sudoPassword
    }
    localStorage.setItem('thinkube-config', JSON.stringify(configToSave))
    router.push('/review')
  }
}
</script>