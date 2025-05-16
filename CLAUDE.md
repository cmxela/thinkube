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
- **Module Names**: Use fully qualified names (e.g., `ansible.builtin.command` not `command`)
- **Tasks**: Always include descriptive name field
- **Facts**: Default to `gather_facts: true`
- **Error Handling**: Always fail fast on critical errors
- **Become**: Never use become at playbook level, only for specific tasks
- **DNS Usage**: Use DNS hostnames, eliminate hardcoded IPs

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
   - Replace `gato-p` with `k8s-control-node`
   - Replace `gato-w1` with `k8s-worker-nodes`

3. **Variable Compliance**
   - Move ALL hardcoded values to inventory variables
   - No defaults in playbooks
   - Common migrations:
     - `cmxela.com` → `{{ domain_name }}`
     - `192.168.191.100` → `{{ primary_ingress_ip }}`
     - `alexmc` → `{{ admin_username }}`

4. **TLS Certificate Migration**
   - Replace manual certificate copying with Cert-Manager
   - Ensure the same certificate domains/SANs are preserved
   - Use Certificate resources instead of manual Secret creation

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

### AI-Generated Content

Mark all AI-generated or AI-assisted content:
- Use 🤖 emoji in comments
- Add `[AI-assisted]` to commit messages
- Track in AI_CONTRIBUTIONS.md
- Clearly separate AI analysis from human decisions