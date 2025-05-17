# MicroK8s Control Node

This directory contains playbooks for installing and managing MicroK8s on the control node as part of the Thinkube platform.

## Overview

MicroK8s is the lightweight Kubernetes distribution used by Thinkube. This component:
- Installs MicroK8s via snap package
- Configures the control node with proper networking
- Enables required addons (DNS, storage, Helm)
- Sets up kubectl and helm wrapper scripts
- Integrates with the Thinkube alias system

## Playbooks

### 10_install_microk8s.yaml
Main installation playbook that:
- Installs MicroK8s (classic snap)
- Configures node IP
- Adds user to microk8s group
- Enables required and optional addons
- Creates kubectl/helm wrappers
- Integrates with Thinkube alias system

### 18_test_control.yaml
Test playbook that verifies:
- MicroK8s installation status
- Node readiness
- Addon status
- kubectl/helm functionality
- Alias system integration

### 19_rollback_control.yaml
Rollback playbook that:
- Removes MicroK8s snap
- Cleans up configuration directories
- Removes kubectl/helm wrappers
- Removes aliases from Thinkube system
- Removes user from microk8s group

## Usage

### Installation
```bash
# Install MicroK8s on control node
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/microk8s/10_install_microk8s.yaml

# Verify installation
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/microk8s/18_test_control.yaml
```

### Rollback
```bash
# Remove MicroK8s completely
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/microk8s/19_rollback_control.yaml
```

## Requirements

- Ubuntu 22.04+ or compatible OS
- Snapd installed and running
- User account with sudo privileges
- Thinkube shell environment already configured

## Configuration

The playbooks use variables from the inventory:
- `control_node_ip`: IP address for the control node
- `admin_username`: User to configure
- `kubectl_bin`: Path to kubectl command
- `helm_bin`: Path to helm command

## Alias Integration

This component integrates with the Thinkube common alias system by creating:
- `kubectl_aliases.json`: kubectl shortcuts (k, kgp, kgs, etc.)
- `helm_aliases.json`: helm shortcuts (h, hl, hi, etc.)

Aliases are automatically loaded by the Thinkube shell environment.

## Notes

- User needs to log out/in after installation for group membership to take effect
- MicroK8s runs as a snap with strict confinement
- The control node IP is configured specifically to avoid issues with multi-homed systems
- Dashboard addon is optional and disabled by default

## Troubleshooting

### MicroK8s not starting
```bash
# Check snap status
snap list microk8s
sudo microk8s inspect

# Check logs
journalctl -u snap.microk8s.daemon-kubelite -f
```

### kubectl not working
```bash
# Verify wrapper script
ls -la ~/.local/bin/kubectl

# Check direct access
/snap/bin/microk8s.kubectl get nodes
```

### Aliases not working
```bash
# Regenerate aliases
~/.thinkube_shared_shell/scripts/regenerate_aliases.sh

# Source shell config
source ~/.bashrc  # or ~/.zshrc, config.fish
```

## Migration Notes

This component was migrated from thinkube-core's `20_install_microk8s_planner.yaml` with the following changes:
- Updated to use FQCN for all modules
- Integrated with Thinkube common alias system
- Removed custom shell configuration in favor of centralized system
- Enhanced test coverage
- Added comprehensive rollback functionality