<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="mb-4">Review Configuration</h1>
        
        <v-alert type="info" variant="tonal" class="mb-4">
          Please review your configuration before proceeding with the installation.
        </v-alert>

        <v-card class="mb-4">
          <v-card-title>Cluster Settings</v-card-title>
          <v-card-text>
            <v-simple-table>
              <template v-slot:default>
                <tbody>
                  <tr>
                    <td><strong>Cluster Name</strong></td>
                    <td>{{ config.clusterName }}</td>
                  </tr>
                  <tr>
                    <td><strong>Domain Name</strong></td>
                    <td>{{ config.domainName }}</td>
                  </tr>
                  <tr>
                    <td><strong>Admin Username</strong></td>
                    <td>{{ config.adminUsername }}</td>
                  </tr>
                  <tr>
                    <td><strong>Deployment Type</strong></td>
                    <td>{{ config.deploymentType }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>Nodes ({{ config.nodes.length }})</v-card-title>
          <v-card-text>
            <v-simple-table>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Role</th>
                    <th>GPU</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="node in config.nodes" :key="node.hostname">
                    <td>{{ node.hostname }}</td>
                    <td>{{ node.ipAddress }}</td>
                    <td>
                      <v-chip size="small" :color="node.role === 'control_plane' ? 'primary' : 'secondary'">
                        {{ node.role }}
                      </v-chip>
                    </td>
                    <td>
                      <v-icon :color="node.hasGpu ? 'success' : 'grey'">
                        {{ node.hasGpu ? 'mdi-check' : 'mdi-close' }}
                      </v-icon>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>Generated Inventory Preview</v-card-title>
          <v-card-text>
            <pre class="inventory-preview">{{ inventoryPreview }}</pre>
          </v-card-text>
        </v-card>

        <div class="d-flex justify-space-between">
          <v-btn @click="$router.push('/configuration')" variant="text">
            <v-icon start>mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-btn 
            color="primary" 
            @click="startInstallation"
            size="large"
          >
            Start Installation
            <v-icon end>mdi-rocket-launch</v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const config = ref({})
const inventoryPreview = ref('')

const backendUrl = computed(() => {
  if (window.electronAPI) {
    return window.electronAPI.getBackendURL()
  }
  return '/api'
})

onMounted(async () => {
  // Load config from localStorage
  const savedConfig = localStorage.getItem('thinkube-config')
  if (savedConfig) {
    config.value = JSON.parse(savedConfig)
    
    // Get inventory preview from backend
    try {
      const response = await axios.post(`${backendUrl.value}/generate-inventory`, config.value)
      inventoryPreview.value = response.data.inventory
    } catch (error) {
      console.error('Failed to generate inventory preview:', error)
    }
  } else {
    router.push('/configuration')
  }
})

const startInstallation = async () => {
  try {
    await axios.post(`${backendUrl.value}/install`, config.value)
    router.push('/deploy')
  } catch (error) {
    console.error('Failed to start installation:', error)
  }
}
</script>

<style scoped>
.inventory-preview {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.9rem;
}
</style>