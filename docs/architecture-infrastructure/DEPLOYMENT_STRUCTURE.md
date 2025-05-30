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
├── 40_thinkube/                    # Component-based deployment
│   ├── core/                       # Essential platform components
│   │   ├── infrastructure/         # Basic Kubernetes infrastructure
│   │   │   ├── microk8s/
│   │   │   ├── coredns/
│   │   │   ├── cert-manager/      # Must be installed before ingress
│   │   │   └── ingress/           # Depends on cert-manager for certificates
│   │   ├── keycloak/              # SSO and authentication
│   │   ├── postgresql/            # Database services
│   │   ├── minio/                 # Object storage
│   │   ├── harbor/                # Container registry
│   │   ├── argo-workflows/        # Workflow automation
│   │   ├── argocd/                # GitOps deployment
│   │   ├── devpi/                 # Python package repository
│   │   ├── awx/                   # Ansible automation
│   │   ├── mkdocs/                # Documentation
│   │   └── thinkube-dashboard/    # Main dashboard
│   └── optional/                  # AWX-deployed components
│       ├── prometheus/            # Metrics collection
│       ├── grafana/               # Metrics visualization
│       ├── opensearch/            # Log aggregation
│       ├── jupyterhub/            # Data science notebooks
│       ├── code-server/           # VS Code in browser
│       ├── mlflow/                # ML experiment tracking
│       ├── knative/               # Serverless platform
│       ├── qdrant/                # Vector database
│       ├── pgadmin/               # PostgreSQL admin
│       ├── penpot/                # Design platform
│       └── valkey/                # Cache service
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

### Phase 4: Thinkube Platform
- Deploy core infrastructure in order:
  1. MicroK8s cluster setup
  2. CoreDNS configuration
  3. Cert-manager (required for ingress certificates)
  4. Ingress controllers (depends on cert-manager)
- Deploy core services in dependency order:
  1. **Keycloak** (uses embedded H2 database in dev mode)
  2. **Harbor** (requires Keycloak for OIDC authentication)
  3. **Mirror public images** to Harbor (including postgres:14.5-alpine)
  4. **PostgreSQL** (uses postgres image from Harbor)
  5. **MinIO** (object storage)
  6. Other services that depend on the above
- Deploy CI/CD stack (Argo Workflows, ArgoCD, DevPi)
- Deploy AWX for optional component management
- Deploy optional services via AWX (Prometheus, JupyterHub, etc.)
- Configure and test all integrations
- Validate complete platform functionality

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