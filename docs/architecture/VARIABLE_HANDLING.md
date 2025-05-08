# Variable Handling Policy

This document establishes clear guidelines for handling variables in Thinkube deployment playbooks.

## Core Principle

**Playbooks must never include defaults for installation-specific variables.** The trusted source of truth for all configuration is the inventory file and environment variables.

## Variable Categories

### Category 1: Required Installation-Specific Variables

These variables **MUST NOT** have defaults in playbooks. Playbooks should fail immediately with a clear error message if these are not defined.

Examples:
- `domain_name` - The primary domain for services
- `network_cidr` - IP range for the network
- `zerotier_network_id` - ZeroTier network identifier
- `admin_username` - Administrative username
- IP address ranges and assignments
- Hostnames and FQDNs
- DNS server addresses
- Interface names for critical network interfaces

**Implementation requirement:** All playbooks must verify these variables exist before proceeding with any tasks.

```yaml
# Example verification
- name: Verify required variables are defined
  ansible.builtin.assert:
    that:
      - domain_name is defined and domain_name != ""
      - network_cidr is defined and network_cidr != ""
      - zerotier_network_id is defined and zerotier_network_id != ""
    fail_msg: "ERROR: Required variables are not defined. Please ensure all required variables are set in inventory."
```

### Category 2: Technical/Advanced Variables

These variables MAY have defaults in playbooks, but should be documented.

Examples:
- `ssh_key_name` - Name of SSH key file (can default to "thinkube_cluster_key")
- `ssh_key_type` - Type of SSH key (can default to "ed25519")
- Timeout values
- Retry counts
- Technical parameters that don't affect functionality
- Performance tuning parameters

**Implementation requirement:** Defaults should be clearly documented in the playbook header.

```yaml
# Example default with documentation
# Variable: ssh_key_name
# Default: thinkube_cluster_key
# Purpose: Filename for SSH keys, primarily for avoiding collisions
ssh_key_name: "{{ ssh_key_name | default('thinkube_cluster_key') }}"
```

## Variable Definition Locations

### 1. Inventory Files
- Location: `inventory/inventory.yaml` and `inventory/group_vars/*`
- Purpose: Define all installation-specific variables
- Content: All Category 1 variables MUST be defined here

### 2. Environment Variables
- Location: User's environment (exported or in ~/.env)
- Purpose: Define sensitive information and temporary overrides
- Content: Passwords, tokens, and other sensitive information

### 3. Playbook Defaults
- Location: Within playbooks
- Purpose: ONLY for Category 2 variables (technical/advanced)
- Content: Sensible defaults for non-critical configuration

## Verification Practices

All playbooks MUST:

1. Verify required variables exist at the start of execution
2. Fail immediately with clear error messages if required variables are missing
3. Document all variables used, their purpose, and where they should be defined
4. Use `assert` tasks to validate variable values meet requirements

## Example Implementation

```yaml
---
# Example playbook with proper variable handling

- name: Setup Component X
  hosts: all
  gather_facts: true
  
  tasks:
    - name: Verify required variables
      ansible.builtin.assert:
        that:
          - domain_name is defined and domain_name != ""
          - network_cidr is defined and network_cidr != ""
        fail_msg: >
          ERROR: Required variables not defined! Please ensure these variables 
          are set in inventory. See docs/architecture/VARIABLE_HANDLING.md for details.
    
    - name: Set technical variables with defaults
      ansible.builtin.set_fact:
        # Technical variable - can have default
        ssh_key_name: "{{ ssh_key_name | default('thinkube_cluster_key') }}"
        retry_count: "{{ retry_count | default(3) }}"
      
    # Proceed with tasks...
```

## Error Messages

When variables are missing, error messages must be clear and helpful. Example:

```
ERROR: Required variable 'domain_name' is not defined.

This variable must be set in your inventory file at:
inventory/inventory.yaml or inventory/group_vars/all.yml

Example value: example.com

For more information, see docs/architecture/VARIABLE_HANDLING.md
```