---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-001] Deploy MicroK8s Control Node'
labels: requirement, milestone-2, infrastructure
assignees: ''

---

## Component Requirement

### Description
Deploy MicroK8s control plane node with proper configuration for the Thinkube platform. This includes installing MicroK8s, configuring the node IP, enabling required addons, setting up kubectl/helm access, and integrating with the thinkube common alias system.

### Component Details
- **Component Name**: MicroK8s Control Node
- **Namespace**: kube-system (core Kubernetes)
- **Source**: thinkube-core migration
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/infrastructure/microk8s/

### Migration Checklist
- [x] Update host groups (`gato-p` → `k8s-control-node`) - Already compliant
- [x] Move hardcoded values to inventory variables - Already compliant
- [ ] Replace TLS secrets with Cert-Manager certificates - N/A for this component
- [ ] Update module names to FQCN - Mixed compliance
- [x] Verify variable compliance - Using inventory variables
- [ ] Integrate with thinkube alias system for kubectl/helm

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test_control.yaml)
- [ ] SSO integration working - N/A
- [ ] Resource limits configured - N/A (system service)
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback_control.yaml)
- [ ] kubectl and helm aliases configured via common alias system
- [ ] Aliases work in bash, zsh, and fish shells

### Dependencies
**Required Services:**
- None (first component to deploy)

**Required Configurations:**
- VM created and accessible
- Snapd available on system
- User account exists
- Thinkube shell configuration (for alias system integration)

### Hardcoded Values to Migrate
<!-- List found during analysis -->
- [x] IP addresses: Using `control_node_ip` variable
- [x] Domain names: None present
- [x] Usernames: Using `admin_username` variable
- [x] Paths: Using variables like `kubectl_bin`, `helm_bin`

### TLS Certificate Changes
- [ ] Current method: N/A - no certificates in this playbook
- [ ] Cert-Manager resource needed: None
- [ ] Domains required: None

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbook for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate deployment playbook
5. [ ] Add kubectl/helm alias configuration using thinkube alias system
6. [ ] Test deployment and alias functionality
7. [ ] Create rollback playbook
8. [ ] Update documentation
9. [ ] Create PR

### Verification Steps
```bash
# 1. Check for hardcoded values
grep -n "gato-p\|gato-w1" ansible/40_thinkube/core/infrastructure/microk8s/*.yaml
grep -n "192\.168\." ansible/40_thinkube/core/infrastructure/microk8s/*.yaml

# 2. Run test playbook
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/microk8s/18_test.yaml

# 3. Verify MicroK8s status
microk8s status
kubectl get nodes

# 4. Test kubectl aliases in different shells
bash -c 'source ~/.bashrc; k get nodes'
zsh -c 'source ~/.zshrc; k get nodes'
fish -c 'k get nodes'
```

### Resource Requirements
- CPU: Minimal (installation only)
- Memory: Minimal (installation only)
- Storage: ~2GB for MicroK8s snap

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation
- 2025-05-16: Added kubectl/helm alias configuration requirement

### Source Playbook Analysis

**File**: `playbooks/core/20_install_microk8s_planner.yaml`

**Key Features**:
1. Installs MicroK8s using snap (classic mode)
2. Configures node IP for kubelet
3. Adds user to microk8s group
4. Enables addons (dns, storage, helm3, dashboard)
5. Creates kubectl/helm wrapper scripts
6. Configures shell aliases for multiple shells (currently custom implementation)
7. Comprehensive verification steps

**Module Naming Issues**:
- Uses `community.general.snap` instead of FQCN
- Mixed module naming (some use `ansible.builtin.*`, others don't)

**Variable Compliance**:
- Already using inventory variables correctly
- No hardcoded values found
- Uses `ansible_env.HOME` for dynamic paths

**Special Considerations**:
- MicroK8s stop/start during configuration
- User group membership requires logout/login
- Multiple shell support (bash, fish)
- Wrapper scripts in ~/.local/bin

### Additional Requirements for Thinkube Integration

**kubectl/helm Alias Configuration**:
- Integrate with the common alias system at `~/.thinkube_shared_shell/aliases/`
- Add kubectl aliases to the JSON format used by the alias system:
  - `k` → `kubectl`
  - `kns` → `kubectl config set-context --current --namespace`
  - `kctx` → `kubectl config use-context`
  - `kgp` → `kubectl get pods`
  - `kgs` → `kubectl get services`
  - `kgd` → `kubectl get deployments`
  - `kga` → `kubectl get all`
  - `kaf` → `kubectl apply -f`
  - `kdf` → `kubectl delete -f`
  - `kl` → `kubectl logs`
  - `ke` → `kubectl exec -it`
  - `kdesc` → `kubectl describe`
- Add helm aliases:
  - `h` → `helm`
  - `hl` → `helm list`
  - `hi` → `helm install`
  - `hu` → `helm upgrade`
  - `hd` → `helm delete`
  - `hs` → `helm search`
- Ensure aliases are regenerated and loaded for all shells
- Remove custom shell configuration in favor of the common system
- Use the existing wrapper scripts for kubectl and helm binaries