---
name: Component Requirement
about: Define a requirement for deploying a Thinkube component
title: '[CORE-003] Deploy Cert-Manager'
labels: requirement, milestone-2, infrastructure
assignees: ''

---

## Component Requirement

### Description
Deploy cert-manager to replace manual SSL certificate management using acme.sh. This will provide automatic certificate issuance and renewal for all platform services using Let's Encrypt via Cloudflare DNS validation.

### Component Details
- **Component Name**: Cert-Manager
- **Namespace**: cert-manager
- **Source**: New deployment (replacing thinkube-core manual approach)
- **Priority**: high
- **Directory**: ansible/40_thinkube/core/infrastructure/cert-manager/

### Migration Checklist
- [ ] Update host groups - N/A (new deployment)
- [ ] Move hardcoded values to inventory variables
- [ ] Replace TLS secrets with Cert-Manager certificates - This IS the replacement
- [ ] Update module names to FQCN
- [ ] Verify variable compliance

### Acceptance Criteria
- [ ] Component deployed successfully
- [ ] All tests passing (18_test.yaml)
- [ ] SSO integration working - N/A
- [ ] Resource limits configured
- [ ] Documentation updated
- [ ] Rollback playbook created (19_rollback.yaml)
- [ ] Successfully issues wildcard certificates
- [ ] Automatic renewal working
- [ ] Ingress controller integration verified

### Dependencies
**Required Services:**
- CORE-001: MicroK8s Control Node
- CORE-002: MicroK8s Worker Nodes
- Ingress controller must be deployed

**Required Configurations:**
- Cloudflare API token for DNS validation
- MicroK8s cluster running
- DNS zones configured in Cloudflare

### Hardcoded Values to Migrate
<!-- From existing SSL certificate playbook -->
- [ ] Certificate domains list (should come from inventory)
- [ ] ACME server URL
- [ ] Certificate key type (EC-256)
- [ ] Renewal age threshold (30 days)
- [ ] Cloudflare API token reference

### TLS Certificate Changes
- [ ] Current method: acme.sh with manual management
- [ ] Cert-Manager resources needed:
  - ClusterIssuer for Let's Encrypt
  - Certificate resources for each domain
  - DNS01 solver configuration
- [ ] Domains required:
  - `{{ domain_name }}`
  - `*.{{ domain_name }}`
  - `*.{{ k8s_domain }}`
  - `*.kn.{{ domain_name }}`

### Implementation Tasks
1. [ ] Create component directory structure
2. [ ] Analyze existing SSL playbook for migration requirements
3. [ ] Create test playbook first (TDD)
4. [ ] Create deployment playbook:
   - [ ] Deploy cert-manager using official manifests
   - [ ] Create ClusterIssuer for Let's Encrypt
   - [ ] Configure Cloudflare DNS solver
   - [ ] Create Certificate resources
5. [ ] Test certificate issuance
6. [ ] Verify automatic renewal
7. [ ] Create rollback playbook
8. [ ] Update documentation
9. [ ] Create PR

### Verification Steps
```bash
# 1. Check cert-manager deployment
kubectl get pods -n cert-manager
kubectl get clusterissuer

# 2. Check certificate status
kubectl get certificates -A
kubectl describe certificate <cert-name> -n <namespace>

# 3. Test certificate issuance
kubectl get certificaterequest -A
kubectl get challenges -A

# 4. Verify ingress integration
kubectl get ingress -A -o yaml | grep tls
```

### Resource Requirements
- CPU: 100m request, 500m limit
- Memory: 128Mi request, 512Mi limit
- Storage: None

### Edit History
<!-- Track significant changes to this issue -->
- 2025-05-16: Initial creation

### Migration Notes

**From**: `playbooks/core/70_create_ssl_certificates.yaml`

**Current Implementation**:
1. Uses acme.sh for certificate management
2. Cloudflare DNS validation via API token
3. Manual installation and renewal scripts
4. Issues wildcard certificates for multiple domains
5. Reloads ingress on certificate updates
6. Manual file permissions management

**Cert-Manager Implementation**:
1. Deploy cert-manager CRDs and components
2. Create ClusterIssuer with Cloudflare DNS01 solver
3. Create Certificate resources for automatic management
4. Let cert-manager handle renewals automatically
5. Integrate with ingress-nginx for automatic updates
6. Use cert-manager's secret management

**Key Differences**:
- No manual certificate files on filesystem
- Automatic renewal without cron jobs
- Native Kubernetes integration
- Better observability through CRDs
- Simplified configuration through resources

**Special Considerations**:
- Cloudflare API token must be stored as Kubernetes secret
- Certificate domains should be configurable via inventory
- Consider staging environment for testing
- Plan migration path for existing certificates