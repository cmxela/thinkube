import { createRouter, createWebHistory } from 'vue-router'
import Welcome from '../views/Welcome.vue'
import Requirements from '../views/Requirements.vue'
import SudoPassword from '../views/SudoPassword.vue'
import Installation from '../views/Installation.vue'
import ServerDiscovery from '../views/ServerDiscovery.vue'
import SSHSetup from '../views/SSHSetup.vue'
import HardwareDetection from '../views/HardwareDetection.vue'
import VMPlanning from '../views/VMPlanning.vue'
import RoleAssignment from '../views/RoleAssignment.vue'
import Configuration from '../views/Configuration.vue'
import NetworkConfiguration from '../views/NetworkConfiguration.vue'
import GPUAssignment from '../views/GPUAssignment.vue'
import Review from '../views/Review.vue'
import Deploy from '../views/Deploy.vue'
import Complete from '../views/Complete.vue'

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: Welcome
  },
  {
    path: '/requirements',
    name: 'requirements',
    component: Requirements
  },
  {
    path: '/sudo-password',
    name: 'sudo-password',
    component: SudoPassword
  },
  {
    path: '/installation',
    name: 'installation',
    component: Installation
  },
  {
    path: '/server-discovery',
    name: 'server-discovery',
    component: ServerDiscovery
  },
  {
    path: '/ssh-setup',
    name: 'ssh-setup',
    component: SSHSetup
  },
  {
    path: '/hardware-detection',
    name: 'hardware-detection',
    component: HardwareDetection
  },
  {
    path: '/vm-planning',
    name: 'vm-planning',
    component: VMPlanning
  },
  {
    path: '/role-assignment',
    name: 'role-assignment',
    component: RoleAssignment
  },
  {
    path: '/configuration',
    name: 'configuration',
    component: Configuration
  },
  {
    path: '/network-configuration',
    name: 'network-configuration',
    component: NetworkConfiguration
  },
  {
    path: '/gpu-assignment',
    name: 'gpu-assignment',
    component: GPUAssignment
  },
  {
    path: '/review',
    name: 'review',
    component: Review
  },
  {
    path: '/deploy',
    name: 'deploy',
    component: Deploy
  },
  {
    path: '/complete',
    name: 'complete',
    component: Complete
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

// 🤖 AI-generated