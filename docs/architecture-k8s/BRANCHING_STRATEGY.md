# Git Branching Strategy for Milestone 2

## Overview

This document defines the Git branching strategy for Milestone 2 (Core Services). The approach uses a branch-per-component model, except for infrastructure components which are grouped together.

## Branch Structure

### Infrastructure Components (Single Branch)
All core infrastructure components are developed in a single branch:

```
feature/k8s-infrastructure
├── microk8s setup
├── ingress controllers  
├── cert-manager
└── coredns configuration
```

### Core Services (Individual Branches)
Each core service gets its own feature branch:

```
feature/keycloak
feature/postgresql
feature/minio
feature/harbor
feature/argo-workflows
feature/argocd
feature/devpi
feature/awx
feature/mkdocs
feature/thinkube-dashboard
```

### Optional Components (Individual Branches)
Services deployed via AWX also get individual branches:

```
feature/prometheus-grafana
feature/opensearch
feature/jupyterhub
feature/code-server
feature/mlflow
feature/qdrant
feature/pgadmin
feature/knative
feature/penpot
feature/valkey
```

## Naming Conventions

- **Infrastructure**: `feature/k8s-infrastructure`
- **Components**: `feature/[component-name]`
- **Bug fixes**: `fix/[issue-number]-[short-description]`
- **Documentation**: `docs/[topic]`

## Development Workflow

### 1. Create GitHub Issue
- Use component requirement template
- Assign unique ID (CORE-XXX or OPT-XXX)
- Define acceptance criteria

### 2. Create Feature Branch
```bash
# For infrastructure
git checkout -b feature/k8s-infrastructure

# For individual components
git checkout -b feature/keycloak
```

### 3. Component Development
- Work within component directory: `ansible/40_core_services/[component]/`
- Follow established patterns
- Implement test-driven development

### 4. Testing
- Run component test playbook
- Verify all acceptance criteria
- Document test results

### 5. Create Pull Request
```markdown
## PR Title: [CORE-XXX] Deploy [Component Name]

### Changes
- Deployed [component] to [namespace]
- Configured [specific settings]
- Added test playbook
- Updated documentation

### Testing
- [ ] Test playbook runs successfully
- [ ] Component is accessible
- [ ] SSO integration works (if applicable)
- [ ] Resource limits configured

### Related Issue
Closes #XXX
```

### 6. Merge Strategy
- Squash and merge for clean history
- Ensure PR title follows convention
- Delete branch after merge

## Pull Request Guidelines

### PR Must Include:
1. Reference to GitHub issue
2. Test results/screenshots
3. Documentation updates
4. Passing CI checks

### PR Review Checklist:
- [ ] Code follows established patterns
- [ ] Variables are properly managed
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No hardcoded values

## Benefits

1. **Isolation**: Components developed independently
2. **Parallel Development**: Multiple components can progress simultaneously  
3. **Clean History**: Each component's evolution is clear
4. **Easy Rollback**: Can revert individual components
5. **Focused Reviews**: Smaller, component-specific PRs

## Example Commands

```bash
# Start new component
git checkout main
git pull origin main
git checkout -b feature/postgresql

# After development
git add ansible/40_core_services/postgresql/
git commit -m "[CORE-005] Deploy PostgreSQL shared instance"
git push origin feature/postgresql

# Create PR via GitHub UI or CLI
gh pr create --title "[CORE-005] Deploy PostgreSQL" \
  --body "Deploys PostgreSQL shared instance. Closes #5" \
  --base main
```

## Integration with AWX

For optional components deployed via AWX:
1. Develop component in feature branch
2. Merge to main
3. AWX pulls from main branch
4. Deploy using AWX job template

## Maintenance

- Keep branches short-lived
- Merge frequently to avoid conflicts
- Update from main regularly
- Delete branches after merge