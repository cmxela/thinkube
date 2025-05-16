---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-002] Deploy MicroK8s Worker Nodes'
labels: requirement, milestone-2, infrastructure
assignees: ''

---

## Component Requirement

### Description
Deploy MicroK8s worker nodes and join them to the control plane cluster. This includes installing MicroK8s, configuring node IP, retrieving join token from control node, and joining the cluster.

### Component Details
- **Component Name**: MicroK8s Worker Nodes
- **Namespace**: kube-system (core Kubernetes)
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/infrastructure/microk8s/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`, `gato-w1` → `k8s-worker-node`) - Already compliant
- [x] Move hardcoded values to inventory variables - Already compliant
- [ ] Replace TLS secrets with Cert-Manager certificates - N/A for this component
- [ ] Update module names to FQCN - Needs attention
- [x] Verify variable compliance - Using inventory variables

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test_workers.yaml)
- [ ] SSO integration working - N/A
- [ ] Resource limits configured - N/A (system service)
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback_workers.yaml)
- [ ] Worker nodes successfully joined to cluster
- [ ] Node communication verified

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node (must be running)

**Required Configurations:**
- VM created and accessible
- Snapd available on system
- User account exists
- Network connectivity to control node
- Control node must be accessible for join token

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [x] IP addresses: Using `worker_node_ip` and `control_node_ip` variables
- [x] Domain names: None present
- [x] Usernames: Using `admin_username` variable
- [ ] No hardcoded paths found

### TLS Certificate Changes
- [ ] Current method: N/A - no certificates in this playbook
- [ ] Cert-Manager resource needed: None
- [ ] Domains required: None

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbook for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook
5. [ ] Update module names to FQCN
6. [ ] Test deployment and cluster joining
7. [ ] Create rollback playbook
8. [ ] Update documentation
9. [ ] Create PR

### Verification Steps
```bash
# 1. Check for hardcoded values
grep -n "gato-p\|gato-w1" ansible/40_thinkube/core/infrastructure/microk8s/*.yaml
grep -n "192\.168\." ansible/40_thinkube/core/infrastructure/microk8s/*.yaml

# 2. Run test playbook
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/microk8s/18_test_workers.yaml

# 3. Verify worker node status
kubectl get nodes
microk8s status

# 4. Test node communication
kubectl run test-pod --image=busybox --rm -it -- ping <worker-ip>
```

### Resource Requirements
- CPU: Minimal (installation only)
- Memory: Minimal (installation only)
- Storage: ~2GB for MicroK8s snap

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Source Playbook Analysis

**File**: `playbooks/core/30_install_microk8s_worker.yaml`

**Key Features**:
1. Installs MicroK8s using snap (classic mode)
2. Configures node IP for kubelet
3. Adds user to microk8s group
4. Retrieves join token from control node using delegation
5. Joins worker to the cluster with --worker flag
6. Verifies successful cluster joining

**Module Naming Issues**:
- Uses `community.general.snap` without FQCN
- Inconsistent module naming (some use `ansible.builtin.*`, others don't)

**Variable Compliance**:
- Already using inventory variables correctly (`worker_node_ip`, `control_node_ip`, `admin_username`)
- No hardcoded values found

**Special Considerations**:
- MicroK8s stop/start during configuration
- User group membership requires logout/login
- Token TTL set to 300 seconds (5 minutes)
- Retries on join operation (3 attempts with 10s delay)
- Delegate_to for cross-node operations
- Regex extraction of join command