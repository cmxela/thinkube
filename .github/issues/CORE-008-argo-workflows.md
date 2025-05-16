---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-008] Deploy Argo Workflows'
labels: requirement, milestone-2, core
assignees: ''

---

## Component Requirement

### Description
Deploy Argo Workflows and Argo Events for workflow automation and event-driven processing. Includes Keycloak SSO integration, artifact storage configuration with MinIO, and both UI and gRPC access.

### Component Details
- **Component Name**: Argo Workflows & Argo Events
- **Namespace**: argo
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/argo-workflows/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates
- [ ] Update module names to FQCN - Mixed compliance
- [ ] Verify variable compliance - Needs work

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working via Keycloak OIDC
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] Argo Events operational
- [ ] Artifact storage configured with MinIO
- [ ] Service account tokens configured
- [ ] gRPC endpoint accessible

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes  
- CORE-003: Cert-Manager (for TLS)
- CORE-004: Keycloak (for SSO)
- CORE-006: MinIO (for artifact storage)

**Required Configurations:**
- Keycloak client for Argo
- TLS certificates for both UI and gRPC
- MinIO bucket for artifacts
- Environment variable: KEYCLOAK_ADMIN_PASSWORD

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [ ] Namespace: "argo"
- [ ] Release names: "argo-workflows", "argo-events"
- [ ] Chart repository URL
- [ ] Service type: "ClusterIP"
- [ ] OIDC configuration
- [ ] Artifact repository settings
- [ ] Resource limits
- [ ] gRPC configuration

### TLS Certificate Changes
- [ ] Current method: Manual TLS secret creation
- [ ] Cert-Manager resources needed:
  - Certificate for UI endpoint
  - Certificate for gRPC endpoint
- [ ] Domains required:
  - `{{ argo_hostname }}`
  - `{{ argo_grpc_hostname }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbooks for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook (71_setup_argo.yaml)
5. [ ] Migrate Keycloak client setup (70r_setup_argo_keycloak.yaml)
6. [ ] Migrate token configuration (72_setup_argo_token.yaml)
7. [ ] Migrate artifact storage setup (73_setup_argo_artifacts.yaml)
8. [ ] Replace manual TLS with cert-manager
9. [ ] Add resource limits for all components
10. [ ] Test workflow execution
11. [ ] Create rollback playbook
12. [ ] Update documentation
13. [ ] Create PR

### Verification Steps
```bash
# 1. Check Argo deployment
kubectl get pods -n argo
kubectl get ingress -n argo
helm list -n argo

# 2. Verify Argo Events
kubectl get eventsources -n argo
kubectl get eventbus -n argo
kubectl get sensors -n argo

# 3. Test UI access
curl -I https://argo.example.com

# 4. Test workflow submission
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml

# 5. Check SSO integration
# Login via Argo UI with Keycloak credentials

# 6. Verify artifact storage
kubectl get secret -n argo | grep artifact
argo logs -n argo @latest
```

### Resource Requirements
- CPU: 500m request, 1000m limit (controller)
- Memory: 256Mi request, 512Mi limit (controller)
- CPU: 100m request, 500m limit (server)
- Memory: 128Mi request, 256Mi limit (server)

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**Files**:
- `playbooks/services/71_setup_argo.yaml` - Main deployment
- `playbooks/services/70r_setup_argo_keycloak.yaml` - Keycloak client
- `playbooks/services/72_setup_argo_token.yaml` - Token configuration
- `playbooks/services/73_setup_argo_artifacts.yaml` - Artifact storage

**Key Features (71_setup_argo.yaml)**:
1. Deploys both Argo Workflows and Argo Events
2. Uses official Helm charts
3. Configures OIDC authentication
4. Sets up separate ingress for UI and gRPC
5. Creates SSO secrets from Keycloak
6. Configures RBAC (disabled by default)

**Key Features (70r_setup_argo_keycloak.yaml)**:
1. Creates Keycloak client for Argo
2. Configures redirect URIs
3. Retrieves client secret
4. Sets up proper scopes

**Key Features (72_setup_argo_token.yaml)**:
1. Creates system-level service account
2. Generates authentication token
3. Stores in ~/.argo/kube/config

**Key Features (73_setup_argo_artifacts.yaml)**:
1. Configures MinIO integration
2. Creates artifact repository secret
3. Patches workflow controller config
4. Sets up bucket and credentials

**Special Considerations**:
- Dual deployment (Workflows + Events)
- Complex OIDC configuration
- Separate endpoints for UI and gRPC
- Artifact storage requires MinIO
- Service account token management
- Helm-based deployment
- Multiple configuration files