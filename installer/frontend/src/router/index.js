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

// Check for ongoing deployment on every navigation
router.beforeEach((to, from, next) => {
  console.log('Router guard checking navigation to:', to.name)
  
  // Check if there's a saved deployment state
  const deploymentState = localStorage.getItem('thinkube-deployment-state')
  
  if (deploymentState) {
    const state = JSON.parse(deploymentState)
    console.log('Found deployment state:', {
      awaitingRestart: state.awaitingRestart,
      currentPhase: state.currentPhase,
      queueLength: state.queue?.length
    })
    
    // If we're in the middle of a deployment and not already going to deploy page
    if (state.awaitingRestart && to.name !== 'deploy') {
      console.log('Redirecting to deployment page due to awaitingRestart flag')
      next({ name: 'deploy' })
      return
    }
  } else {
    console.log('No deployment state found in localStorage')
  }
  
  // Otherwise, proceed normally
  next()
})

export default router

// 🤖 AI-generated