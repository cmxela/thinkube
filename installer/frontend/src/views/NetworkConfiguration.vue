<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Network Configuration</h1>
    
    <!-- Network Overview -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Network Overview</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Local Network CIDR</span>
              <span class="label-text-alt">Auto-discovered during setup</span>
            </label>
            <input 
              v-model="networkConfig.cidr" 
              type="text" 
              class="input input-bordered input-disabled"
              readonly
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">Gateway IP</span>
              <span class="label-text-alt">Auto-discovered (last octet editable)</span>
            </label>
            <div class="flex items-center gap-1">
              <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.cidr) }}.</span>
              <input 
                :value="getLastOctet(networkConfig.gateway)"
                @input="networkConfig.gateway = setLastOctet(getNetworkBase(networkConfig.cidr), $event.target.value)"
                type="number" 
                min="1" 
                max="254"
                class="input input-bordered input-sm w-16"
                :class="{ 'input-error': !isValidIP(networkConfig.gateway) }"
              />
            </div>
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">ZeroTier CIDR</span>
              <span class="label-text-alt">Auto-retrieved from your network</span>
            </label>
            <input 
              v-model="networkConfig.zerotierCIDR" 
              type="text" 
              class="input input-bordered input-disabled"
              readonly
            />
          </div>
          
          <div v-if="virtualMachines.length > 0" class="form-control">
            <label class="label">
              <span class="label-text">LXD Internal Network</span>
              <span class="label-text-alt">Auto-configured by Thinkube</span>
            </label>
            <input 
              v-model="networkConfig.lxdIPv4Address" 
              type="text" 
              class="input input-bordered input-disabled"
              readonly
              placeholder="192.168.100.1/24"
            />
          </div>
        </div>
        
        <div v-if="zerotierLoading" class="flex items-center gap-3 mt-4">
          <span class="loading loading-spinner loading-sm"></span>
          <span class="text-sm">Fetching ZeroTier network details...</span>
        </div>
        
        <div v-if="zerotierError" class="alert alert-error mt-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <div class="font-bold">Failed to fetch ZeroTier network</div>
            <div class="text-sm">{{ zerotierError }}</div>
          </div>
        </div>
        
        <div v-if="zerotierNetworkName" class="alert alert-info mt-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <div>
            <div class="font-bold">Networks Configured</div>
            <div class="text-sm">ZeroTier: {{ zerotierNetworkName }} • LXD Bridge: lxdbr0 • IPs auto-assigned below</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ingress IP Configuration -->
    <div v-if="networkConfig.zerotierCIDR" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Ingress IP Configuration</h2>
        
        <div class="alert alert-info mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <div class="font-bold">MetalLB Load Balancer IPs</div>
            <div class="text-sm">These IPs will be reserved on the ZeroTier network for Kubernetes ingress services</div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Primary Ingress IP</span>
              <span class="label-text-alt">For main services</span>
            </label>
            <div class="flex items-center gap-1">
              <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.zerotierCIDR) }}.</span>
              <input 
                v-model="networkConfig.primaryIngressOctet"
                type="number" 
                min="1" 
                max="254"
                placeholder="200"
                class="input input-bordered input-sm w-20"
                :class="{ 
                  'input-error': !isValidIngressOctet(networkConfig.primaryIngressOctet),
                  'input-warning': isIngressIPInUse(networkConfig.primaryIngressOctet)
                }"
              />
            </div>
            <div v-if="isIngressIPInUse(networkConfig.primaryIngressOctet)" class="text-xs text-warning mt-1">
              This IP is already assigned to a ZeroTier member
            </div>
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">Secondary Ingress IP</span>
              <span class="label-text-alt">For Knative services</span>
            </label>
            <div class="flex items-center gap-1">
              <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.zerotierCIDR) }}.</span>
              <input 
                v-model="networkConfig.secondaryIngressOctet"
                type="number" 
                min="1" 
                max="254"
                placeholder="201"
                class="input input-bordered input-sm w-20"
                :class="{ 
                  'input-error': !isValidIngressOctet(networkConfig.secondaryIngressOctet),
                  'input-warning': isIngressIPInUse(networkConfig.secondaryIngressOctet)
                }"
              />
            </div>
            <div v-if="isIngressIPInUse(networkConfig.secondaryIngressOctet)" class="text-xs text-warning mt-1">
              This IP is already assigned to a ZeroTier member
            </div>
          </div>
        </div>
        
        <div v-if="networkConfig.primaryIngressOctet && networkConfig.secondaryIngressOctet" class="mt-4">
          <div class="text-sm text-base-content/70">
            <p>Reserved IPs:</p>
            <ul class="list-disc list-inside ml-2">
              <li>Primary: {{ getNetworkBase(networkConfig.zerotierCIDR) }}.{{ networkConfig.primaryIngressOctet }}</li>
              <li>Secondary: {{ getNetworkBase(networkConfig.zerotierCIDR) }}.{{ networkConfig.secondaryIngressOctet }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Baremetal Servers -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Baremetal Servers</h2>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>Hostname</th>
                <th>LAN IP</th>
                <th>ZeroTier IP</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(server, idx) in physicalServers" :key="server.hostname">
                <td class="font-medium">{{ server.hostname }}</td>
                <td>
                  <div class="flex items-center gap-1">
                    <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.cidr) }}.</span>
                    <input 
                      :value="getLastOctet(server.ip)"
                      @input="server.ip = setLastOctet(getNetworkBase(networkConfig.cidr), $event.target.value)"
                      type="number" 
                      min="1" 
                      max="254"
                      class="input input-bordered input-sm w-16"
                      :class="{ 'input-error': !isValidIP(server.ip) }"
                    />
                  </div>
                </td>
                <td>
                  <div>
                    <div class="flex items-center gap-1">
                      <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.zerotierCIDR) }}.</span>
                      <input 
                        :value="getLastOctet(server.zerotierIP)"
                        @input="server.zerotierIP = setLastOctet(getNetworkBase(networkConfig.zerotierCIDR), $event.target.value)"
                        type="number" 
                        min="1" 
                        max="254"
                        class="input input-bordered input-sm w-16"
                        :class="{ 
                          'input-error': !isValidIP(server.zerotierIP) || isZeroTierIPInUse(server.zerotierIP),
                          'input-warning': isZeroTierIPInUse(server.zerotierIP)
                        }"
                        :disabled="!networkConfig.zerotierCIDR"
                      />
                    </div>
                    <div v-if="isZeroTierIPInUse(server.zerotierIP)" class="text-xs text-warning mt-1">
                      {{ getZeroTierIPStatus(server.zerotierIP) }}
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge badge-outline">{{ getServerRole(server.hostname) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Virtual Machines -->
    <div v-if="virtualMachines.length > 0" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Virtual Machines</h2>
        
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>VM Name</th>
                <th>Host</th>
                <th>LAN IP</th>
                <th>Internal IP</th>
                <th>ZeroTier IP</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vm, idx) in virtualMachines" :key="vm.name">
                <td class="font-medium">{{ vm.name }}</td>
                <td>{{ vm.host }}</td>
                <td>
                  <div class="flex items-center gap-1">
                    <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.cidr) }}.</span>
                    <input 
                      :value="getLastOctet(vm.lanIP)"
                      @input="vm.lanIP = setLastOctet(getNetworkBase(networkConfig.cidr), $event.target.value)"
                      type="number" 
                      min="1" 
                      max="254"
                      class="input input-bordered input-sm w-16"
                      :class="{ 'input-error': !isValidIP(vm.lanIP) }"
                    />
                  </div>
                </td>
                <td>
                  <div class="flex items-center gap-1">
                    <span class="text-sm text-base-content/70">{{ getLXDBase() }}.</span>
                    <input 
                      :value="getLastOctet(vm.internalIP)"
                      @input="vm.internalIP = setLastOctet(getLXDBase(), $event.target.value)"
                      type="number" 
                      min="1" 
                      max="254"
                      class="input input-bordered input-sm w-16"
                      :class="{ 'input-error': !isValidIP(vm.internalIP) }"
                    />
                  </div>
                </td>
                <td>
                  <div>
                    <div class="flex items-center gap-1">
                      <span class="text-sm text-base-content/70">{{ getNetworkBase(networkConfig.zerotierCIDR) }}.</span>
                      <input 
                        :value="getLastOctet(vm.zerotierIP)"
                        @input="vm.zerotierIP = setLastOctet(getNetworkBase(networkConfig.zerotierCIDR), $event.target.value)"
                        type="number" 
                        min="1" 
                        max="254"
                        class="input input-bordered input-sm w-16"
                        :class="{ 
                          'input-error': !isValidIP(vm.zerotierIP) || isZeroTierIPInUse(vm.zerotierIP),
                          'input-warning': isZeroTierIPInUse(vm.zerotierIP)
                        }"
                        :disabled="!networkConfig.zerotierCIDR"
                      />
                    </div>
                    <div v-if="isZeroTierIPInUse(vm.zerotierIP)" class="text-xs text-warning mt-1">
                      {{ getZeroTierIPStatus(vm.zerotierIP) }}
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="vm.role === 'control_plane' ? 'badge-primary' : 'badge-secondary'">
                    {{ vm.role === 'control_plane' ? 'Control Plane' : vm.role === 'worker' ? 'Worker' : vm.role }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>



    <!-- IP Conflict Detection -->
    <div v-if="ipConflicts.length > 0" class="alert alert-warning mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <h3 class="font-bold">IP Address Conflicts Detected</h3>
        <ul class="text-sm mt-1">
          <li v-for="conflict in ipConflicts" :key="conflict">{{ conflict }}</li>
        </ul>
      </div>
    </div>

    <!-- Validation Summary -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Configuration Summary</h2>
        
        <div class="stats stats-vertical lg:stats-horizontal shadow">
          <div class="stat">
            <div class="stat-title">Baremetal Servers</div>
            <div class="stat-value text-primary">{{ physicalServers.length }}</div>
            <div class="stat-desc">{{ physicalServers.filter(s => isValidIP(s.ip)).length }} with valid IPs</div>
          </div>
          
          <div class="stat">
            <div class="stat-title">Virtual Machines</div>
            <div class="stat-value text-secondary">{{ virtualMachines.length }}</div>
            <div class="stat-desc">{{ virtualMachines.filter(v => isValidIP(v.lanIP)).length }} with valid LAN IPs</div>
          </div>
          
          <div class="stat">
            <div class="stat-title">IP Conflicts</div>
            <div class="stat-value" :class="ipConflicts.length > 0 ? 'text-error' : 'text-success'">
              {{ ipConflicts.length }}
            </div>
            <div class="stat-desc">{{ ipConflicts.length === 0 ? 'No conflicts' : 'Need resolution' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-between">
      <button class="btn btn-ghost gap-2" @click="$router.push('/configuration')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Back to Configuration
      </button>
      
      <button 
        class="btn btn-primary gap-2"
        @click="saveAndContinue"
        :disabled="!isConfigurationValid"
      >
        Continue to GPU Assignment
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { generateDynamicInventory, inventoryToYAML } from '../utils/inventoryGenerator.js'
import axios from 'axios'

const router = useRouter()

// State
const networkConfig = ref({
  cidr: '192.168.1.0/24',
  gateway: '192.168.1.1',
  zerotierCIDR: '',  // Will be fetched from ZeroTier API
  lxdIPv4Address: '',  // Auto-configured by LXD snap
  primaryIngressOctet: '200',  // Default primary ingress IP octet
  secondaryIngressOctet: '201'  // Default secondary ingress IP octet
})

const physicalServers = ref([])
const virtualMachines = ref([])

// ZeroTier API state
const zerotierLoading = ref(false)
const zerotierError = ref('')
const zerotierNetworkName = ref('')
const zerotierUsedIPs = ref([])
const zerotierMembers = ref([])

// Computed
const ipConflicts = computed(() => {
  const conflicts = []
  const allIPs = []
  
  // Collect all IPs
  physicalServers.value.forEach(server => {
    if (server.ip) allIPs.push(server.ip)
    if (server.zerotierIP) allIPs.push(server.zerotierIP)
  })
  
  virtualMachines.value.forEach(vm => {
    if (vm.lanIP) allIPs.push(vm.lanIP)
    if (vm.internalIP) allIPs.push(vm.internalIP)
    if (vm.zerotierIP) allIPs.push(vm.zerotierIP)
  })
  
  // Check for duplicates
  const ipCounts = {}
  allIPs.forEach(ip => {
    if (ip && isValidIP(ip)) {
      ipCounts[ip] = (ipCounts[ip] || 0) + 1
    }
  })
  
  Object.entries(ipCounts).forEach(([ip, count]) => {
    if (count > 1) {
      conflicts.push(`IP ${ip} is assigned ${count} times`)
    }
  })
  
  // Check for ZeroTier conflicts
  allIPs.forEach(ip => {
    if (ip && isZeroTierIPInUse(ip) && ip.startsWith(getNetworkBase(networkConfig.value.zerotierCIDR))) {
      const status = getZeroTierIPStatus(ip)
      if (status) {
        conflicts.push(`ZeroTier IP ${ip}: ${status}`)
      }
    }
  })
  
  return conflicts
})

const isConfigurationValid = computed(() => {
  // All IPs must be valid and no conflicts
  const allServersValid = physicalServers.value.every(s => 
    isValidIP(s.ip) && isValidIP(s.zerotierIP)
  )
  
  const allVMsValid = virtualMachines.value.every(v => 
    isValidIP(v.lanIP) && isValidIP(v.internalIP) && isValidIP(v.zerotierIP)
  )
  
  const networkValid = isValidIP(networkConfig.value.gateway) && 
                      networkConfig.value.cidr &&
                      networkConfig.value.zerotierCIDR
  
  // LXD configuration is auto-generated, so always valid
  
  return allServersValid && allVMsValid && networkValid && ipConflicts.value.length === 0
})

// Methods
const isValidIP = (ip) => {
  if (!ip) return false
  const regex = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/
  if (!regex.test(ip)) return false
  
  const parts = ip.split('.')
  return parts.every(part => {
    const num = parseInt(part, 10)
    return num >= 0 && num <= 255
  })
}

const getNetworkBase = (cidr) => {
  if (!cidr) return ''
  return cidr.split('/')[0].split('.').slice(0, 3).join('.')
}

const getLastOctet = (ip) => {
  if (!ip) return ''
  return ip.split('.').pop()
}

const setLastOctet = (baseNetwork, octet) => {
  if (!baseNetwork || !octet) return ''
  return `${baseNetwork}.${octet}`
}

const isZeroTierIPInUse = (ip) => {
  return zerotierUsedIPs.value.includes(ip)
}

const getZeroTierIPStatus = (ip) => {
  if (!ip) return ''
  if (isZeroTierIPInUse(ip)) {
    const member = zerotierMembers.value.find(m => m.ipAssignments.includes(ip))
    return member ? `Used by ${member.name || member.nodeId.substring(0, 10)}` : 'Already in use'
  }
  return ''
}

const isValidIngressOctet = (octet) => {
  if (!octet) return false
  const num = parseInt(octet, 10)
  return num >= 1 && num <= 254
}

const isIngressIPInUse = (octet) => {
  if (!octet || !networkConfig.value.zerotierCIDR) return false
  const fullIP = `${getNetworkBase(networkConfig.value.zerotierCIDR)}.${octet}`
  return isZeroTierIPInUse(fullIP)
}

const getLXDBase = () => {
  if (!networkConfig.value.cidr) return '192.168.100'
  const localBase = networkConfig.value.cidr.split('/')[0].split('.').slice(0, 2).join('.')
  return `${localBase}.100`
}

const getServerRole = (hostname) => {
  const clusterNodes = JSON.parse(sessionStorage.getItem('clusterNodes') || '[]')
  const node = clusterNodes.find(n => n.hostname === hostname && n.type === 'baremetal')
  return node ? (node.role === 'control_plane' ? 'Control Plane' : 'Worker') : 'LXD Host'
}

const assignZeroTierIPs = () => {
  if (!networkConfig.value.zerotierCIDR) return
  
  // Extract base from ZeroTier CIDR (e.g., "192.168.191.0/24" -> "192.168.191")
  const zerotierBase = networkConfig.value.zerotierCIDR.split('/')[0].split('.').slice(0, 3).join('.')
  
  // Create a set of used IPs for quick lookup
  const usedIPSet = new Set(zerotierUsedIPs.value)
  
  // Function to find next available IP
  const findNextAvailableIP = (startFrom = 10) => {
    let counter = startFrom
    while (counter < 254) {
      const testIP = `${zerotierBase}.${counter}`
      if (!usedIPSet.has(testIP)) {
        usedIPSet.add(testIP) // Mark as used for next iteration
        return testIP
      }
      counter++
    }
    return null // No available IPs
  }
  
  // Assign to physical servers
  physicalServers.value.forEach(server => {
    if (!server.zerotierIP || usedIPSet.has(server.zerotierIP)) {
      const newIP = findNextAvailableIP()
      if (newIP) {
        server.zerotierIP = newIP
      } else {
        zerotierError.value = 'No available ZeroTier IPs'
      }
    }
  })
  
  // Assign to VMs
  virtualMachines.value.forEach(vm => {
    if (!vm.zerotierIP || usedIPSet.has(vm.zerotierIP)) {
      const newIP = findNextAvailableIP()
      if (newIP) {
        vm.zerotierIP = newIP
      } else {
        zerotierError.value = 'No available ZeroTier IPs'
      }
    }
  })
}

const fetchZeroTierMembers = async (config) => {
  try {
    const response = await axios.post('/api/fetch-zerotier-members', {
      network_id: config.zerotierNetworkId,
      api_token: config.zerotierApiToken
    })
    
    if (response.data.success) {
      zerotierMembers.value = response.data.members
      zerotierUsedIPs.value = response.data.used_ips
      console.log(`Found ${response.data.members.length} ZeroTier members with ${response.data.used_ips.length} used IPs`)
    }
  } catch (error) {
    console.error('Failed to fetch ZeroTier members:', error)
  }
}

const fetchZeroTierNetwork = async () => {
  const config = JSON.parse(localStorage.getItem('thinkube-config') || '{}')
  
  if (!config.zerotierNetworkId || !config.zerotierApiToken) {
    zerotierError.value = 'ZeroTier network ID and API token are required'
    return
  }
  
  zerotierLoading.value = true
  zerotierError.value = ''
  zerotierNetworkName.value = ''
  
  try {
    // Fetch network info and members in parallel
    const [networkResponse] = await Promise.all([
      axios.post('/api/fetch-zerotier-network', {
        network_id: config.zerotierNetworkId,
        api_token: config.zerotierApiToken
      }),
      fetchZeroTierMembers(config)
    ])
    
    if (networkResponse.data.success) {
      networkConfig.value.zerotierCIDR = networkResponse.data.cidr
      zerotierNetworkName.value = networkResponse.data.network_name
      zerotierError.value = ''
      
      // Now assign ZeroTier IPs using the actual CIDR and avoiding used IPs
      assignZeroTierIPs()
    } else {
      zerotierError.value = networkResponse.data.message
      networkConfig.value.zerotierCIDR = ''
    }
  } catch (error) {
    zerotierError.value = error.response?.data?.message || 'Failed to connect to ZeroTier API'
    networkConfig.value.zerotierCIDR = ''
  } finally {
    zerotierLoading.value = false
  }
}

const generateDefaultIPs = () => {
  const networkBase = networkConfig.value.cidr.split('/')[0].split('.').slice(0, 3).join('.')
  
  // Find highest used IP in physical servers
  const usedIPs = physicalServers.value.map(s => parseInt(s.ip.split('.').pop())).filter(Boolean)
  let vmIPCounter = Math.max(...usedIPs, 50) + 10
  
  // Assign VM LAN IPs
  virtualMachines.value.forEach(vm => {
    if (!vm.lanIP || !isValidIP(vm.lanIP)) {
      vm.lanIP = `${networkBase}.${vmIPCounter++}`
    }
  })
  
  // Generate LXD internal network based on local network CIDR
  // This keeps them in the same address family while avoiding conflicts
  if (virtualMachines.value.length > 0 && networkConfig.value.cidr) {
    const localBase = networkConfig.value.cidr.split('/')[0].split('.').slice(0, 2).join('.')
    const lxdBase = `${localBase}.100`  // Use .100 as safe offset from local network
    const lxdNetwork = `${lxdBase}.1/24`
    
    // Assign VM internal IPs from calculated LXD range
    let internalCounter = 10
    virtualMachines.value.forEach(vm => {
      if (!vm.internalIP || !isValidIP(vm.internalIP)) {
        vm.internalIP = `${lxdBase}.${internalCounter++}`
      }
    })
    
    // Set value for LXD network (no comments in the value!)
    networkConfig.value.lxdIPv4Address = lxdNetwork
  }
  
  // Ingress IP will be configured later with MicroK8s
}


const saveAndContinue = () => {
  // Save network configuration
  sessionStorage.setItem('networkConfiguration', JSON.stringify({
    networkConfig: networkConfig.value,
    physicalServers: physicalServers.value,
    virtualMachines: virtualMachines.value
  }))
  
  // Also generate and save the final inventory for later use
  try {
    const inventory = generateDynamicInventory()
    const inventoryYAML = inventoryToYAML(inventory)
    sessionStorage.setItem('generatedInventory', inventoryYAML)
  } catch (error) {
    console.error('Failed to generate inventory:', error)
  }
  
  router.push('/gpu-assignment')
}

// Watch for changes and validate (simplified)
watch([physicalServers, virtualMachines, networkConfig], () => {
  // Any additional validation logic can go here
}, { deep: true })

// Lifecycle
onMounted(async () => {
  // Load data from previous steps
  const serverHardware = JSON.parse(sessionStorage.getItem('serverHardware') || '[]')
  const vmPlan = JSON.parse(sessionStorage.getItem('vmPlan') || '[]')
  const clusterNodes = JSON.parse(sessionStorage.getItem('clusterNodes') || '[]')
  const networkCIDR = sessionStorage.getItem('networkCIDR') || '192.168.1.0/24'
  
  // Set network configuration
  networkConfig.value.cidr = networkCIDR
  const networkBase = networkCIDR.split('/')[0].split('.').slice(0, 3).join('.')
  networkConfig.value.gateway = `${networkBase}.1`
  
  // Fetch ZeroTier network details automatically
  await fetchZeroTierNetwork()
  
  if (vmPlan.length > 0) {
    // Auto-generate LXD IPv4 network based on VM internal IPs (192.168.100.x)
    networkConfig.value.lxdIPv4Address = '192.168.100.1/24'
    // No IPv6 configuration needed since we don't assign IPv6 to VMs
  }
  
  // Load physical servers (ZeroTier IPs will be assigned after fetching CIDR)
  physicalServers.value = serverHardware.map(server => ({
    hostname: server.hostname,
    ip: server.ip || server.ip_address,
    zerotierIP: ''  // Will be assigned after ZeroTier CIDR is fetched
  }))
  
  // Load virtual machines (ZeroTier IPs will be assigned after fetching CIDR)
  virtualMachines.value = vmPlan.map((vm, idx) => {
    const clusterNode = clusterNodes.find(n => n.hostname === vm.name)
    return {
      name: vm.name,
      host: vm.host,
      lanIP: '',  // Will be auto-assigned
      internalIP: '',  // Will be auto-assigned
      zerotierIP: '',  // Will be assigned after ZeroTier CIDR is fetched
      role: clusterNode?.role || 'unknown'
    }
  })
  
  // Generate default IP assignments (after ZeroTier CIDR is available)
  generateDefaultIPs()
  
  // Load saved configuration if exists
  const savedConfig = sessionStorage.getItem('networkConfiguration')
  if (savedConfig) {
    const parsed = JSON.parse(savedConfig)
    networkConfig.value = { ...networkConfig.value, ...parsed.networkConfig }
    if (parsed.physicalServers) physicalServers.value = parsed.physicalServers
    if (parsed.virtualMachines) virtualMachines.value = parsed.virtualMachines
  }
  
  // After loading/creating data, assign ZeroTier IPs if we have CIDR
  if (networkConfig.value.zerotierCIDR) {
    assignZeroTierIPs()
  }
})
</script>