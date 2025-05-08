# Error Handling Standard

This document defines the standard approach to error handling across all Thinkube deployment playbooks, following the "fail fast" principle.

## Core Principles

1. **Fail Fast**: Fail immediately when any critical error is detected
2. **Clear Messages**: Provide clear, actionable error messages
3. **Validation First**: Validate all prerequisites before making changes
4. **No Recovery Attempts**: Don't attempt to auto-recover from failures
5. **Consistent Format**: Use a standard error message format

## Error Message Format

All error messages must follow this standard format:

```
ERROR: [Component] - [Brief error description]

DETAILS:
- [Specific details about what failed]
- [Current state information]
- [Variables or settings involved]

REQUIRED ACTION:
- [What the user needs to do to fix the issue]
- [Commands or steps to resolve]

REFERENCE: [Link to documentation or troubleshooting guide if available]
```

## Implementation in Playbooks

### 1. Variable Validation

Always validate required variables at the start of playbooks:

```yaml
- name: Verify required variables
  ansible.builtin.assert:
    that:
      - domain_name is defined and domain_name | length > 0
      - system_username is defined and system_username | length > 0
    fail_msg: |
      ERROR: Missing Required Variables
      
      DETAILS:
      - The following variables must be defined in inventory:
        - domain_name: {% if domain_name is defined %}✓{% else %}✗ missing{% endif %}
        - system_username: {% if system_username is defined %}✓{% else %}✗ missing{% endif %}
      
      REQUIRED ACTION:
      - Add missing variables to your inventory file at inventory/inventory.yaml
      - Or define them in inventory/group_vars/all.yml
      
      REFERENCE: See docs/architecture/VARIABLE_HANDLING.md
```

### 2. Environment Check Failures

When checking environment prerequisites:

```yaml
- name: Check for required tools
  ansible.builtin.command: which {{ item }}
  register: tool_check
  failed_when: false
  changed_when: false
  loop:
    - lxc
    - lxd
    - snap

- name: Fail if tools are missing
  ansible.builtin.fail:
    msg: |
      ERROR: Required Tools Missing
      
      DETAILS:
      - The following tools must be installed:
        {% for item in tool_check.results %}
        - {{ item.item }}: {% if item.rc == 0 %}✓{% else %}✗ missing{% endif %}
        {% endfor %}
      
      REQUIRED ACTION:
      - Install missing tools with:
        sudo apt update
        sudo apt install -y lxd snapd
      
      REFERENCE: See docs/architecture/00_initial_setup/README.md
  when: tool_check.results | selectattr('rc', 'ne', 0) | list | count > 0
```

### 3. Task Failure Handling

For critical tasks that must succeed:

```yaml
- name: Critical operation
  ansible.builtin.command: some_command
  register: command_result
  failed_when: 
    - command_result.rc != 0
    - "'expected_error_text' not in command_result.stderr"
  
- name: Fail with helpful message if operation failed
  ansible.builtin.fail:
    msg: |
      ERROR: Critical Operation Failed
      
      DETAILS:
      - Command: some_command
      - Exit code: {{ command_result.rc }}
      - Error message: {{ command_result.stderr }}
      
      REQUIRED ACTION:
      - Check logs at /var/log/app.log for details
      - Verify system permissions
      - Ensure service X is running
      
      REFERENCE: See docs/troubleshooting.md
  when: command_result.rc != 0
```

## Error Categories and Response

| Error Category | Example | Action |
|----------------|---------|--------|
| **Missing Variables** | Required variable not defined | Fail immediately with variable list |
| **Permission Issues** | Cannot write to directory | Fail with permissions check instructions |
| **Connectivity Problems** | Cannot reach service | Fail with network diagnostic instructions |
| **Resource Limitations** | Not enough disk space | Fail with resource requirements |
| **Dependency Issues** | Required service not running | Fail with dependency verification steps |

## Testing Error Handling

Each playbook should be tested for proper error handling by:

1. Deliberately omitting required variables
2. Running with insufficient permissions
3. Verifying that error messages are clear and actionable

## Examples

### Good Error Message

```
ERROR: DNS Server Unreachable

DETAILS:
- Failed to reach DNS server at 192.168.191.1
- Current network configuration: eth0 (192.168.1.101)
- ZeroTier status: not connected

REQUIRED ACTION:
- Verify DNS server is running: ssh dns1 systemctl status bind9
- Check ZeroTier connection: zerotier-cli listnetworks
- Ensure DNS server has correct firewall rules

REFERENCE: See docs/architecture/30_networking/README.md
```

### Poor Error Message (Avoid This)

```
Error: Failed to deploy. Command error.
```