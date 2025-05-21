---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-003d] Deploy NVIDIA GPU Operator'
labels: requirement, milestone-2
assignees: ''
---

## Component Requirement

### Description
Deploy the NVIDIA GPU Operator to enable GPU support in the Kubernetes cluster, allowing GPU hardware to be discovered, managed, and utilized by containerized workloads. The GPU Operator automates driver installation, GPU device plugin, container runtime, and more.

**IMPORTANT**: This is a minimal migration requirement. The reference playbook is already well-structured with few dependencies. NVIDIA drivers are already installed and tested on the host systems. The main changes needed are:
1. Updating host group from `k8s-control-node` to `microk8s_control_plane` 
2. Ensuring variable compliance
3. Creating proper test/rollback playbooks

### Component Details
- **Component Name**: GPU Operator
- **Namespace**: gpu-operator
- **Source**: thinkube-core migration (60_install_gpu_operator.yaml)
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/infrastructure/gpu_operator/

### Migration Checklist
- [ ] Update host groups (`k8s-control-node` → `microk8s_control_plane`)
- [ ] Move hardcoded values to inventory variables (minimal changes needed)
- [ ] Update module names to FQCN (already compliant)
- [ ] Verify variable compliance
- [ ] Create proper test and rollback playbooks

### Acceptance Criteria
- [ ] GPU Operator deployed successfully
- [ ] All GPU-operator components running (device plugin, driver, toolkit)
- [ ] CUDA test job executes successfully
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)

### Dependencies
**Required Services:**
- MicroK8s cluster with GPU-equipped nodes
- NVIDIA drivers already installed on host systems (pre-verified)

**Required Configurations:**
- Proper containerd configuration for GPU support (already in place)
- Helm must be available (already configured)

### Hardcoded Values to Migrate
- [ ] IP addresses: None found
- [ ] Domain names: None found
- [ ] Usernames: None found
- [ ] Paths: `/tmp/cuda-vectoradd.yaml` - Consider using Ansible temp directory

### TLS Certificate Changes
- [ ] Current method: N/A (no certificate needed)
- [ ] Cert-Manager resource needed: None
- [ ] Domains required: None

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Create test playbook first (18_test.yaml)
3. [ ] Migrate deployment playbook (10_deploy.yaml) with minimal changes
4. [ ] Test deployment
5. [ ] Create rollback playbook (19_rollback.yaml)
6. [ ] Update documentation
7. [ ] Create PR

### Verification Steps
```bash
# 1. Check GPU resource availability
microk8s kubectl get nodes -o json | jq '.items[].status.capacity["nvidia.com/gpu"]'

# 2. Run test playbook
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/gpu_operator/18_test.yaml

# 3. Verify components are running
microk8s kubectl get pods -n gpu-operator
```

### Resource Requirements
- CPU: 500m per component
- Memory: 300Mi per component
- Storage: None (stateless)

### Edit History
- 2025-05-21: Initial creation