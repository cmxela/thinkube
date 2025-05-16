# 10 Baremetal Infrastructure

## Overview

The Baremetal Infrastructure component configures the physical servers that will host the Thinkube platform. This includes installing system dependencies, setting up network bridges for VMs, and configuring hardware-specific settings.

## Playbooks

### 10_install_dependencies.yaml
- **Purpose**: Installs required system packages on all baremetal servers
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - SSH access configured by 00_initial_setup
  - Internet connectivity for package installation
- **Required Variables**:
  - None (uses inventory groups to determine which hosts to configure)
- **Optional Variables**:
  - `extra_packages`: List of additional packages to install
- **Outputs**: 
  - All required system packages installed
  - System configured for hosting VMs
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/10_baremetal_infra/10_install_dependencies.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 11_configure_system_settings.yaml
- **Purpose**: Configures system parameters for optimal performance
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - Dependencies installed by 10_install_dependencies.yaml
- **Required Variables**:
  - None
- **Optional Variables**:
  - `swappiness`: VM swappiness setting (default: 10)
  - `max_map_count`: Maximum map count for containers (default: 262144)
- **Outputs**: 
  - System settings optimized for VM hosting
  - Kernel parameters properly configured
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/10_baremetal_infra/11_configure_system_settings.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 20_configure_network_bridge.yaml
- **Purpose**: Sets up network bridge (br0) for VM connectivity
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - System dependencies installed
- **Required Variables**:
  - `network_cidr`: Network CIDR for the LAN (e.g., "192.168.1.0/24")
  - `network_gateway`: Gateway IP address for the LAN
  - `ansible_host`: IP address of each server
- **Optional Variables**:
  - `network_bridge_name`: Name of network bridge (default: "br0")
- **Outputs**: 
  - Network bridge (br0) created and configured
  - Physical interface attached to bridge
  - Bridge configured with static IP
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/10_baremetal_infra/20_configure_network_bridge.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 18_test_system_readiness.yaml
- **Purpose**: Validates system configuration for hosting VMs
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**:
  - System configured by previous playbooks
- **Required Variables**:
  - None
- **What it Tests**:
  - Required packages are installed
  - System settings are properly configured
  - Network bridge is working correctly
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/10_baremetal_infra/18_test_system_readiness.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 19_rollback_system_changes.yaml
- **Purpose**: Reverts system changes if needed
- **Target Hosts**: `baremetal` (all physical servers)
- **When to Use**:
  - When troubleshooting network issues
  - When needing to reconfigure system settings
- **Required Variables**:
  - None
- **What it Removes**:
  - Network bridge configuration
  - System settings changes
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/10_baremetal_infra/19_rollback_system_changes.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

## Dependencies

- Initial SSH setup completed (00_initial_setup)
- Internet connectivity for package installation
- Physical network interfaces with static IP addresses

## Common Issues and Troubleshooting

- **Network Bridge Issues**:
  - If bridge creation disconnects your SSH session, physical access may be required
  - Backup network configuration before making changes
  - Check interface names with `ip a` as they might differ between servers

- **Package Installation Failures**:
  - Verify internet connectivity with `ping 8.8.8.8`
  - Check apt/dpkg lock with `lsof /var/lib/dpkg/lock`
  - Ensure apt sources are up-to-date with `apt update`

- **System Settings Issues**:
  - Verify changes with `sysctl -a | grep <parameter>`
  - Check if changes persist after reboot

## Component-Specific Guidelines

- Network bridge configuration must preserve SSH connectivity
- Always backup network configuration before making changes
- Use the native interface name (like ens160 or enp0s31f6) consistently
- Run VM tests after network configuration to verify bridge functionality