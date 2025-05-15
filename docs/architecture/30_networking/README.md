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

# Note: This playbook has been consolidated into 10_setup_zerotier.yaml
# and is mentioned here for reference only.
### ~11_configure_zerotier_routes.yaml~ (Deprecated)
- **Status**: Consolidated into 10_setup_zerotier.yaml
- **Purpose**: ~Configures advanced routing in ZeroTier network~
- **Note**: All functionality is now handled in the main 10_setup_zerotier.yaml playbook
  which configures all aspects of ZeroTier networking including:
  - Installation and setup
  - Network joining
  - Node authorization
  - IP assignment (including MetalLB IPs)
  - Route configuration
  - Firewall settings

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

# Note: This playbook has been consolidated into 20_setup_dns.yaml
# and is mentioned here for reference only.
### ~21_configure_dns_zones.yaml~ (Deprecated)
- **Status**: Consolidated into 20_setup_dns.yaml
- **Purpose**: ~Configures specific DNS zones and records~
- **Note**: All DNS zone configuration functionality is now handled in the main 20_setup_dns.yaml playbook
  which configures all aspects of DNS including:
  - Bind9 installation and setup
  - Main domain zone configuration
  - Knative subdomain zone configuration
  - Wildcard records for service discovery
  - Resolver configuration and DNS forwarders
  - Service-specific records creation

### 18_test_zerotier.yaml
- **Purpose**: Tests ZeroTier connectivity between all nodes
- **Target Hosts**: `zerotier_nodes` (all nodes with ZeroTier, as defined in inventory)
- **Prerequisites**:
  - ZeroTier configured on all nodes
- **Required Variables**:
  - Node definitions in inventory (for validation)
  - `zerotier_network_id`: ZeroTier network ID from environment variable
- **What it Tests**:
  - ZeroTier service status and activation
  - Network membership and authorization
  - Proper IP assignment (including MetalLB IPs)
  - Routing table configuration
  - Network connectivity between nodes
  - Performance testing with iperf3 (when available)
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
  - `zerotier_network_id`: ZeroTier network ID to leave from environment variable
  - `zerotier_api_token`: ZeroTier API token for Central API operations
- **What it Removes**:
  - ZeroTier network membership for specific nodes
  - Node authorization in ZeroTier Central (optional)
  - ZeroTier software (optional)
- **Safety Features**:
  - Preserves the ZeroTier network itself and other nodes
  - Provides confirmation prompt for dangerous operations
  - Allows safe node-specific removal without affecting other nodes
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
  - DNS server IP from inventory (`dns_server_ip`)
- **What it Tests**:
  - DNS server connectivity and availability
  - Resolution of main domain and specific hostnames
  - Wildcard resolution for services (*.domain.com)
  - Knative subdomain resolution (*.kn.domain.com)
  - MetalLB ingress IP resolution
  - Forward and reverse lookups
- **Features**:
  - Graceful handling of connectivity issues
  - Detailed diagnostics for troubleshooting
  - Per-host and overall test summary
  - Recommendations based on test results
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
  - When reconfiguring DNS zones
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
- **What it Removes**:
  - DNS zone files and configurations
  - Bind9 configuration to default state
  - Resolver configuration
- **Safety Features**:
  - Confirmation pause before proceeding
  - Configurable severity (from resetting configuration to full removal)
  - Optionally reinstalls bind9 with clean configuration
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/30_networking/29_reset_dns.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

## Dependencies

- Initial setup completed (00_initial_setup)
- Baremetal infrastructure configured (10_baremetal_infra)
- LXD setup completed with VMs created (20_lxd_setup)

## Common Issues and Troubleshooting

### ZeroTier Connectivity Issues

- **Service Status Issues**:
  - Verify ZeroTier service with `systemctl status zerotier-one`
  - Restart if needed: `sudo systemctl restart zerotier-one`
  - Check logs: `journalctl -u zerotier-one`

- **Network Membership Problems**:
  - Check network status: `zerotier-cli listnetworks`
  - Ensure network is authorized: Look for "OK" status
  - Rejoin if needed: `sudo zerotier-cli leave <network_id> && sudo zerotier-cli join <network_id>`

- **IP Assignment Issues**:
  - Verify assigned IPs: `zerotier-cli listnetworks | grep 192.168.191`
  - Check MetalLB IPs on controller: Should include ingress IPs (192.168.191.200-201)
  - Check Central API authorization: Ensure node is authorized in ZeroTier Central

- **Connectivity Problems**:
  - Check UDP port 9993: `sudo ufw status` or equivalent firewall command
  - Verify routes: `ip route | grep zt`
  - Test inter-node connectivity: Run the test playbook

### DNS Resolution Problems

- **Bind9 Service Issues**:
  - Check service status: `systemctl status bind9` or `systemctl status named`
  - View logs: `journalctl -u named`
  - Reload configuration: `sudo rndc reload`

- **Zone File Problems**:
  - Verify zone syntax: `named-checkzone domain.com /etc/bind/zones/db.domain.com`
  - Check zone loading: `sudo rndc zonestatus domain.com`
  - Ensure zone files have final newlines: Add a newline at the end of zone files

- **Resolution Failures**:
  - Test from DNS server: `dig @127.0.0.1 domain.com`
  - Test from other hosts: `dig @192.168.191.1 domain.com`
  - Check for UDP port 53 blocking: May require firewall adjustment
  - Verify test results: Run the test playbook

- **Client Configuration**:
  - Check resolver: `cat /etc/resolv.conf`
  - Check systemd-resolved: `resolvectl status`
  - Update resolver: `sudo systemctl restart systemd-resolved`

### Network Performance Issues

- **Latency Problems**:
  - Test basic connectivity: `ping -c 10 hostname`
  - Check for packet loss: Look for "X% packet loss" in ping results
  - Verify route efficiency: `traceroute hostname`

- **Bandwidth Issues**:
  - Test with iperf3: `iperf3 -c hostname`
  - Check for MTU problems: `ping -c 5 -M do -s 1472 hostname`
  - Verify throughput: Run the ZeroTier test playbook with iperf testing

- **Routing Problems**:
  - Check routing tables: `ip route`
  - Verify ZeroTier routes: `zerotier-cli listroutes`
  - Check for route conflicts: Look for overlapping routes

## Component-Specific Guidelines

### Configuration Management

- **No Hardcoded Values**: All network configuration must come from inventory or environment variables
- **Environment Variable Usage**: Set in ~/.env file and symlinked to project root:
  ```bash
  export ZEROTIER_NETWORK_ID=93afae59634c1a70
  export ZEROTIER_API_TOKEN=your_token_here
  ```
- **IP Address Management**: 
  - All IP addresses must be defined in inventory, never hardcoded
  - Use variables in templates with explicit defaults: `{{ variable | default('fallback') }}`
  - Follow the subnet organization defined in inventory

### Networking Best Practices

- **Complete Flow-Based Approach**: 
  - Process nodes one at a time with `serial: 1`
  - Complete all operations for one node before moving to the next
  - Use ZeroTier API cautiously to avoid affecting other nodes

- **Idempotent Configuration**:
  - Network configuration must be idempotent (can be run multiple times safely)
  - Check for existing configuration before modifying
  - Playbooks should detect and report rather than changing blindly

- **Security Considerations**:
  - Always ensure SSH connectivity is maintained during network changes
  - Never expose API tokens or sensitive credentials
  - Use properly restricted API tokens for ZeroTier Central

### DNS and Service Discovery

- **DNS First Approach**:
  - Use DNS for service discovery, never hardcoded IPs
  - Prefer wildcard domains for dynamic service discovery
  - Assign specific domains for critical infrastructure components

- **Testing and Validation**:
  - Run test playbooks after configuration changes
  - Test DNS resolution from all nodes after configuration
  - Verify both internal and external DNS resolution

- **DNS Zone Management**:
  - DNS zone configuration should be derived from inventory variables
  - Use templates for all zone files with appropriate variable substitution
  - Ensure SOA records have proper serial number incrementation