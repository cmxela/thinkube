# 00 Initial Setup

## Overview

The Initial Setup component establishes the foundation for the Thinkube deployment by configuring SSH access between servers and setting up environment variables. This is the first phase of deployment and must be completed successfully before continuing.

## Playbooks

### 10_setup_ssh_keys.yaml
- **Purpose**: Establishes bidirectional SSH access between all baremetal servers
- **Target Hosts**: `baremetal` (all physical servers in the baremetal group)
- **Prerequisites**: 
  - All servers must be accessible via SSH with password authentication
  - Sudo access on all servers
- **Required Variables**:
  - `ansible_host`: IP address of each server (in inventory)
- **Optional Variables**:
  - `ssh_key_name`: Name of the SSH key to generate (default: thinkube_cluster_key)
  - `ssh_key_type`: Type of SSH key to generate (default: ed25519)
- **Outputs**: 
  - SSH keys generated on all servers
  - Each server can SSH to every other server without password
  - SSH config files created with hostname aliases
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/10_setup_ssh_keys.yaml --ask-pass --ask-become-pass
  ```

### 20_setup_env.yaml
- **Purpose**: Sets up environment variables from inventory
- **Target Hosts**: `localhost` (runs only on the Ansible controller)
- **Prerequisites**: 
  - SSH keys must be properly configured
- **Required Variables**:
  - Variables defined in inventory (domain_name, admin_username, etc.)
- **Outputs**: 
  - Environment file created at ~/.env with required variables
  - Symbolic link created from ~/.env to project root (.env)
  - Variables added to environment
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/20_setup_env.yaml
  ```

### 18_test_ssh_connectivity.yaml
- **Purpose**: Tests SSH connectivity between all servers
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**:
  - SSH keys must be set up
- **Required Variables**:
  - None (uses inventory host definitions)
- **What it Tests**:
  - Validates SSH connectivity between all servers
  - Checks proper hostname resolution
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/18_test_ssh_connectivity.yaml
  ```

### 19_reset_ssh_config.yaml
- **Purpose**: Resets SSH configuration if needed
- **Target Hosts**: `baremetal` (all physical servers)
- **When to Use**:
  - When SSH configuration needs to be rebuilt
  - When keys need to be regenerated
- **Required Variables**:
  - None (uses inventory host definitions)
- **What it Removes**:
  - SSH keys for Thinkube
  - SSH configuration in ~/.ssh/config
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/19_reset_ssh_config.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

## Dependencies

- SSH server must be installed on all hosts
- Password-based SSH access must be enabled initially
- All hosts must be reachable by IP address

## Common Issues and Troubleshooting

- **SSH Connection Failure**: 
  - Ensure SSH service is running (`systemctl status sshd`)
  - Verify password authentication is enabled in `/etc/ssh/sshd_config`
  - Check firewall settings (`ufw status` or `firewalld status`)

- **Permission Issues**: 
  - Run `chmod 700 ~/.ssh && chmod 600 ~/.ssh/*` to set proper permissions
  - Verify ownership with `ls -la ~/.ssh`

- **Environment Variables Not Loaded**: 
  - Run `source ~/.env` to load variables into current shell
  - Check if ~/.env is sourced in ~/.bashrc

## Component-Specific Guidelines

- Always use the most secure SSH key type available (ed25519)
- Never store private keys in version control
- Ensure proper permissions on SSH directories and files
- The SSH setup must work for both interactive and non-interactive sessions