---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-004] Deploy Keycloak'
labels: requirement, milestone-2, core
assignees: ''

---

## Component Requirement

### Description
Deploy Keycloak identity provider for SSO authentication across the platform. This includes deploying Keycloak, creating kubernetes realm, configuring user profiles, creating admin user, and setting up cluster-admins group.

### Component Details
- **Component Name**: Keycloak
- **Namespace**: keycloak
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/keycloak/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates
- [ ] Update module names to FQCN - Needs attention
- [x] Verify variable compliance - Mostly compliant

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] kubernetes realm created
- [ ] Admin user configured with proper permissions
- [ ] cluster-admins group created
- [ ] Unmanaged attributes policy enabled

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes
- CORE-003: Cert-Manager (for TLS certificates)
- Ingress controller must be deployed

**Required Configurations:**
- Valid TLS certificates
- DNS configured for keycloak hostname
- Environment variable: KEYCLOAK_ADMIN_PASSWORD

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [ ] Keycloak image version: `quay.io/keycloak/keycloak:26.1.0`
- [ ] Namespace: keycloak (should be variable)
- [ ] Service ports: 8080, 9000
- [ ] Deployment arguments: ["start-dev"] (should be production mode)
- [ ] Replica count: 1
- [ ] Probe delays and timeouts
- [ ] Ingress annotations

### TLS Certificate Changes
- [ ] Current method: Manual TLS secret creation
- [ ] Cert-Manager resource needed: Certificate for keycloak hostname
- [ ] Domains required: `{{ keycloak_hostname }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbooks for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook (80_setup_keycloak.yaml)
5. [ ] Migrate configuration playbook (90_setup_keycloak4kubernetes.yaml)
6. [ ] Replace manual TLS with cert-manager Certificate
7. [ ] Add resource limits and production configuration
8. [ ] Test deployment and SSO
9. [ ] Create rollback playbook
10. [ ] Update documentation
11. [ ] Create PR

### Verification Steps
```bash
# 1. Check Keycloak deployment
kubectl get pods -n keycloak
kubectl get ingress -n keycloak

# 2. Verify realm creation
curl -s https://keycloak.example.com/admin/realms | jq '.[] | select(.realm=="kubernetes")'

# 3. Test admin login
curl -X POST https://keycloak.example.com/realms/kubernetes/protocol/openid-connect/token \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password"

# 4. Check group creation
# Via Keycloak admin console or API
```

### Resource Requirements
- CPU: 500m request, 1000m limit
- Memory: 512Mi request, 1Gi limit
- Storage: None (using external DB later)

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**Files**: 
- `playbooks/core/80_setup_keycloak.yaml` - Main deployment
- `playbooks/core/90_setup_keycloak4kubernetes.yaml` - Realm configuration

**Key Features (80_setup_keycloak.yaml)**:
1. Creates namespace and TLS secret
2. Deploys Keycloak service and deployment
3. Configures ingress with nginx annotations
4. Sets up proxy headers and health endpoints
5. Creates initial admin user
6. Waits for deployment readiness

**Key Features (90_setup_keycloak4kubernetes.yaml)**:
1. Creates/updates kubernetes realm
2. Sets unmanagedAttributePolicy to "ENABLED"
3. Creates cluster-admins group
4. Creates admin user with proper attributes
5. Assigns admin to cluster-admins group
6. Configures Kubernetes integration settings

**Module Naming Issues**:
- kubernetes.core.k8s used correctly (FQCN)
- ansible.builtin modules mostly FQCN compliant
- Some shell module usage without FQCN

**Special Considerations**:
- Currently using development mode (start-dev)
- Production deployment needs proper database
- Resource limits not configured
- Manual TLS certificate handling
- Admin password from environment variable
- Complex realm configuration via API
- Token-based authentication for realm setup