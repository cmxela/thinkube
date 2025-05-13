# CLAUDE.md - Master Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: When starting a new session, first read the [START_HERE.md](/START_HERE.md) document at the project root. This document contains the master task list and tracks implementation progress to ensure continuity between sessions.

## Project Overview

Thinkube is a home-based development platform built on Kubernetes, designed specifically for AI applications and agents. See [Project Definition](/docs/architecture/PROJECT_DEFINITION.md) for full details.

## Architecture Documentation

- [Project Definition](/docs/architecture/PROJECT_DEFINITION.md) - Core project principles and goals
- [Deployment Structure](/docs/architecture/DEPLOYMENT_STRUCTURE.md) - Directory structure and playbook organization
- [Variable Handling Policy](/docs/architecture/VARIABLE_HANDLING.md) - Rules for variable management and defaults
- [User Management](/docs/architecture/USER_MANAGEMENT.md) - System, application, and SSO user management
- [Error Handling Standard](/docs/architecture/ERROR_HANDLING.md) - Standardized approach to error handling
- [Pre-deployment Checklist](/docs/architecture/PRE_DEPLOYMENT_CHECKLIST.md) - Minimal requirements for deployment
- [Inventory Guide](/docs/architecture/INVENTORY_GUIDE.md) - Structure and management of the inventory system
- [Networking and DNS](/docs/architecture/NETWORKING_AND_DNS.md) - Network architecture and DNS configuration
- [Ansible Roles](/docs/architecture/ANSIBLE_ROLES.md) - Guidelines for when and how to use roles

## Component-Specific Documentation

- [00 Initial Setup](/docs/architecture/00_initial_setup/README.md) - Host configuration and SSH setup
- [10 Baremetal Infrastructure](/docs/architecture/10_baremetal_infra/README.md) - Physical server configuration
- [20 LXD Setup](/docs/architecture/20_lxd_setup/README.md) - LXD cluster, profiles, and VM creation
- [30 Networking](/docs/architecture/30_networking/README.md) - Network configuration (ZeroTier, DNS)
- [40 Core Services](/docs/architecture/40_core_services/README.md) - MicroK8s and core Kubernetes services

## Commands and Secure Sudo Password Handling

### Setting up Secure Environment Variables
First set up your sudo password securely:

```bash
# Option 1: Export password for current session only
export ANSIBLE_SUDO_PASS='your_sudo_password'

# Option 2: Add to .env file and create symbolic link in project root
echo 'ANSIBLE_SUDO_PASS=your_sudo_password' >> ~/.env
ln -sf ~/.env /home/thinkube/thinkube/.env  # Create symbolic link in project root

# Option 3: Provide password interactively when prompted
# (no environment variable needed, use --ask-become-pass)
```

The symbolic link to `~/.env` in the project root allows you to:
- Edit environment variables directly from the project directory
- Keep sensitive data out of version control
- Maintain a single source of truth for environment variables

### Running Playbooks
All commands use environment variables for security:

```bash
# Basic command with sudo password from environment variable
ansible-playbook -i inventory/inventory.yaml ansible/[path/to/playbook].yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"

# Alternative: prompt for password interactively (more secure for shared systems)
ansible-playbook -i inventory/inventory.yaml ansible/[path/to/playbook].yaml --ask-become-pass

# Run with specific tags
ansible-playbook -i inventory/inventory.yaml ansible/[path/to/playbook].yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS" --tags "tag1,tag2"

# Run MicroK8s setup
ansible-playbook -i inventory/inventory.yaml ansible/40_core_services/10_setup_microk8s.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"

# Join worker nodes
ansible-playbook -i inventory/inventory.yaml ansible/40_core_services/20_join_workers.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"

# Additional variables
ansible-playbook -i inventory/inventory.yaml ansible/[path/to/playbook].yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS domain_name=example.org admin_username=user"
```

### Playbook Execution Policy

- **Run for ALL hosts by default**: Always run playbooks for all hosts in the target group unless explicitly requested otherwise
- **Avoid partial runs**: Do not use the `-l` (limit) flag to restrict playbook execution to specific hosts unless you have a specific reason and know the implications
- **Complete infrastructure changes**: Each playbook should make complete, consistent changes across the entire infrastructure
- **Testing vs. Production**: If you need to test a playbook on specific hosts first, clearly document this as a temporary testing approach, not the standard execution method
- **Rollbacks should be complete**: When running rollback playbooks, apply them to all hosts where the original playbook was run

```bash
# AVOID (partial execution can lead to inconsistent infrastructure state):
./scripts/run_ansible.sh ansible/00_initial_setup/30_reserve_gpus.yaml -l bcn1

# PREFER (complete execution across all target hosts):
./scripts/run_ansible.sh ansible/00_initial_setup/30_reserve_gpus.yaml
```

### Linting and Syntax Checking
```bash
# Lint (no sudo needed)
ansible-lint ansible/[path/to/playbook].yaml

# Syntax check (no sudo needed)
ansible-playbook --syntax-check -i inventory/inventory.yaml ansible/[path/to/playbook].yaml
```

## Code Style Guidelines

- **YAML**: 2-space indentation, use list format for tasks with clear names
- **Variables**: 
  - Use snake_case for all variable names
  - Installation-specific variables MUST be defined in inventory, NEVER in playbooks
  - Only technical/advanced variables MAY have defaults in playbooks
  - All playbooks MUST verify required variables exist before proceeding
  - See [Variable Handling Policy](/docs/architecture/VARIABLE_HANDLING.md) for details
- **Module Names**: Use fully qualified names (e.g., `ansible.builtin.command` not `command`)
- **Tasks**: Always include descriptive name field
- **Facts**: Default to `gather_facts: true` - only disable fact gathering when performance is critical and facts are not needed
- **Documentation**: Include description, requirements, and usage in playbook headers
- **Error Handling**: Always fail fast on critical errors - never attempt to continue after a step fails
- **Templates**: Use .j2 extension, document with comments, maintain consistent whitespace
- **Secrets**: Store in vault, never commit plaintext credentials
- **Become**: Never use become at playbook level, only use it for tasks that require elevation
- **DNS Usage**: Use DNS hostnames for service communication, eliminate all hardcoded IPs
- **Messages**: Format user-facing messages for readability:
  ```yaml
  - name: Display important notice
    ansible.builtin.debug:
      msg: >-
        
        ═════════════════════════════════════════════════════════
        NOTE: Important Information ({{ inventory_hostname }})
        ═════════════════════════════════════════════════════════
        
        This is the main content of the message with proper spacing.
        
        IMPORTANT DETAILS:
          ✓ Use checkmarks for important points
          ✓ Add empty lines between sections
          ✓ Use separator lines and emoji for emphasis
        
        ═════════════════════════════════════════════════════════
  ```

## Playbook Numbering Convention

We follow a consistent numbering convention:
- **x0**: Main component setup (base installation)
- **x1-x7**: Component-specific configurations and extensions
- **x8**: Testing and validation
- **x9**: Rollback and recovery procedures

## Execution Flow Principles

Playbooks are designed to:
1. Run in numerical order with minimal human intervention
2. Fail fast when any critical step fails
3. Include proper verification at each stage
4. Be idempotent (safe to run multiple times)

## Playbook Completeness Principle

- Each playbook must be complete and fully functional without requiring additional "fix-up" playbooks
- All necessary permissions, configurations, and validations must be included within the playbook
- When a playbook finishes successfully, the system should be in a valid, usable state
- User intervention should never be required to fix incomplete configurations
- Always verify permissions, access rights, and functionality before considering a playbook complete
- The impact of a playbook must be clearly documented, including prerequisite checks and follow-up validations

## Storage Configuration Decisions

### LXD Storage Driver
- The LXD cluster will use ZFS as the storage driver (default in LXD) for its superior features:
  - Built-in snapshot and rollback capabilities
  - Better performance and data integrity guarantees
  - Native compression
- ZFS tools (zfsutils-linux) must be installed on all hosts before LXD initialization

## GPU Passthrough Configuration

### Current Status (2025-05-14)
- Implemented GPU passthrough configuration playbooks:
  - **30_reserve_gpus.yaml**: Configures GPUs for passthrough while keeping one for host OS
  - **38_test_gpu_reservation.yaml**: Verifies GPU passthrough configuration after reboot
  - **39_rollback_gpu_reservation.yaml**: Removes GPU passthrough configuration
  - **39_rollback_gpu_reservation_08.yaml**: Rollback for older (08_reserve_gpus.yaml) configuration

- Configured systems:
  - **bcn1**: Desktop system with 2× NVIDIA RTX 3090s with mixed configuration:
    - One RTX 3090 (PCI 01:00.0) bound to vfio-pci for VM passthrough
    - One RTX 3090 (PCI 08:00.0) kept with NVIDIA driver for host OS
    - System also has AMD iGPU (Raphael) available
    - **Status: Working correctly** - GPU at 01:00.0 bound to vfio-pci, AMD GPU used for display
  - **bcn2**: Headless server with NVIDIA GTX 1080Ti 
    - **Status: Working correctly** - GTX 1080Ti bound to vfio-pci

### Implementation Details
- For systems with identical GPUs (like bcn1 with two RTX 3090s), we use:
  - Systemd service that runs at boot to bind specific PCI slots to vfio-pci
  - Direct driver_override method instead of vfio-pci kernel module parameters
  - Only blacklist nouveau (open source NVIDIA driver), not the proprietary NVIDIA driver
- For systems with different GPUs, simpler vendor:device ID blacklisting works well

### Mixed GPU Setup (bcn1)
For bcn1's mixed GPU configuration:
1. A systemd service (vfio-bind-01-00.0.service) runs at boot time
2. The service executes a script that:
   - Loads vfio kernel modules
   - Unbinds any existing driver from the 01:00.0 PCI slot
   - Sets driver_override to vfio-pci for that specific slot
   - Forces a bind to vfio-pci
   - Also binds the associated audio device (01:00.1) to vfio-pci
3. This allows selective binding of one RTX 3090 while leaving the other available to the host

### Improved Test Playbook
The test playbook (38_test_gpu_reservation.yaml) has been enhanced to:
1. Support mixed GPU setups like bcn1 with special handling for IOMMU group binding
2. Use multiple methods to detect IOMMU enablement:
   - Checking kernel logs (dmesg)
   - Examining kernel parameters
   - Verifying vfio-pci module loading
   - Checking if GPUs are actually bound to vfio-pci
3. Explicitly convert numeric values to integers for reliable comparison
4. Provide detailed diagnostics for troubleshooting

### Verification After Reboot
After rebooting the systems, verify GPU passthrough with:
```bash
# Run verification playbook for all systems
./scripts/run_ansible.sh ansible/00_initial_setup/38_test_gpu_reservation.yaml

# Check VFIO binding manually if needed
./scripts/run_ssh_command.sh bcn1 "lspci -nnk | grep -A3 NVIDIA"
./scripts/run_ssh_command.sh bcn1 "systemctl status vfio-bind*"
./scripts/run_ssh_command.sh bcn2 "lspci -nnk | grep -A3 NVIDIA"
```