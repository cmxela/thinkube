---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-003b] Deploy CoreDNS Configuration'
labels: requirement, milestone-2
assignees: ''

---

## Component Requirement

### Description
Configure CoreDNS in MicroK8s to properly handle ingress hostnames and Knative service resolution, including hairpin routing support for internal access to services.

### Component Details
- **Component Name**: CoreDNS Configuration
- **Namespace**: kube-system (existing)
- **Source**: thinkube-core migration (50_setup_coredns.yaml)
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/infrastructure/coredns/

### Migration Checklist
- [ ] Update host groups (`gato-p` → `k8s-control-node`)
- [ ] Move hardcoded values to inventory variables
- [ ] Update module names to FQCN
- [ ] Verify variable compliance
- [ ] Handle Knative-specific configuration conditionally

### Acceptance Criteria
- [ ] CoreDNS configured for proper DNS resolution
- [ ] Hairpin routing enabled for ingress hostnames
- [ ] Knative domain resolution working (if Knative installed)
- [ ] System certificates configured
- [ ] All tests passing (18_test_coredns.yaml)
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback_coredns.yaml)

### Dependencies
**Required Services:**
- MicroK8s Control Node
- MicroK8s Worker Nodes
- Ingress Controllers

**Required Configurations:**
- Valid domain configuration in inventory
- DNS servers configured

### Hardcoded Values to Migrate
- [ ] Domain names: cmxela.com → {{ domain_name }}
- [ ] DNS server IPs: 10.152.183.10 → {{ k8s_dns_server }}
- [ ] Paths: /var/snap/microk8s → {{ microk8s_path }}
- [ ] Test endpoints: minio-api hostname → {{ test_endpoint }}

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze source playbook for compliance
3. [ ] Create test playbook first (TDD)
4. [ ] Migrate/create deployment playbook
5. [ ] Configure CoreDNS for ingress resolution
6. [ ] Add Knative domain support (conditional)
7. [ ] Configure system certificates
8. [ ] Test deployment
9. [ ] Create rollback playbook
10. [ ] Update documentation
11. [ ] Create PR

### Verification Steps
```bash
# 1. Check for hardcoded values
grep -n "gato-p\|gato-w1" ansible/40_thinkube/core/infrastructure/coredns/*.yaml
grep -n "192\.168\." ansible/40_thinkube/core/infrastructure/coredns/*.yaml

# 2. Verify CoreDNS is configured correctly
kubectl -n kube-system get configmap coredns -o yaml

# 3. Test DNS resolution
kubectl run test-dns --rm -i --restart=Never --image=busybox -- nslookup kubernetes.default.svc.cluster.local

# 4. Run test playbook
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/18_test.yaml
```

### Resource Requirements
- CPU: None (configuration only)
- Memory: None (configuration only)
- Storage: None (configuration only)

### Edit History
- 2025-05-17: Initial creation to fix gap in infrastructure sequence