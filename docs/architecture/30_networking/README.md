# 30 Networking

## Overview

The Networking component configures the network infrastructure for the Thinkube platform, including ZeroTier overlay networking and DNS services. This component ensures that all nodes can communicate with each other and that services are properly discoverable.

## Playbooks

### 10_setup_zerotier.yaml
- **Purpose**: Configures ZeroTier overlay network on all nodes
- **Target Hosts**: `zerotier_nodes` (all nodes that need ZeroTier, as defined in inventory)
- **Prerequisites**: 
  - SSH access to all nodes
  - VMs created and accessible
- **Required Variables**:
  - `zerotier_network_id`: ZeroTier network ID from inventory
  - IP addresses for each node (defined in inventory)
- **Optional Variables**:
  - `zerotier_api_key`: ZeroTier API key for automated configuration
- **Outputs**: 
  - ZeroTier installed on all nodes
  - Nodes joined to ZeroTier network
  - Static IP addresses assigned
  - Routing configured for overlay network
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/10_setup_zerotier.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 11_configure_zerotier_routes.yaml
- **Purpose**: Configures advanced routing in ZeroTier network
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - ZeroTier set up on all nodes
  - API access to ZeroTier network
- **Required Variables**:
  - `zerotier_network_id`: ZeroTier network ID from inventory
  - `zerotier_api_key`: ZeroTier API key
  - Network route definitions (from inventory)
- **Optional Variables**:
  - None
- **Outputs**: 
  - Routes configured in ZeroTier
  - Managed routes set up for specialized traffic
  - Bridging configured if needed
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/11_configure_zerotier_routes.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 20_setup_dns.yaml
- **Purpose**: Sets up DNS server for service discovery
- **Target Hosts**: `dns` (DNS server nodes defined in inventory)
- **Prerequisites**: 
  - ZeroTier network configured
  - DNS server nodes created and accessible
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
  - DNS server IP addresses (from inventory)
  - Zone configuration details (from inventory)
- **Optional Variables**:
  - DNS forwarding settings
- **Outputs**: 
  - DNS server installed and configured
  - Zones created for service discovery
  - Wildcard records set up for services
  - Forwarding configured for external domains
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/20_setup_dns.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 21_configure_dns_zones.yaml
- **Purpose**: Configures specific DNS zones and records
- **Target Hosts**: `dns` (DNS server nodes defined in inventory)
- **Prerequisites**: 
  - DNS server installed by 20_setup_dns.yaml
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
  - Zone configuration details (from inventory)
- **Optional Variables**:
  - Additional domain aliases
- **Outputs**: 
  - Additional zones configured
  - Service-specific records created
  - Wildcard records for subdomains
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/21_configure_dns_zones.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 18_test_zerotier.yaml
- **Purpose**: Tests ZeroTier connectivity between all nodes
- **Target Hosts**: `zerotier_nodes` (all nodes with ZeroTier, as defined in inventory)
- **Prerequisites**:
  - ZeroTier configured on all nodes
- **Required Variables**:
  - Node definitions in inventory (for validation)
- **What it Tests**:
  - ZeroTier connectivity between all nodes
  - Proper IP assignment
  - Routing table configuration
  - Network performance
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/18_test_zerotier.yaml
  ```

### 19_reset_zerotier.yaml
- **Purpose**: Removes ZeroTier configuration if needed
- **Target Hosts**: `zerotier_nodes` (all nodes with ZeroTier, as defined in inventory)
- **When to Use**:
  - When troubleshooting network issues
  - When changing ZeroTier network ID
- **Required Variables**:
  - `zerotier_network_id`: ZeroTier network ID to leave
- **What it Removes**:
  - ZeroTier network membership
  - ZeroTier configuration
  - Routes related to ZeroTier
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/19_reset_zerotier.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 28_test_dns.yaml
- **Purpose**: Tests DNS resolution for services
- **Target Hosts**: All hosts that need DNS resolution
- **Prerequisites**:
  - DNS server configured
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
- **What it Tests**:
  - DNS resolution for main domain
  - Wildcard resolution
  - Service-specific record resolution
  - Forward and reverse lookups
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/28_test_dns.yaml
  ```

### 29_reset_dns.yaml
- **Purpose**: Resets DNS configuration if needed
- **Target Hosts**: `dns` (DNS server nodes defined in inventory)
- **When to Use**:
  - When changing domain configuration
  - When troubleshooting DNS issues
- **Required Variables**:
  - None (uses inventory host definitions)
- **What it Removes**:
  - DNS zone configuration
  - DNS server configuration
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/29_reset_dns.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

## Dependencies

- Initial setup completed (00_initial_setup)
- Baremetal infrastructure configured (10_baremetal_infra)
- LXD setup completed with VMs created (20_lxd_setup)

## Common Issues and Troubleshooting

- **ZeroTier Connectivity Issues**:
  - Verify ZeroTier service with `systemctl status zerotier-one`
  - Check network membership with `zerotier-cli listnetworks`
  - Verify IP assignment with `zerotier-cli info`
  - Check firewall settings for UDP port 9993

- **DNS Resolution Problems**:
  - Check DNS server status with `systemctl status bind9` or `systemctl status named`
  - Verify zone files with `named-checkzone domain.com /path/to/zonefile`
  - Test resolution with `dig @dns_server_ip domain.com`
  - Check client resolver configuration with `cat /etc/resolv.conf`

- **Network Performance Issues**:
  - Test latency with `ping -c 10 hostname`
  - Check bandwidth with `iperf3 -c hostname`
  - Verify routing tables with `ip route` and `zerotier-cli listroutes`

## Component-Specific Guidelines

- **No Hardcoded Values**: All network configuration must come from inventory
- ZeroTier network ID is a required configuration parameter in inventory
- All IP addresses must be defined in inventory, never hardcoded
- DNS zone configuration should be derived from inventory variables
- Use DNS for service discovery, never hardcoded IPs
- Network configuration must be idempotent (can be run multiple times safely)
- Always ensure SSH connectivity is maintained during network changes
- Test DNS resolution from all nodes after configuration