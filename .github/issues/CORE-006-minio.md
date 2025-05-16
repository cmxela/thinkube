---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-006] Deploy MinIO'
labels: requirement, milestone-2, core
assignees: ''

---

## Component Requirement

### Description
Deploy MinIO object storage for S3-compatible storage needs across the platform. Includes Keycloak SSO integration, persistent storage configuration, and both API and console access.

### Component Details
- **Component Name**: MinIO
- **Namespace**: minio
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/minio/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates
- [ ] Update module names to FQCN - Compliant
- [ ] Verify variable compliance - Needs work

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working via Keycloak OIDC
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] Persistent storage configured
- [ ] Both API and console accessible
- [ ] Policy-based authorization working

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes
- CORE-003: Cert-Manager (for TLS)
- CORE-004: Keycloak (for SSO)
- Storage class available

**Required Configurations:**
- Keycloak client for MinIO
- TLS certificates
- Environment variable: KEYCLOAK_ADMIN_PASSWORD

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [ ] Namespace: "minio"
- [ ] Image: "registry.cmxela.com/library/minio:latest"
- [ ] Root user: "cmxela"
- [ ] Storage capacity: "50Gi"
- [ ] Storage class: "microk8s-hostpath"
- [ ] Service ports
- [ ] Ingress annotations
- [ ] OIDC configuration values

### TLS Certificate Changes
- [ ] Current method: Manual TLS secret creation
- [ ] Cert-Manager resources needed:
  - Certificate for API endpoint
  - Certificate for console endpoint
- [ ] Domains required:
  - `{{ minio_api_hostname }}`
  - `{{ minio_console_hostname }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbooks for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook (40_setup_minio.yaml)
5. [ ] Migrate Keycloak client setup (41r_setup_minio_keycloak_client.yaml)
6. [ ] Migrate OIDC configuration (42_setup_minio_oidc.yaml)
7. [ ] Replace manual TLS with cert-manager
8. [ ] Add resource limits
9. [ ] Test S3 compatibility and SSO
10. [ ] Create rollback playbook
11. [ ] Update documentation
12. [ ] Create PR

### Verification Steps
```bash
# 1. Check MinIO deployment
kubectl get pods -n minio
kubectl get pvc -n minio
kubectl get ingress -n minio

# 2. Test MinIO access
mc alias set minio https://minio-api.example.com --api S3v4
mc admin info minio

# 3. Test console access
curl -I https://minio-console.example.com

# 4. Verify SSO integration
# Login via console and check Keycloak authentication

# 5. Test S3 operations
mc mb minio/test-bucket
mc cp test-file minio/test-bucket/
mc ls minio/test-bucket/
```

### Resource Requirements
- CPU: 500m request, 2000m limit
- Memory: 512Mi request, 2Gi limit
- Storage: 50Gi (configurable)

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**Files**:
- `playbooks/services/40_setup_minio.yaml` - Main deployment
- `playbooks/services/41r_setup_minio_keycloak_client.yaml` - Keycloak client
- `playbooks/services/42_setup_minio_oidc.yaml` - OIDC configuration

**Key Features (40_setup_minio.yaml)**:
1. Creates namespace and TLS secrets
2. Deploys MinIO using StatefulSet
3. Configures separate ingress for API and console
4. Sets up persistent storage
5. Configures basic authentication

**Key Features (41r_setup_minio_keycloak_client.yaml)**:
1. Creates Keycloak client for MinIO
2. Configures client scope for policy mapping
3. Sets up user attributes for authorization
4. Configures redirect URIs

**Key Features (42_setup_minio_oidc.yaml)**:
1. Installs MinIO client (mc)
2. Configures OIDC identity provider
3. Sets up offline_access for persistent sessions
4. Maps policies from Keycloak claims
5. Restarts MinIO to apply changes

**Special Considerations**:
- Requires multiple playbooks for full setup
- Complex OIDC configuration
- Policy-based authorization via Keycloak claims
- Separate endpoints for API and console
- Persistent storage using StatefulSet
- Password shared with Keycloak admin