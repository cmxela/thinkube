# Scripts Directory

This directory contains utility scripts for the Thinkube platform. These scripts simplify common operations and provide automation for various tasks.

## Script Inventory

| Script | Description | Status |
|--------|-------------|--------|
| `10_install-tools.sh` | Installs required tools and dependencies | Required |
| `setup_env_link.sh` | Creates a symbolic link from ~/.env to project root for environment variables | Required |
| `setup_lxd_cluster.sh` | Sets up the LXD cluster with predefined settings | Required |
| `update_task_status.py` | Updates task status in START_HERE.md | Required |
| `run_ansible.sh` | Wrapper script to simplify running Ansible playbooks with proper authentication | Required |
| `test_ansible_ssh.sh` | Diagnostic tool to test SSH connectivity for Ansible | Temporary - Can be deleted once SSH setup is stable |

## Script Details

### 10_install-tools.sh
Installs required tools and dependencies for the Thinkube platform. This script should be run during initial setup to ensure all necessary software is installed.

### setup_env_link.sh
Creates a symbolic link from `~/.env` to the project root directory's `.env` file. This allows environment variables to be shared between the user's shell and the project, while keeping sensitive data outside version control.

Usage:
```bash
./scripts/setup_env_link.sh
```

### setup_lxd_cluster.sh
Sets up the LXD cluster with predefined settings. This script automates the configuration of LXD across multiple hosts.

### update_task_status.py
A utility script to update task status in the START_HERE.md file. This helps track progress during implementation.

### run_ansible.sh
A wrapper script that simplifies running Ansible playbooks with proper authentication. It automatically:
1. Sources environment variables from ~/.env
2. Sets up appropriate SSH and sudo authentication
3. Runs the playbook with all necessary parameters

Usage:
```bash
./scripts/run_ansible.sh ansible/[path/to/playbook].yaml [additional options]
```

Example:
```bash
./scripts/run_ansible.sh ansible/20_lxd_setup/10_setup_lxd_cluster.yaml
```

### test_ansible_ssh.sh
A diagnostic tool to test SSH connectivity for Ansible. It tests both direct SSH and Ansible's SSH connection to verify configuration.

Usage:
```bash
./scripts/test_ansible_ssh.sh
```

Status: **Temporary** - This script can be deleted once SSH setup is stable.

## Environment Variables

Scripts in this directory typically rely on environment variables defined in the `.env` file:

- `ANSIBLE_SUDO_PASS` - Used for sudo operations in Ansible playbooks
- `ANSIBLE_SSH_PASS` - Used for SSH password authentication when keys aren't available
- `ZEROTIER_NETWORK_ID` - ZeroTier network identifier
- `ZEROTIER_API_TOKEN` - ZeroTier API token for network management
- Other inventory-specific variables

To set up environment variables, see the instructions in CLAUDE.md.