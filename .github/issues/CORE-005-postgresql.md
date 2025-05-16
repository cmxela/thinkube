---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-005] Deploy PostgreSQL'
labels: requirement, milestone-2, core
assignees: ''

---

## Component Requirement

### Description
Deploy PostgreSQL database server to provide persistent storage for platform services including Keycloak, Harbor, MLflow, and others. Uses official PostgreSQL container image with StatefulSet for data persistence.

### Component Details
- **Component Name**: PostgreSQL
- **Namespace**: postgres
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/postgresql/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates
- [ ] Update module names to FQCN - Compliant
- [ ] Verify variable compliance - Needs work

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working - N/A
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] Database accessible from services
- [ ] Data persistence verified
- [ ] Backup strategy documented

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes
- Storage class available (microk8s-hostpath)

**Required Configurations:**
- Persistent storage available
- Network policies configured (if enabled)

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [ ] Namespace: "postgres"
- [ ] Image: "registry.cmxela.com/library/postgres:14.5-alpine"
- [ ] Storage class: "microk8s-hostpath"
- [ ] PVC size: "10Gi"
- [ ] User credentials: "admin/strongpassword123"
- [ ] Database name: "mydatabase"
- [ ] Service name pattern
- [ ] Volume mount paths
- [ ] Security context UID: 999

### TLS Certificate Changes
- [ ] Current method: Manual TLS configuration
- [ ] Cert-Manager resource needed: Certificate for postgres hostname
- [ ] Domains required: `{{ postgres_hostname }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbook for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook
5. [ ] Move credentials to Kubernetes secrets
6. [ ] Add resource limits
7. [ ] Configure backup solution
8. [ ] Test data persistence
9. [ ] Create rollback playbook
10. [ ] Update documentation
11. [ ] Create PR

### Verification Steps
```bash
# 1. Check PostgreSQL deployment
kubectl get statefulset -n postgres
kubectl get pvc -n postgres
kubectl get pods -n postgres

# 2. Test database connection
kubectl exec -it postgresql-official-0 -n postgres -- psql -U admin -d mydatabase -c "SELECT version();"

# 3. Verify data persistence
kubectl exec -it postgresql-official-0 -n postgres -- psql -U admin -d mydatabase -c "CREATE TABLE test(id int);"
kubectl delete pod postgresql-official-0 -n postgres
# Wait for pod to restart
kubectl exec -it postgresql-official-0 -n postgres -- psql -U admin -d mydatabase -c "\dt"

# 4. Check service availability
kubectl get svc -n postgres
```

### Resource Requirements
- CPU: 250m request, 1000m limit
- Memory: 256Mi request, 1Gi limit
- Storage: 10Gi (configurable)

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**File**: `playbooks/services/50_setup_postgress.yaml`

**Key Features**:
1. Creates namespace and TLS secret
2. Deploys PostgreSQL using StatefulSet
3. Uses official postgres:14.5-alpine image
4. Creates PersistentVolumeClaim for data
5. Configures basic authentication
6. Sets up service for database access
7. Includes TCP passthrough configuration for external access

**Module Naming**:
- Uses kubernetes.core.k8s correctly (FQCN)
- ansible.builtin modules properly namespaced

**Variable Compliance Issues**:
- Hardcoded namespace
- Hardcoded credentials (should be in secrets)
- Hardcoded storage configuration
- Image registry hardcoded to specific domain

**Special Considerations**:
- StatefulSet for data persistence
- Security context with PostgreSQL UID
- External access via TCP passthrough
- No resource limits configured
- Plain text passwords in deployment
- Single replica (no HA)
- No backup configuration
- Missing monitoring setup