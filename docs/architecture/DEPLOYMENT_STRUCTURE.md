# Thinkube Deployment Structure

This document outlines the detailed structure and organization of the Thinkube deployment system, including the directory structure, playbook organization, and numbering convention.

## Numbering Convention

The deployment system uses a consistent numbering convention to organize playbooks:

```
x0: Main component setup (base installation)
x1-x7: Component-specific configurations and extensions
x8: Testing and validation
x9: Rollback and recovery procedures
```

This convention provides a clear structure where:
- Each component starts with a base installation playbook (x0)
- Configuration aspects are separated into dedicated playbooks (x1-x7)
- Each component has a standard testing playbook (x8)
- Each component has a standard rollback procedure (x9)

## Directory Structure and Playbook Organization

```
/ansible
├── 00_initial_setup/               # Host configuration and SSH setup
│   ├── 10_setup_ssh_keys.yaml      # Base SSH key configuration
│   ├── 11_configure_ssh_agent.yaml # Configure SSH agent forwarding
│   ├── 18_test_ssh_connectivity.yaml # Test SSH connectivity
│   ├── 19_reset_ssh_config.yaml    # Reset SSH configuration if needed
│   │
│   ├── 20_setup_env.yaml           # Base environment variable setup
│   ├── 28_test_environment.yaml    # Test environment configuration 
│   ├── 29_reset_environment.yaml   # Reset environment if needed
│
├── 10_baremetal_infra/             # Physical server configuration
│   ├── 10_install_dependencies.yaml # Base system dependencies
│   ├── 11_configure_system_settings.yaml # Configure system parameters
│   ├── 18_test_system_readiness.yaml # Test system configuration
│   ├── 19_rollback_system_changes.yaml # Rollback system changes
│   │
│   ├── 20_configure_network_bridge.yaml # Base network bridge setup
│   ├── 21_configure_advanced_networking.yaml # Additional network config
│   ├── 28_test_network_connectivity.yaml # Test network configuration
│   ├── 29_reset_network_configuration.yaml # Rollback network changes
│
├── 20_lxd_setup/                   # LXD cluster setup and profiles
│   ├── 00_cleanup.yaml             # Clean up existing deployments
│   │
│   ├── 10_setup_lxd_cluster.yaml   # Base LXD cluster setup
│   ├── 11_configure_lxd_storage.yaml # Configure storage pools
│   ├── 18_test_lxd_cluster.yaml    # Test LXD cluster functionality
│   ├── 19_reset_lxd_cluster.yaml   # Reset LXD cluster if needed
│   │
│   ├── 20_setup_lxd_profiles.yaml  # Base profile creation
│   ├── 21_configure_gpu_profiles.yaml # GPU-specific profiles
│   ├── 28_test_lxd_profiles.yaml   # Test profile functionality
│   ├── 29_reset_lxd_profiles.yaml  # Reset profiles if needed
│   │
│   ├── 30_create_vms.yaml          # Base VM creation
│   ├── 31_configure_vm_resources.yaml # Configure VM resources
│   ├── 38_test_vms.yaml            # Test VM functionality
│   ├── 39_reset_vms.yaml           # Reset VMs if needed
│   │
│   ├── 40_configure_vm_ssh.yaml    # Base SSH setup for VMs
│   ├── 48_test_vm_ssh.yaml         # Test VM SSH connectivity
│   ├── 49_reset_vm_ssh.yaml        # Reset VM SSH configuration
│
├── 30_networking/                  # Network configuration
│   ├── 10_setup_zerotier.yaml      # Base ZeroTier installation
│   ├── 11_configure_zerotier_routes.yaml # Configure routing
│   ├── 18_test_zerotier.yaml       # Test ZeroTier connectivity
│   ├── 19_reset_zerotier.yaml      # Reset ZeroTier if needed
│   │
│   ├── 20_setup_dns.yaml           # Base DNS server setup
│   ├── 21_configure_dns_zones.yaml # Configure DNS zones
│   ├── 28_test_dns.yaml            # Test DNS resolution
│   ├── 29_reset_dns.yaml           # Reset DNS if needed
│
├── 40_core_services/               # MicroK8s deployment and services
│   ├── 10_setup_microk8s.yaml      # Base MicroK8s installation
│   ├── 11_configure_microk8s_addons.yaml # Configure addons
│   ├── 18_test_microk8s.yaml       # Test MicroK8s functionality
│   ├── 19_reset_microk8s.yaml      # Reset MicroK8s if needed
│   │
│   ├── 20_join_workers.yaml        # Base worker node joining
│   ├── 21_configure_worker_roles.yaml # Configure worker roles
│   ├── 28_test_workers.yaml        # Test worker functionality
│   ├── 29_reset_workers.yaml       # Reset worker nodes if needed
│   │
│   ├── 30_setup_coredns.yaml       # Base CoreDNS configuration
│   ├── 31_configure_dns_forwarding.yaml # Configure DNS forwarding
│   ├── 38_test_coredns.yaml        # Test CoreDNS functionality
│   ├── 39_reset_coredns.yaml       # Reset CoreDNS if needed
│   │
│   ├── 40_setup_ingress.yaml       # Base Ingress controller installation
│   ├── 41_configure_primary_ingress.yaml # Configure main ingress
│   ├── 42_configure_knative_ingress.yaml # Configure Knative ingress
│   ├── 48_test_ingress.yaml        # Test ingress functionality
│   ├── 49_reset_ingress.yaml       # Reset ingress controllers
│   │
│   ├── 50_setup_metallb.yaml       # Base MetalLB installation
│   ├── 51_configure_ip_pools.yaml  # Configure IP address pools
│   ├── 58_test_metallb.yaml        # Test load balancer functionality
│   ├── 59_reset_metallb.yaml       # Reset MetalLB if needed
│   │
│   ├── 60_setup_cert_manager.yaml  # Base cert-manager installation
│   ├── 61_configure_issuers.yaml   # Configure certificate issuers
│   ├── 68_test_certificates.yaml   # Test certificate issuance
│   ├── 69_reset_cert_manager.yaml  # Reset cert-manager if needed
```

## Deployment Workflow

The deployment follows a sequential process through each directory, with each directory representing a phase of the deployment:

### Phase 0: Initial Setup
- Configure SSH access between servers
- Set up environment variables
- Test connectivity and configuration

### Phase 1: Baremetal Infrastructure
- Install system dependencies
- Configure network bridging
- Set up hardware-specific settings
- Test physical infrastructure

### Phase 2: LXD Setup
- Create LXD cluster
- Set up profiles for VMs
- Create and configure VMs
- Configure SSH access to VMs
- Test VM functionality

### Phase 3: Networking
- Configure ZeroTier overlay network
- Set up DNS server and resolution
- Test network connectivity
- Ensure proper routing between components

### Phase 4: Core Services
- Install MicroK8s on control plane
- Join worker nodes to the cluster
- Configure CoreDNS for service discovery
- Set up ingress controllers
- Configure load balancing with MetalLB
- Set up certificate management
- Test core functionality

## Testing Strategy

Each component includes a dedicated testing playbook (x8) that:
1. Verifies the component is properly installed
2. Tests basic functionality
3. Validates integration with other components
4. Fails immediately if any test doesn't pass

## Rollback Strategy

Each component includes a rollback playbook (x9) that:
1. Safely removes the component if needed
2. Restores the system to its previous state
3. Cleans up any artifacts

## Execution Approach

Playbooks are designed to follow these principles:

1. **Fail Fast**: Fail immediately when any critical step fails
   - No attempt to recover automatically from failures
   - Clear error messages that indicate exactly what failed and why
   - Immediate termination when prerequisites aren't met

2. **Idempotent**: Can be run multiple times safely
   - Running a second time should not break the system
   - Should detect already-completed steps and skip them

3. **Atomic**: Either complete successfully or fail cleanly
   - No partial deployments
   - All validation done before making changes

4. **Self-validating**: Include validation steps
   - Each step validates its own success criteria
   - Immediate failure if validation doesn't pass

5. **Well-documented**: Include clear documentation
   - Purpose of each playbook clearly stated
   - Prerequisites explicitly documented
   - Expected outcome defined

## Implementation Notes

1. **Dependencies**: Each playbook explicitly checks for dependencies before proceeding
2. **Variables**: Variables are defined in inventory, not hardcoded in playbooks
3. **Templates**: Jinja2 templates are used for complex configurations
4. **Verification**: Each critical step includes immediate verification
5. **Error Messages**: Descriptive error messages that clearly indicate the failure point and reason