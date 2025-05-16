# CORE-012: MkDocs

## Component Requirements

**Component**: MkDocs  
**Type**: Core  
**Priority**: Low  
**Dependencies**: ArgoCD, Argo Workflows, Keycloak, MinIO/Harbor (for container registry)  

## Description

Migrate MkDocs deployment from thinkube-core to thinkube. MkDocs is the documentation system used for generating and serving project documentation.

## Requirements Analysis

Based on source playbook analysis:

### Deployment Requirements
1. **Namespace**: `mkdocs`
2. **Deployment Method**: 
   - Container build via Argo Workflows
   - GitOps deployment via ArgoCD
   - Pre-push Git hooks for automation
3. **Hostname**: `{{ mkdocs_hostname }}`
4. **Storage**:
   - PersistentVolumeClaim: `mkdocs-content-pvc` (1Gi)
   - For documentation content
5. **Authentication**:
   - OAuth2 Proxy with Keycloak OIDC
   - Cookie-based session management

### OAuth2 Proxy Integration
1. **Client Configuration**:
   - Client ID: `mkdocs-dashboard`
   - Cookie domain: `.{{ k8s_domain }}`
   - OIDC issuer: Keycloak realm
   - Redirect URL: OAuth2 callback
2. **Session Management**:
   - Redis for session storage
   - Session store type: `redis`
   - Cookie same-site: `none`
   - Ephemeral Redis deployment
3. **Ingress Settings**:
   - Custom ingress class
   - TLS termination
   - Wildcard certificates

### Container Build System
1. **Argo Workflows**:
   - Kaniko builder for container creation
   - Service account: `kaniko-builder`
   - Docker registry secret configuration
2. **GitHub Integration**:
   - Repository: `thinkube/thinkube-documentation`
   - SSH key configuration for repository access
   - Automated builds on Git changes
   - Pre-push hooks for validation
3. **Image Registry**:
   - Uses Harbor project: `{{ harbor_project }}`
   - Dynamic tagging with timestamp
   - Registry domain configuration

### Git Configuration
1. **Automation Settings**:
   - Git user: "MkDocs Automation"
   - Email: "thinkube@thinkube.com"
   - SSH key management
2. **GitHub Token**:
   - Secret for API access
   - Repository monitoring
   - Webhook configuration
3. **Repository Setup**:
   - Clone to local path
   - Pre-push hook installation
   - Automatic builds on changes

### Environment Requirements
1. **Environment Variables**:
   - `KEYCLOAK_ADMIN_PASSWORD`
   - GitHub token configuration
2. **Files Required**:
   - TLS certificates at specified paths
   - SSH keys for repository access
   - Kubeconfig for cluster access
3. **DNS Configuration**:
   - MkDocs hostname resolution
   - OAuth2 callback URL

## Migration Plan

### Phase 1: Infrastructure Setup
1. Create namespace and RBAC: `ansible/40_thinkube/core/mkdocs/10_namespace.yaml`
2. Configure storage: `ansible/40_thinkube/core/mkdocs/20_storage.yaml`
3. Deploy Redis for sessions: `ansible/40_thinkube/core/mkdocs/30_redis.yaml`

### Phase 2: Authentication Setup
1. Configure Keycloak client: `ansible/40_thinkube/core/mkdocs/40_keycloak_client.yaml`
2. Deploy OAuth2 Proxy: `ansible/40_thinkube/core/mkdocs/50_oauth2_proxy.yaml`

### Phase 3: Application Deployment
1. Configure container build: `ansible/40_thinkube/core/mkdocs/60_build_workflow.yaml`
2. Setup Git repository: `ansible/40_thinkube/core/mkdocs/65_git_setup.yaml`
3. Deploy via ArgoCD: `ansible/40_thinkube/core/mkdocs/70_deploy_mkdocs.yaml`

### Phase 4: Monitoring and Automation
1. Configure repository monitoring: `ansible/40_thinkube/core/mkdocs/80_monitoring.yaml`
2. Setup pre-push hooks: `ansible/40_thinkube/core/mkdocs/85_git_hooks.yaml`

### Phase 5: Testing
1. Validate authentication: `ansible/40_thinkube/core/mkdocs/88_test_mkdocs.yaml`
2. Test documentation build
3. Verify OAuth2 flow
4. Test automatic rebuilds

### Phase 6: Rollback
1. Create rollback playbook: `ansible/40_thinkube/core/mkdocs/89_rollback_mkdocs.yaml`

## Implementation Checklist

- [ ] Create directory structure under `ansible/40_thinkube/core/mkdocs/`
- [ ] Migrate namespace and storage configuration
- [ ] Port Redis deployment for session management
- [ ] Configure Keycloak client and OAuth2 Proxy
- [ ] Setup container build workflow with Kaniko
- [ ] Implement Git repository configuration
- [ ] Deploy application via ArgoCD
- [ ] Configure repository monitoring
- [ ] Setup pre-push hooks for automation
- [ ] Create comprehensive test playbook
- [ ] Implement rollback procedures
- [ ] Update documentation

## Notes

- Repository monitoring is referenced as being handled by code-server monitor playbook
- The playbook follows the same pattern as DevPi deployment
- Redis is essential for OAuth2 session management
- Pre-push hooks enable automatic documentation builds
- Container builds use Argo Workflows for orchestration
- The deployment supports multi-node configurations

## Related Files

**Source Playbook**: `services/150_deploy_mkdocs.yaml`  
**Target Directory**: `ansible/40_thinkube/core/mkdocs/`

**Roles Used**:
- `redis/ephemeral_redis`
- `oauth2_proxy`
- `common/github_ssh_keys`
- `container_deployment/repo`
- `container_deployment/docker_kaniko`
- `container_deployment/git_push`
- `container_deployment/workflow`
- `waiting_for_image`

**Referenced Monitoring**: `111_setup_codeserver_monitor.yaml`

---
*Migration tracking for Thinkube platform - Generated by Analysis System*