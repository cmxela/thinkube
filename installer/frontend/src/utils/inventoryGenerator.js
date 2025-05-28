/**
 * Dynamic Inventory Generator for Thinkube Installer
 * Generates Ansible inventory based on user configuration with dynamic network allocation
 */

export function generateDynamicInventory() {
  // Get all configuration from sessionStorage and localStorage
  const config = JSON.parse(localStorage.getItem('thinkube-config') || '{}')
  const networkConfiguration = JSON.parse(sessionStorage.getItem('networkConfiguration') || '{}')
  const clusterNodes = JSON.parse(sessionStorage.getItem('clusterNodes') || '[]')
  const vmPlan = JSON.parse(sessionStorage.getItem('vmPlan') || '[]')  // Original VM specs
  const gpuAssignments = JSON.parse(sessionStorage.getItem('gpuAssignments') || '{}')  // GPU assignments from Review
  const dnsOption = sessionStorage.getItem('dnsOption')
  const lxdPrimary = sessionStorage.getItem('lxdPrimary')
  const deploymentType = sessionStorage.getItem('deploymentType')
  
  // Validate required configuration exists
  if (!networkConfiguration.networkConfig) {
    throw new Error('Network configuration is required. Please complete the network configuration step.')
  }
  
  if (!networkConfiguration.physicalServers || networkConfiguration.physicalServers.length === 0) {
    throw new Error('Baremetal server configuration is required.')
  }
  
  if (!config.domainName) {
    throw new Error('Domain name is required.')
  }
  
  if (!config.zerotierNetworkId) {
    throw new Error('ZeroTier network ID is required.')
  }
  
  if (!config.zerotierApiToken) {
    throw new Error('ZeroTier API token is required.')
  }
  
  const networkConfig = networkConfiguration.networkConfig
  const configuredPhysicalServers = networkConfiguration.physicalServers
  const configuredVirtualMachines = networkConfiguration.virtualMachines || []
  
  // Helper function to check if VM has GPU passthrough
  const vmHasGPUPassthrough = (vmHostname) => {
    return Object.values(gpuAssignments).includes(vmHostname)
  }
  
  // Validate required network configuration
  if (!networkConfig.cidr) {
    throw new Error('Network CIDR is required.')
  }
  
  if (!networkConfig.gateway) {
    throw new Error('Network gateway is required.')
  }
  
  if (!networkConfig.zerotierCIDR) {
    throw new Error('ZeroTier CIDR is required.')
  }
  
  // Build inventory structure
  const inventory = {
    all: {
      vars: {
        // Global variables from user configuration
        domain_name: config.domainName,
        admin_username: 'tkadmin',
        system_username: 'thinkube',
        auth_realm_username: 'thinkube',
        ansible_python_interpreter: '/home/thinkube/.venv/bin/python3',
        ansible_become_pass: "{{ lookup('env', 'ANSIBLE_SUDO_PASS') }}",
        home: "{{ lookup('env', 'HOME') }}",
        
        // Network configuration (user-provided values only)
        network_cidr: networkConfig.cidr,
        network_gateway: networkConfig.gateway,
        zerotier_network_id: config.zerotierNetworkId,
        zerotier_api_token: config.zerotierApiToken,
        zerotier_cidr: networkConfig.zerotierCIDR,
        dns_servers: ["8.8.8.8", "8.8.4.4"],
        
        // LXD configuration (hardcoded bridge name, auto-generated IPv4 network)
        lxd_network_name: "lxdbr0",  // Hardcoded in playbooks
        lxd_network_ipv4_address: networkConfig.lxdIPv4Address || "192.168.100.1/24",
        lxd_network_ipv6_address: "none",  // No IPv6 since we don't assign IPv6 to VMs
        
        // Kubernetes configuration (will be configured later with MicroK8s)
        
        // Cloudflare configuration
        cloudflare_token: config.cloudflareToken
      },
      children: {
        // Physical servers (baremetal)
        baremetal: {
          hosts: {}
        },
        
        // LXD cluster configuration
        lxd_cluster: {
          children: {
            lxd_primary: {
              hosts: {}
            },
            lxd_secondary: {
              hosts: {}
            }
          }
        },
        
        // DNS servers
        dns: {
          hosts: {}
        },
        
        // MicroK8s groups
        microk8s: {
          children: {
            microk8s_control_plane: {
              hosts: {}
            },
            microk8s_workers: {
              hosts: {}
            }
          }
        },
        
        // LXD containers/VMs
        lxd_containers: {
          vars: {
            lxd_image: "ubuntu:24.04",
            ansible_python_interpreter: "/home/thinkube/.venv/bin/python3"
          },
          children: {
            dns_containers: {
              hosts: {}
            },
            microk8s_containers: {
              children: {
                controllers: {
                  hosts: {}
                },
                workers: {
                  hosts: {}
                }
              }
            }
          }
        }
      }
    }
  }
  
  // Add baremetal servers from network configuration
  configuredPhysicalServers.forEach(server => {
    const hostname = server.hostname
    const serverDef = {
      ansible_host: server.ip,
      lan_ip: server.ip,
      zerotier_ip: server.zerotierIP,
      arch: 'x86_64',
      zerotier_enabled: true
    }
    
    // Special handling for local connection
    if (hostname === 'bcn1') {
      serverDef.ansible_connection = 'local'
    }
    
    // Determine if this host needs GPU passthrough configuration
    const gpuAssignments = JSON.parse(sessionStorage.getItem('gpuAssignments') || '{}')
    const assignedSlots = []
    
    // Find GPUs assigned to VMs on this host
    Object.entries(gpuAssignments).forEach(([pciAddress, assignment]) => {
      if (assignment !== 'baremetal' && configuredVirtualMachines.some(vm => vm.host === hostname && vm.name === assignment)) {
        // This GPU is assigned to a VM on this host
        assignedSlots.push(pciAddress)
      }
    })
    
    const hasGPUPassthrough = assignedSlots.length > 0
    serverDef.configure_gpu_passthrough = hasGPUPassthrough
    
    // Add assigned PCI slots if any
    if (hasGPUPassthrough) {
      serverDef.assigned_pci_slots = assignedSlots
    }
    
    // Add to inventory
    inventory.all.children.baremetal.hosts[hostname] = serverDef
  })
  
  // Configure LXD cluster groups
  if (deploymentType !== 'baremetal-only' && lxdPrimary) {
    inventory.all.children.lxd_cluster.children.lxd_primary.hosts[lxdPrimary] = {}
    
    // Add other servers with VMs as secondary nodes
    configuredPhysicalServers.forEach(server => {
      if (server.hostname !== lxdPrimary && configuredVirtualMachines.some(vm => vm.host === server.hostname)) {
        inventory.all.children.lxd_cluster.children.lxd_secondary.hosts[server.hostname] = {}
      }
    })
  }
  
  // Add DNS configuration
  if (dnsOption === 'baremetal') {
    // Find baremetal DNS server from clusterNodes
    const dnsNode = clusterNodes.find(n => n.role === 'dns' && n.type === 'baremetal')
    if (dnsNode) {
      inventory.all.children.dns.hosts[dnsNode.hostname] = {}
    }
  } else if (dnsOption === 'vm') {
    // VM-based DNS - merge original VM specs with network config
    const originalDnsVM = vmPlan.find(vm => vm.name === 'dns')
    const networkDnsVM = configuredVirtualMachines.find(vm => vm.name === 'dns')
    
    if (originalDnsVM && networkDnsVM) {
      inventory.all.children.lxd_containers.children.dns_containers.hosts.dns1 = {
        parent_host: originalDnsVM.host,
        memory: `${originalDnsVM.memory}GB`,
        cpu_cores: originalDnsVM.cpu,
        disk_size: `${originalDnsVM.disk}GB`,
        arch: 'x86_64',
        lan_ip: networkDnsVM.lanIP,
        internal_ip: networkDnsVM.internalIP,
        zerotier_ip: networkDnsVM.zerotierIP,
        zerotier_enabled: true,
        gpu_passthrough: false
      }
      inventory.all.children.dns.hosts.dns1 = {}
    }
  }
  
  // Add Kubernetes nodes based on clusterNodes assignments
  clusterNodes.forEach((node) => {
    if (node.role === 'control_plane') {
      inventory.all.children.microk8s.children.microk8s_control_plane.hosts[node.hostname] = {}
      
      // If it's a VM, also add to LXD containers
      if (node.type === 'vm') {
        const originalVM = vmPlan.find(v => v.name === node.hostname)
        const networkVM = configuredVirtualMachines.find(v => v.name === node.hostname)
        
        if (originalVM && networkVM) {
          const vmDef = {
            parent_host: originalVM.host,
            memory: `${originalVM.memory}GB`,
            cpu_cores: originalVM.cpu,
            disk_size: `${originalVM.disk}GB`,
            arch: 'x86_64',
            lan_ip: networkVM.lanIP,
            internal_ip: networkVM.internalIP,
            zerotier_ip: networkVM.zerotierIP,
            zerotier_enabled: true,
            gpu_passthrough: vmHasGPUPassthrough(node.hostname)
          }
          inventory.all.children.lxd_containers.children.microk8s_containers.children.controllers.hosts[node.hostname] = vmDef
        }
      }
    } else if (node.role === 'worker') {
      inventory.all.children.microk8s.children.microk8s_workers.hosts[node.hostname] = {}
      
      // If it's a VM, also add to LXD containers
      if (node.type === 'vm') {
        const originalVM = vmPlan.find(v => v.name === node.hostname)
        const networkVM = configuredVirtualMachines.find(v => v.name === node.hostname)
        
        if (originalVM && networkVM) {
          const vmDef = {
            parent_host: originalVM.host,
            memory: `${originalVM.memory}GB`,
            cpu_cores: originalVM.cpu,
            disk_size: `${originalVM.disk}GB`,
            arch: 'x86_64',
            lan_ip: networkVM.lanIP,
            internal_ip: networkVM.internalIP,
            zerotier_ip: networkVM.zerotierIP,
            zerotier_enabled: true,
            gpu_passthrough: vmHasGPUPassthrough(node.hostname)
          }
          inventory.all.children.lxd_containers.children.microk8s_containers.children.workers.hosts[node.hostname] = vmDef
        }
      }
    }
  })
  
  return inventory
}

/**
 * Convert inventory object to YAML format
 */
export function inventoryToYAML(inventory) {
  // Simple YAML serializer for inventory
  const yaml = []
  yaml.push('---')
  yaml.push('# Dynamically generated inventory by Thinkube Installer')
  yaml.push('')
  
  function indent(level) {
    return '  '.repeat(level)
  }
  
  function writeObject(obj, level = 0) {
    Object.entries(obj).forEach(([key, value]) => {
      if (value === null || value === undefined) return
      
      if (typeof value === 'object' && !Array.isArray(value)) {
        yaml.push(`${indent(level)}${key}:`)
        writeObject(value, level + 1)
      } else if (Array.isArray(value)) {
        yaml.push(`${indent(level)}${key}:`)
        value.forEach(item => {
          yaml.push(`${indent(level + 1)}- ${item}`)
        })
      } else if (typeof value === 'string' && value.includes('{{')) {
        // Quote Jinja2 variables for proper YAML parsing
        yaml.push(`${indent(level)}${key}: "${value}"`)
      } else if (typeof value === 'string') {
        yaml.push(`${indent(level)}${key}: "${value}"`)
      } else {
        yaml.push(`${indent(level)}${key}: ${value}`)
      }
    })
  }
  
  writeObject(inventory)
  return yaml.join('\n')
}