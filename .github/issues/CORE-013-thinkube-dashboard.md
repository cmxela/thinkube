# CORE-013: Thinkube Dashboard

## Component Requirements

**Component**: Thinkube Dashboard  
**Type**: Core  
**Priority**: High  
**Dependencies**: ArgoCD, Argo Workflows, Keycloak, MinIO/Harbor (for container registry)  

## Description

Migrate Thinkube Dashboard deployment from thinkube-core to thinkube. The Thinkube Dashboard is the central hub interface for accessing all services in the Thinkube platform.

## Requirements Analysis

Based on source playbook analysis:

### Deployment Requirements
1. **Namespace**: `dashboard-hub`
2. **Deployment Method**: 
   - Container build via Argo Workflows
   - GitOps deployment via ArgoCD
   - Separate frontend and backend components
3. **Hostname**: `{{ dashboard_hub_hostname }}`
4. **Authentication**:
   - OAuth2 Proxy with Keycloak OIDC
   - Client ID: `dashboard-hub`
   - User access control

### Architecture Components
1. **Frontend Application**:
   - Image: `dashboard-frontend`
   - React-based UI
   - OAuth2 authentication flow
2. **Backend Application**:
   - Image: `dashboard-backend`
   - API server
   - Service integration
3. **Session Management**:
   - Redis for session storage
   - OAuth2 Proxy for authentication
   - Cookie-based sessions

### OAuth2 Proxy Integration
1. **Client Configuration**:
   - Client ID: `dashboard-hub`
   - Cookie domain: `.{{ k8s_domain }}`
   - OIDC issuer: Keycloak realm
   - Redirect URL: OAuth2 callback
2. **Session Configuration**:
   - Session store type: `redis`
   - Ephemeral Redis deployment
   - Cookie same-site: `none`
3. **Ingress Settings**:
   - TLS termination
   - Custom ingress class
   - Wildcard certificates

### Container Build System
1. **Argo Workflows**:
   - Kaniko builder configuration
   - Service account: `kaniko-builder`
   - Separate builds for frontend/backend
2. **GitHub Integration**:
   - Repository: `thinkube/dashboard-hub`
   - SSH key configuration
   - Automated builds on changes
3. **Image Registry**:
   - Harbor project: `{{ harbor_project }}`
   - Dynamic tagging with timestamp
   - Multiple image repositories

### Keycloak Integration
1. **Client Configuration**:
   - Root URL: Dashboard hostname
   - Base URL: Dashboard hostname
   - Redirect URIs: Wildcard pattern
   - Web origins: Dashboard domain
   - Standard flow enabled
   - Direct access grants disabled
2. **User Access**:
   - Admin user granted access
   - Role-based permissions
   - Group-based authorization

### Environment Requirements
1. **Environment Variables**:
   - `KEYCLOAK_ADMIN_PASSWORD`
   - GitHub token configuration
2. **Files Required**:
   - TLS certificates at specified paths
   - SSH keys for repository access
   - Kubeconfig for cluster access
3. **DNS Configuration**:
   - Dashboard hostname resolution
   - OAuth2 callback URL

## Migration Plan

### Phase 1: Infrastructure Setup
1. Create namespace and RBAC: `ansible/40_thinkube/core/thinkube-dashboard/10_namespace.yaml`
2. Deploy Redis for sessions: `ansible/40_thinkube/core/thinkube-dashboard/20_redis.yaml`

### Phase 2: Authentication Setup
1. Configure Keycloak client: `ansible/40_thinkube/core/thinkube-dashboard/30_keycloak_client.yaml`
2. Deploy OAuth2 Proxy: `ansible/40_thinkube/core/thinkube-dashboard/40_oauth2_proxy.yaml`

### Phase 3: Application Build
1. Configure container builds: `ansible/40_thinkube/core/thinkube-dashboard/50_build_workflows.yaml`
2. Setup Git repository: `ansible/40_thinkube/core/thinkube-dashboard/55_git_setup.yaml`

### Phase 4: Application Deployment
1. Deploy backend via ArgoCD: `ansible/40_thinkube/core/thinkube-dashboard/60_deploy_backend.yaml`
2. Deploy frontend via ArgoCD: `ansible/40_thinkube/core/thinkube-dashboard/65_deploy_frontend.yaml`
3. Configure ingress rules: `ansible/40_thinkube/core/thinkube-dashboard/70_ingress.yaml`

### Phase 5: Post-Deployment
1. Configure service integrations: `ansible/40_thinkube/core/thinkube-dashboard/80_service_config.yaml`
2. Setup monitoring: `ansible/40_thinkube/core/thinkube-dashboard/85_monitoring.yaml`

### Phase 6: Testing
1. Validate authentication: `ansible/40_thinkube/core/thinkube-dashboard/88_test_dashboard.yaml`
2. Test service integrations
3. Verify OAuth2 flow
4. Check frontend/backend communication

### Phase 7: Rollback
1. Create rollback playbook: `ansible/40_thinkube/core/thinkube-dashboard/89_rollback_dashboard.yaml`

## Implementation Checklist

- [ ] Create directory structure under `ansible/40_thinkube/core/thinkube-dashboard/`
- [ ] Migrate namespace and RBAC configuration
- [ ] Port Redis deployment for session management
- [ ] Configure Keycloak client with proper settings
- [ ] Deploy OAuth2 Proxy with Redis backend
- [ ] Setup container build workflows for frontend/backend
- [ ] Implement Git repository configuration
- [ ] Deploy applications via ArgoCD
- [ ] Configure ingress with TLS
- [ ] Setup service integrations
- [ ] Create comprehensive test playbook
- [ ] Implement rollback procedures
- [ ] Update documentation

## Notes

- The playbook follows the same pattern as MkDocs deployment
- Frontend and backend are built and deployed separately
- Redis is required for OAuth2 session management
- Keycloak client configuration is handled by the role
- Service integration configuration is critical for functionality
- Multi-node support is included

## Related Files

**Source Playbook**: `services/160_setup_thinkube_dashboard.yaml`  
**Target Directory**: `ansible/40_thinkube/core/thinkube-dashboard/`

**Roles Used**:
- `common/github_ssh_keys`
- `container_deployment/repo`
- `container_deployment/docker_kaniko`
- `container_deployment/git_push`
- `keycloak/keycloak_client`
- `redis/ephemeral_redis`
- `oauth2_proxy`
- `container_deployment/workflow`
- `waiting_for_image`
- `container_deployment/deployment`
- `container_deployment/argocd`

---
*Migration tracking for Thinkube platform - Generated by Analysis System*