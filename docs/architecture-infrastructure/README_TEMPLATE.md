# Component Name

## Overview

Brief description of this component's purpose and role in the Thinkube deployment.

## Playbooks

### X0_base_playbook.yaml
- **Purpose**: Description of what this playbook does
- **Target Hosts**: Specific inventory group this playbook targets (e.g., `baremetal`, `microk8s_control_plane`, etc.)
- **Prerequisites**: List of conditions that must be met before running
- **Required Variables**: Variables that must be defined in inventory
- **Optional Variables**: Variables that have defaults in the playbook
- **Outputs**: Expected state after successful execution
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/path/to/playbook.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### X1_configuration_playbook.yaml
- **Purpose**: Description of what this playbook does
- **Target Hosts**: Specific inventory group this playbook targets
- **Prerequisites**: List of conditions that must be met before running
- **Required Variables**: Variables that must be defined in inventory
- **Optional Variables**: Variables that have defaults in the playbook
- **Outputs**: Expected state after successful execution 
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/path/to/playbook.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### X8_test_playbook.yaml
- **Purpose**: Tests functionality of this component
- **Target Hosts**: Specific inventory group this playbook targets
- **Prerequisites**: Component must be installed
- **Required Variables**: Variables that must be defined in inventory
- **What it Tests**: List of specific tests performed
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/path/to/playbook.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### X9_rollback_playbook.yaml
- **Purpose**: Reverts changes made by the installation
- **Target Hosts**: Specific inventory group this playbook targets
- **When to Use**: Circumstances where rollback is appropriate
- **Required Variables**: Variables that must be defined for rollback
- **What it Removes**: List of changes that will be reverted
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/path/to/playbook.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

## Dependencies

- List of components this component depends on
- Required system packages or configurations

## Common Issues and Troubleshooting

- Issue 1: Description and solution
- Issue 2: Description and solution

## Component-Specific Guidelines

Any special guidelines or notes specific to this component.