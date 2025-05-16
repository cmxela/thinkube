# CORE-010: DevPi

## Component Requirements

**Component**: DevPi  
**Type**: Core  
**Priority**: Medium  
**Dependencies**: ArgoCD, Argo Workflows, Keycloak, MinIO/Harbor (for container registry)  

## Description

Migrate DevPi deployment from thinkube-core to thinkube. DevPi is the private Python package index server used for hosting internal Python packages and caching PyPI packages.

## Requirements Analysis

Based on source playbook analysis:

### Deployment Requirements
1. **Namespace**: `devpi`
2. **Deployment Method**: 
   - Container build via Argo Workflows
   - GitOps deployment via ArgoCD
3. **Ingress Configuration**:
   - Web UI: `{{ devpi_dashboard_hostname }}` (protected with OAuth2)
   - API endpoint: `{{ devpi_api_hostname }}` (no authentication for pip/CLI)
4. **Storage**:
   - PersistentVolumeClaim: `devpi-data-pvc` (5Gi)
   - For package storage
5. **Authentication**:
   - OAuth2 Proxy with Keycloak OIDC for web interface
   - Separate ingress for unauthenticated API access

### OAuth2 Proxy Integration
1. **Client Configuration**:
   - Client ID: `devpi-dashboard`
   - Cookie domain: `.{{ k8s_domain }}`
   - OIDC issuer: Keycloak realm
2. **Session Management**:
   - Redis for session storage
   - Session store type: `redis`
   - Ephemeral Redis deployment included
3. **Ingress Settings**:
   - Same site cookie: `none`
   - Redirect URL configuration
   - TLS with wildcard certificates

### Container Build System
1. **Argo Workflows**:
   - Kaniko builder for container creation
   - Docker registry secret configuration
   - Service account: `kaniko-builder`
2. **GitHub Integration**:
   - Repository: `thinkube/devpi-deployment`
   - SSH key configuration
   - Automated builds on repository changes
3. **Image Registry**:
   - Uses Harbor project: `{{ harbor_project }}`
   - Dynamic tagging with timestamp

### DevPi Configuration
1. **Admin Settings**:
   - Admin user: `admin`
   - Password from environment: `DEVPI_ADMIN_PASSWORD`
   - Default index: `prod`
2. **CLI Integration**:
   - Installation scripts in `/home/{{ admin_username }}/devpi-scripts`
   - Fish shell configuration
   - Helper functions for package management
3. **Repository Monitoring**:
   - Automatic rebuilds on Git changes
   - Monitoring service deployment

### Environment Requirements
1. **Environment Variables**:
   - `KEYCLOAK_ADMIN_PASSWORD`
   - `DEVPI_ADMIN_PASSWORD`
2. **Files Required**:
   - TLS certificates at specified paths
   - GitHub token for API access
   - SSH keys for repository access
3. **DNS Configuration**:
   - Dashboard hostname resolution
   - API hostname resolution

## Migration Plan

### Phase 1: Infrastructure Setup
1. Create namespace and RBAC: `ansible/40_thinkube/core/devpi/10_namespace.yaml`
2. Configure storage: `ansible/40_thinkube/core/devpi/20_storage.yaml`
3. Deploy Redis for sessions: `ansible/40_thinkube/core/devpi/30_redis.yaml`

### Phase 2: Authentication Setup
1. Configure Keycloak client: `ansible/40_thinkube/core/devpi/40_keycloak_client.yaml`
2. Deploy OAuth2 Proxy: `ansible/40_thinkube/core/devpi/50_oauth2_proxy.yaml`

### Phase 3: Application Deployment
1. Configure container build: `ansible/40_thinkube/core/devpi/60_build_workflow.yaml`
2. Deploy via ArgoCD: `ansible/40_thinkube/core/devpi/70_deploy_devpi.yaml`
3. Configure ingress rules: `ansible/40_thinkube/core/devpi/80_ingress.yaml`

### Phase 4: CLI and Integration
1. Install DevPi CLI tools: `ansible/40_thinkube/core/devpi/85_cli_setup.yaml`
2. Configure shell integration: `ansible/40_thinkube/core/devpi/86_shell_config.yaml`

### Phase 5: Testing
1. Validate authentication: `ansible/40_thinkube/core/devpi/88_test_devpi.yaml`
2. Test package upload/download
3. Verify CLI functionality
4. Test OAuth2 flow

### Phase 6: Rollback
1. Create rollback playbook: `ansible/40_thinkube/core/devpi/89_rollback_devpi.yaml`

## Implementation Checklist

- [ ] Create directory structure under `ansible/40_thinkube/core/devpi/`
- [ ] Migrate namespace and storage configuration
- [ ] Port Redis deployment for session management
- [ ] Configure Keycloak client and OAuth2 Proxy
- [ ] Setup container build workflow
- [ ] Implement ArgoCD application deployment
- [ ] Configure dual ingress (authenticated UI, open API)
- [ ] Setup CLI tools and shell integration
- [ ] Create comprehensive test playbook
- [ ] Implement rollback procedures
- [ ] Update documentation

## Notes

- Source playbook follows the same pattern as MkDocs deployment
- Dual ingress configuration is critical for pip functionality
- Redis is required for OAuth2 session management
- Container builds use Argo Workflows and Kaniko
- Fish shell integration provides developer convenience
- Repository monitoring enables automatic rebuilds

## Related Files

**Source Playbook**: `services/120_setup_devpi.yaml`  
**Target Directory**: `ansible/40_thinkube/core/devpi/`

**Roles Used**:
- `redis/ephemeral_redis`
- `oauth2_proxy`
- `common/github_ssh_keys`
- `container_deployment/repo`
- `container_deployment/docker_kaniko`
- `container_deployment/git_push`
- `container_deployment/workflow`
- `waiting_for_image`

---
*Migration tracking for Thinkube platform - Generated by Analysis System*