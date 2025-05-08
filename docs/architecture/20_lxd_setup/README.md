# 20 LXD Setup

## Overview

The LXD Setup component configures LXD on the baremetal servers, creates VM profiles, and deploys VMs for MicroK8s. This component is responsible for preparing the virtualization environment that will host the Kubernetes cluster.

## Playbooks

### 00_cleanup.yaml
- **Purpose**: Cleans up existing LXD VMs and configurations for a fresh deployment
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - LXD installed on all servers
- **Required Variables**:
  - None (uses inventory host definitions)
- **Outputs**: 
  - Old VMs removed
  - Old profiles removed
  - System ready for fresh deployment
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/00_cleanup.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 10_setup_lxd_cluster.yaml
- **Purpose**: Initializes LXD and configures clustering between nodes
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - Network bridge configured
  - System dependencies installed
- **Required Variables**:
  - `lxd_storage_pool`: Storage pool name from inventory
  - `lxd_storage_size`: Size of storage pool from inventory
- **Optional Variables**:
  - `lxd_network_name`: Name of LXD network bridge (default: "lxdbr0")
  - `lxd_network_cidr`: CIDR for LXD network (default: "192.168.100.0/24")
- **Outputs**: 
  - LXD initialized on all servers
  - Storage pools configured
  - Network bridges created
  - Clustering configured (if multiple servers)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/10_setup_lxd_cluster.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 20_setup_lxd_profiles.yaml
- **Purpose**: Creates VM profiles for MicroK8s nodes
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - LXD cluster set up by 10_setup_lxd_cluster.yaml
- **Required Variables**:
  - None (uses inventory to determine profiles to create)
- **Optional Variables**:
  - None (all configuration taken from inventory)
- **Outputs**: 
  - VM profiles created based on inventory definitions
  - Profiles properly configured for VM creation
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/20_setup_lxd_profiles.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 30_create_vms.yaml
- **Purpose**: Creates VMs for MicroK8s deployment
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - LXD profiles created by 20_setup_lxd_profiles.yaml
- **Required Variables**:
  - VM definitions in inventory (memory, cpu_cores, disk_size, parent_host, etc.)
  - `domain_name`: Domain name for VM FQDNs
- **Optional Variables**:
  - `lxd_image`: VM image to use (default: "ubuntu:24.04")
- **Outputs**: 
  - VMs created with names and resources as defined in inventory
  - Network interfaces configured according to inventory
  - VMs running and ready for further configuration
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/30_create_vms.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 40_configure_vm_ssh.yaml
- **Purpose**: Configures SSH access to VMs from management node
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - VMs created by 30_create_vms.yaml
  - VMs accessible via IP
- **Required Variables**:
  - VM definitions in inventory (hostnames and IP addresses)
- **Optional Variables**:
  - `ssh_key_name`: SSH key to use (default: "thinkube_cluster_key")
- **Outputs**: 
  - SSH keys copied to VMs
  - SSH config updated for direct VM access
  - SSH agent configured for forwarding
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/40_configure_vm_ssh.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### check_environment.yaml
- **Purpose**: Verifies environment readiness for deployment
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - Initial setup complete
- **Required Variables**:
  - None
- **What it Checks**: 
  - LXD installation and version
  - Storage availability
  - Network bridge configuration
  - CPU virtualization extensions
  - GPU availability (if applicable)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/check_environment.yaml
  ```

### 18_test_vms.yaml
- **Purpose**: Tests VM functionality and accessibility
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**:
  - VMs created and configured
- **Required Variables**:
  - VM definitions in inventory (for validation)
- **What it Tests**:
  - VM network connectivity
  - SSH access to VMs
  - Resource allocation correctness
  - GPU passthrough (if configured)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/18_test_vms.yaml
  ```

### 19_reset_vms.yaml
- **Purpose**: Removes VMs if needed
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **When to Use**:
  - When troubleshooting VM issues
  - When needing to reconfigure VMs
- **Required Variables**:
  - VM definitions in inventory (used to determine which VMs to remove)
- **What it Removes**:
  - VMs specified in inventory
  - SSH configuration for VMs
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/19_reset_vms.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

## Dependencies

- Initial setup completed (00_initial_setup)
- Baremetal infrastructure configured (10_baremetal_infra)
- LXD installed on all servers
- Network bridges configured

## Common Issues and Troubleshooting

- **LXD Initialization Failures**:
  - Check storage space with `df -h`
  - Verify LXD version with `lxd --version`
  - Check LXD service status with `systemctl status lxd`

- **VM Creation Issues**:
  - Verify profile existence with `lxc profile list`
  - Check VM logs with `lxc console <vm_name>`
  - Verify network settings with `lxc network list`

- **SSH Access Problems**:
  - Check VM IP address with `lxc list`
  - Verify SSH key permissions
  - Check SSH configuration in `~/.ssh/config`

## Component-Specific Guidelines

- **No Hardcoded Values**: All VM names, IP addresses, resource allocations, and host configurations MUST come from the inventory file
- The inventory file is the single source of truth for all VM configurations
- Playbooks must dynamically use host variables from inventory
- Use inventory groups to determine VM roles (controllers, workers)
- User-defined hostnames in inventory must be respected (no assumptions about naming conventions)
- IP addresses must be taken from inventory variables, never hardcoded
- Parent-child relationships between baremetal servers and VMs are defined in inventory
- All VM resource allocations (CPU, memory, disk) must be taken from inventory