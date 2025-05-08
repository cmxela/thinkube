# Ansible Roles Policy for Thinkube

This document outlines our approach to using Ansible roles in the Thinkube project, addressing the unique considerations of Infrastructure as Code (IaC) compared to traditional software development.

## Core Principles

1. **Selective Role Usage**: Roles are used selectively, not as a default organizational structure
2. **Self-Contained Playbooks**: Playbooks should generally be self-contained and complete
3. **Explicit Over Implicit**: Favor explicit configuration over role abstraction
4. **Documentation Priority**: Documentation of behavior is more important than code reuse
5. **Consistent Variable Handling**: Roles must adhere to the same variable handling rules as playbooks

## When to Use Roles

Roles in Thinkube are appropriate in these specific scenarios:

### 1. Cross-Environment Components

For components that need consistent configuration across different environments:

- SSH key setup and configuration (baremetal hosts and LXD VMs)
- User management and permissions
- Common system configurations

### 2. Third-Party Integrations

When integrating with third-party systems that require complex, well-defined interactions:

- Keycloak client configuration
- Certificate management
- OAuth integration

### 3. Highly Technical, Reused Components

For specialized technical components that:
- Are used across multiple deployment phases
- Require specific expertise to implement correctly
- Have well-defined and stable interfaces
- Would be difficult to implement consistently without abstraction

Examples include:
- LXD container/VM lifecycle management
- ZeroTier network configuration
- GPU passthrough setup

## Variable Handling in Roles

Roles **MUST** follow the same variable handling policies as playbooks:

### 1. No Defaults for Required Variables

Required installation-specific variables (Category 1) must NOT have defaults in `defaults/main.yml`:

```yaml
# ❌ INCORRECT: Setting defaults for required variables
---
# defaults/main.yml
domain_name: example.com
admin_username: admin
```

```yaml
# ✅ CORRECT: No defaults for required variables
---
# tasks/main.yml
- name: Verify required variables
  ansible.builtin.assert:
    that:
      - domain_name is defined
      - admin_username is defined
    fail_msg: >-
      
      ══════════════════════════════════════════
      ERROR: Missing Required Variables
      ══════════════════════════════════════════
      
      The following variables are required:
        - domain_name
        - admin_username
      
      These must be defined in inventory.
      ══════════════════════════════════════════
```

### 2. Technical Variables May Have Defaults

Technical/advanced variables (Category 2) may have reasonable defaults:

```yaml
# ✅ CORRECT: Defaults for technical variables
---
# defaults/main.yml
ssh_key_bits: 4096
ssh_key_type: ed25519
```

### 3. Document All Variables

All variables must be documented in `README.md` and categorized:

```markdown
## Variables

### Required Installation-Specific Variables (No Defaults)
- `domain_name`: Domain name for the installation
- `admin_username`: Username for the admin account

### Technical Variables (With Defaults)
- `ssh_key_bits`: Number of bits for SSH key (Default: 4096)
- `ssh_key_type`: Type of SSH key (Default: ed25519)
```

## Role Metadata and Licensing

### Consistent Licensing

All roles **MUST** use the Apache 2.0 license in their metadata:

```yaml
# meta/main.yml
galaxy_info:
  author: Thinkube Team
  description: Role for managing SSH configuration
  license: Apache-2.0  # IMPORTANT: Use Apache-2.0, not MIT
  
  min_ansible_version: 2.14.0
  
  platforms:
    - name: Ubuntu
      versions:
        - jammy
        - noble
```

### Required Metadata Fields

Each role must include:
- `author`: The role's author (usually "Thinkube Team")
- `description`: A clear, concise description
- `license`: Always "Apache-2.0"
- `min_ansible_version`: Minimum supported Ansible version
- `platforms`: Supported OS platforms and versions

## When NOT to Use Roles

Avoid roles in these scenarios:

### 1. Single-Use Configuration

When a configuration is specific to one deployment phase or component, implement it directly in the playbook rather than creating a role.

### 2. Simple Tasks

When tasks are simple and straightforward, adding role abstraction adds unnecessary complexity.

### 3. When Documentation Would Suffer

If using a role would make it harder to understand what a playbook does, prefer explicit tasks in the playbook.

### 4. When Abstraction Adds Complexity

If creating a role requires complex parameter handling, conditional logic, or makes debugging more difficult, avoid it.

## Role Design Guidelines

When roles are used, they should follow these guidelines:

### 1. Explicit Interface

Roles must have explicitly documented interfaces with:
- Required variables (with validation)
- Optional variables (with clear defaults)
- Expected outputs or registered variables
- Side effects and dependencies

### 2. Fail Fast and Explicitly

Roles should validate inputs and fail with clear error messages using the same formatting standards as playbooks.

### 3. Limited Scope

Roles should do one thing and do it well, avoiding the temptation to include tangentially related functionality.

### 4. Consistent Organization

```
roles/
└── ssh_configuration/
    ├── README.md          # Documentation
    ├── defaults/          # Default variables (technical only)
    │   └── main.yml
    ├── tasks/             # Core implementation
    │   └── main.yml
    ├── templates/         # Templates if needed
    │   └── ssh_config.j2
    ├── vars/              # Internal variables
    │   └── main.yml
    └── meta/              # Dependencies and metadata
        └── main.yml       # Must specify Apache-2.0 license
```

## Identified Role Candidates

These components are candidates for implementation as roles:

1. **SSH Configuration**: Used for both baremetal hosts and LXD VMs
   - SSH key generation
   - SSH config deployment
   - SSH authorized keys management

2. **LXD Management**: Used across container and VM deployments
   - Profile creation and management
   - VM/container lifecycle
   - Resource allocation

3. **ZeroTier Networking**: Used in multiple environments
   - Installation and configuration
   - Network joining and routing
   - Identity management

4. **Keycloak Integration**: Used across multiple services
   - Client creation
   - Role mapping
   - User management

## Role Testing

Roles must have dedicated test playbooks that:

1. Verify correct operation with minimal parameters
2. Test error handling with invalid inputs
3. Verify idempotence (role can be run multiple times safely)

Example test structure:
```
roles/
└── ssh_configuration/
    └── tests/
        ├── inventory
        └── test.yml
```

## Conclusion

By following these guidelines, we ensure that roles are used appropriately to enhance consistency and reusability without sacrificing clarity or maintainability. The targeted use of roles for cross-environment components like SSH configuration provides value while avoiding unnecessary abstraction elsewhere.