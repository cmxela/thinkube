# CLAUDE.md - Master Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: When starting a new session, first read the [START_HERE.md](/START_HERE.md) document at the project root. This document contains the master task list and tracks implementation progress to ensure continuity between sessions.

**MILESTONE 2 FOCUS**: We are now in Milestone 2 (Core Services). All Kubernetes services should be implemented following the guidelines in this document.

## Project Overview

Thinkube is a home-based development platform built on Kubernetes, designed specifically for AI applications and agents.

## Architecture Documentation

### Infrastructure Documentation (Milestone 1)
- [Variable Handling Policy](/docs/architecture-infrastructure/VARIABLE_HANDLING.md) - **MUST READ: Rules for variable management**
- [Error Handling Standard](/docs/architecture-infrastructure/ERROR_HANDLING.md) - Standardized error handling
- [Ansible Roles](/docs/architecture-infrastructure/ANSIBLE_ROLES.md) - When to use roles

### Kubernetes Documentation (Milestone 2)
- [Component Architecture](/docs/architecture-k8s/COMPONENT_ARCHITECTURE.md) - Kubernetes services architecture
- [Playbook Structure](/docs/architecture-k8s/PLAYBOOK_STRUCTURE.md) - Component-based organization
- [Branching Strategy](/docs/architecture-k8s/BRANCHING_STRATEGY.md) - Git workflow

## Document Management Guidelines

**IMPORTANT**: Follow these rules for document versioning and archival:

1. **Never create "OLD" files**: Use Git for version control. Files like `README_OLD.md` or `START_HERE_OLD.md` should not exist.
2. **Milestone documentation is historical**: Files like `CLAUDE_MILESTONE1.md` preserve important context from completed milestones and must be retained.
3. **Use proper renaming**:
   - If updating a document for a new phase: create the new version and delete the old one
   - If preserving milestone context: rename with the milestone identifier (e.g., `START_HERE.md` → `START_HERE_MILESTONE1.md`)
4. **Git is the archive**: Previous versions can always be retrieved from Git history
5. **Keep the repository clean**: Remove temporary or backup files immediately

## Code Style Guidelines

- **YAML**: 2-space indentation, use list format for tasks with clear names
- **Variables**: 
  - Use snake_case for all variable names
  - Installation-specific variables MUST be defined in inventory, NEVER in playbooks
  - Only technical/advanced variables MAY have defaults in playbooks  
  - All playbooks MUST verify required variables exist before proceeding
  - **Admin Credentials**: Always use `admin_username` and `admin_password` (not component-specific variants like `keycloak_admin_username`)
  - **Environment Variables**: Use `ADMIN_PASSWORD` for admin credentials (not `KEYCLOAK_ADMIN_PASSWORD`)
  - Default `admin_username` is `tkadmin` for neutral cross-application use
- **Module Names**: Use fully qualified names (e.g., `ansible.builtin.command` not `command`)
- **Tasks**: Always include descriptive name field
- **Facts**: Default to `gather_facts: true`
- **Error Handling**: Always fail fast on critical errors
- **Become**: Never use become at playbook level, only for specific tasks
- **DNS Usage**: Use DNS hostnames, eliminate hardcoded IPs

## Command Execution Reference

### Running Commands in Kubernetes Control Node (tkc)

To run commands in the Kubernetes control node (tkc), use the `run_ssh_command.sh` script:

```bash
# General syntax
./scripts/run_ssh_command.sh tkc "command_to_run"

# Example: Check pod status
./scripts/run_ssh_command.sh tkc "microk8s.kubectl get pods -n registry"

# Example: Check logs
./scripts/run_ssh_command.sh tkc "microk8s.kubectl logs -n registry deploy/harbor-core -c harbor-core --tail 50"
```

Key kubectl commands for troubleshooting:
- List pods: `microk8s.kubectl get pods -n <namespace>`
- Check logs: `microk8s.kubectl logs -n <namespace> <pod-name> -c <container-name> --tail <number>`
- Describe pod: `microk8s.kubectl describe pod -n <namespace> <pod-name>`
- Check services: `microk8s.kubectl get svc -n <namespace>`
- Check ingress: `microk8s.kubectl get ingress -n <namespace>`

## Playbook Numbering Convention

- **10-17**: Main component setup and configuration
- **18**: Testing and validation
- **19**: Rollback and recovery procedures

## Milestone 2: Core Services Guidelines

### Component Directory Structure

```
ansible/40_thinkube/
├── core/                           # Essential platform components
│   ├── infrastructure/            # MicroK8s, ingress, cert-manager, coredns
│   ├── keycloak/                 # Each service gets its own directory
│   ├── postgresql/
│   └── ...
└── optional/                      # AWX-deployed components
    ├── prometheus/
    └── ...
```

Each component directory contains:
- `10_deploy.yaml` - Main deployment playbook
- `15_configure_*.yaml` - Additional configuration (if needed)
- `18_test.yaml` - Test playbook
- `19_rollback.yaml` - Rollback playbook
- `README.md` - Component documentation

### Migration Requirements from thinkube-core

When migrating playbooks from thinkube-core:

**CRITICAL**: Preserve ALL original functionality while making minimal changes. The goal is compliance with guidelines, not rewriting working code.

1. **Functionality Preservation Check**
   - Document all features in the original playbook
   - Ensure migrated version maintains exact same functionality
   - Make ONLY the minimum changes required for compliance
   - If uncertain about a change, preserve the original approach
   - Test that the service behaves identically after migration

2. **Host Group Updates**
   - Replace `gato-p` with `microk8s_control_plane` (NOT `k8s-control-node`)
   - Replace `gato-w1` with `microk8s_workers` (NOT `k8s-worker-nodes`)
   
   **CRITICAL: Host Group Reference**
   - `microk8s_control_plane`: Control plane node (host: tkc)
   - `microk8s_workers`: Worker nodes (hosts: tkw1, bcn1)
   - `microk8s`: All Kubernetes nodes (both control plane and workers)
   
   **NEVER use incorrect group names like:**
   - `gato-p` (old name from thinkube-core)
   - `k8s-control-node` (incorrect name)
   - `gato-w1` (old name from thinkube-core)
   - `k8s-worker-nodes` (incorrect name)

3. **Variable Compliance**
   - Move ALL hardcoded values to inventory variables
   - No defaults in playbooks
   - Common migrations:
     - `cmxela.com` → `{{ domain_name }}`
     - `192.168.191.100` → `{{ primary_ingress_ip }}`
     - `alexmc` → `{{ admin_username }}`

4. **TLS Certificate Migration**
   - **CRITICAL: ALWAYS copy the wildcard certificate from default namespace**
   - The source certificate name is `thinkube-com-tls` in the `default` namespace
   - Components must copy this certificate to their namespaces
   - Follow the naming convention `{{ component_namespace }}-tls-secret`
   - Example of the correct approach:
     ```yaml
     - name: Get wildcard certificate from default namespace
       kubernetes.core.k8s_info:
         kubeconfig: "{{ kubeconfig }}"
         api_version: v1
         kind: Secret
         namespace: default
         name: thinkube-com-tls
       register: wildcard_cert
       failed_when: wildcard_cert.resources | length == 0

     - name: Copy wildcard certificate to component namespace
       kubernetes.core.k8s:
         kubeconfig: "{{ kubeconfig }}"
         state: present
         definition:
           apiVersion: v1
           kind: Secret
           metadata:
             name: "{{ component_namespace }}-tls-secret"
             namespace: "{{ component_namespace }}"
           type: kubernetes.io/tls
           data:
             tls.crt: "{{ wildcard_cert.resources[0].data['tls.crt'] }}"
             tls.key: "{{ wildcard_cert.resources[0].data['tls.key'] }}"
     ```
   - **NEVER** create TLS secrets from certificate files on disk

5. **Module Name Compliance**
   - Use fully qualified collection names
   - `kubernetes.core.k8s` not `k8s`

### Migration Validation Checklist

Before considering a migration complete:
- [ ] All original features are preserved
- [ ] Service configuration is identical
- [ ] Same ports, protocols, and endpoints
- [ ] Authentication/authorization unchanged
- [ ] Resource limits/requests preserved
- [ ] Environment variables maintained
- [ ] Volume mounts and storage identical
- [ ] Network policies preserved
- [ ] Service dependencies respected

### Development Workflow

1. **Create GitHub Issue**: Use component requirement template
2. **Create Feature Branch**: Per branching strategy
3. **Create Test First**: Write `18_test.yaml` before implementation
4. **Implement Migration**: Follow all compliance rules
5. **Verify Tests Pass**: Run test playbook
6. **Create PR**: Link to issue, include test results
7. **Merge to Main**: After review and approval

**CRITICAL: Never Commit Without Testing**
- **NEVER commit without successfully RUNNING 10_deploy.yaml and 18_test.yaml**
- Syntax checking (--syntax-check) is NOT sufficient
- All code MUST be deployed and tested in a real environment before commit
- At minimum, execute with actual deployment and verify:
  1. `10_deploy.yaml` - Successful real deployment (not just syntax check)
  2. `18_test.yaml` - All tests pass in the live environment

**IMPORTANT**: "Run" always means actual execution against the infrastructure, not syntax validation

### AI-Generated Content

Mark all AI-generated or AI-assisted content:
- Use 🤖 emoji in comments and code
- Add footer to commit messages (see Commit Message Format below)
- Track major contributions in AI_CONTRIBUTIONS.md
- Clearly separate AI analysis from human decisions

## Commit Message Format

Follow this format for all commits:

```
Type CORE-XXX: Short description

- Bullet point explaining change
- Another bullet point
- Continue as needed

[Optional: Fixes #XXX or Closes #XXX]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Where Type is one of:
- `Implement` - New feature or component
- `Fix` - Bug fix
- `Update` - Enhancement or modification
- `docs` - Documentation only changes
- `refactor` - Code refactoring

## Playbook Header Guidelines

All playbooks MUST include a standardized header:

```yaml
---
# ansible/path/to/playbook.yaml
# Description:
#   Brief description of what this playbook does
#   Additional details about its purpose
#
# Requirements:
#   - List prerequisites (e.g., MicroK8s must be installed)
#   - Required variables from inventory
#   - Environment variables needed
#
# Usage:
#   cd ~/thinkube
#   ./scripts/run_ansible.sh ansible/path/to/playbook.yaml
#
# Variables from inventory:
#   - variable_name: Description of variable
#   - another_var: What this variable controls
#
# Dependencies:
#   - Component dependencies (e.g., CORE-001 must be complete)
#   - External services required
#
# [Optional for AI-generated playbooks]
# 🤖 [AI-assisted]
```

Test and rollback playbooks can use a simplified header focusing on their specific purpose.