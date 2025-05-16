---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-007] Deploy Harbor'
labels: requirement, milestone-2, core
assignees: ''

---

## Component Requirement

### Description
Deploy Harbor container registry for managing container images, with Keycloak SSO integration, project configuration for thinkube, and automatic public image mirroring capabilities.

### Component Details
- **Component Name**: Harbor
- **Namespace**: docker-ui
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/harbor/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates
- [ ] Update module names to FQCN - Mostly compliant
- [ ] Verify variable compliance - Needs work

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working via Keycloak OIDC
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] thinkube project created
- [ ] Robot account configured for Kubernetes
- [ ] Public image mirroring working
- [ ] Default registry configuration applied

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes
- CORE-003: Cert-Manager (for TLS)
- CORE-004: Keycloak (for SSO)
- Storage class available

**Required Configurations:**
- Keycloak client for Harbor
- TLS certificates
- Environment variable: KEYCLOAK_ADMIN_PASSWORD

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [ ] Namespace: "docker-ui"
- [ ] Release name: "harbor"
- [ ] Admin user: "admin"
- [ ] OIDC client configuration
- [ ] Harbor project name references
- [ ] Robot account name: "kaniko"
- [ ] Robot duration: 36500 days
- [ ] Various ports and service configurations

### TLS Certificate Changes
- [ ] Current method: LoadBalancer with external IP
- [ ] Cert-Manager resource needed: Certificate for harbor domain
- [ ] Domains required: `{{ harbor_registry }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbooks for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook (100_setup_harbor.yaml)
5. [ ] Migrate project setup (101_setup_harbor_thinkube.yaml)
6. [ ] Migrate registry configuration (102_setup_harbor_default_registry.yaml)
7. [ ] Migrate image mirroring (103_mirror_public_images.yaml)
8. [ ] Replace manual TLS with cert-manager
9. [ ] Add resource limits
10. [ ] Test registry functionality
11. [ ] Create rollback playbook
12. [ ] Update documentation
13. [ ] Create PR

### Verification Steps
```bash
# 1. Check Harbor deployment
kubectl get pods -n docker-ui
kubectl get svc -n docker-ui
helm list -n docker-ui

# 2. Test Harbor access
curl -I https://registry.example.com

# 3. Verify OIDC integration
# Login via Harbor UI with Keycloak credentials

# 4. Test registry operations
docker login registry.example.com
docker pull registry.example.com/library/nginx:latest
docker tag nginx:test registry.example.com/thinkube/nginx:test
docker push registry.example.com/thinkube/nginx:test

# 5. Check robot account
kubectl get secret -n docker-ui | grep robot
```

### Resource Requirements
- CPU: 1000m request, 4000m limit
- Memory: 2Gi request, 8Gi limit
- Storage: 100Gi (configurable)

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**Files**:
- `playbooks/core/100_setup_harbor.yaml` - Main deployment with OIDC
- `playbooks/core/101_setup_harbor_thinkube.yaml` - Project and robot account
- `playbooks/core/102_setup_harbor_default_registry.yaml` - Registry configuration
- `playbooks/core/103_mirror_public_images.yaml` - Image mirroring

**Key Features (100_setup_harbor.yaml)**:
1. Creates Keycloak client with groups scope
2. Sets up harbor-admins group
3. Configures OIDC authentication
4. Deploys Harbor using Helm chart
5. Uses LoadBalancer for external access
6. Configures multiple components (registry, portal, core, etc.)

**Key Features (101_setup_harbor_thinkube.yaml)**:
1. Creates thinkube project
2. Creates system-level robot account
3. Stores credentials in ~/.env
4. Configures permissions for push/pull

**Key Features (102_setup_harbor_default_registry.yaml)**:
1. Configures Harbor as default registry
2. Creates Kubernetes secret for authentication
3. Patches default service account

**Key Features (103_mirror_public_images.yaml)**:
1. Creates public-library project
2. Configures proxy cache for Docker Hub
3. Sets retention policies
4. Pre-populates with common images

**Special Considerations**:
- Complex OIDC configuration with Keycloak
- Multiple playbooks for complete setup
- LoadBalancer service with specific IP
- Robot account naming conventions
- Extensive image mirroring configuration
- Helm chart deployment
- Default registry configuration for Kubernetes