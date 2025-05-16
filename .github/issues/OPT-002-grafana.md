# OPT-002: Grafana

## Component Requirements

**Component**: Grafana  
**Type**: Optional  
**Priority**: Medium  
**Dependencies**: Keycloak, Prometheus, MicroK8s  

## Description

Migrate Grafana deployment from thinkube-core to thinkube. Grafana is the visualization and monitoring dashboard used for displaying Prometheus metrics.

## Requirements Analysis

Based on source playbooks analysis:

### Deployment Requirements
1. **Namespace**: `monitoring` (shared with Prometheus)
2. **Deployment Method**: 
   - Kubernetes Deployment with persistent storage
   - ConfigMap for configuration
3. **Storage**:
   - Persistent Volume: 5Gi
   - Storage class: `microk8s-hostpath`
4. **Container Image**:
   - Registry: `registry.cmxela.com/library/grafana:latest`
   - Mirrored from official image

### Keycloak Integration
1. **Client Configuration**:
   - Client ID: `grafana`
   - Protocol: `openid-connect`
   - Public client: false
   - Redirect URIs: `https://{{ grafana_hostname }}/login/generic_oauth`
   - Direct access grants enabled
2. **Realm Roles**:
   - `grafana-admin` - Full administrative access
   - `grafana-editor` - Edit dashboards and data sources
   - `grafana-viewer` - View-only access
3. **Protocol Mappers**:
   - Realm role mapper for role claims
   - Audience mapper for Grafana
   - Client role mapper
4. **Admin User**:
   - Assigned `grafana-admin` role
   - Username from `admin_username` variable

### OAuth2 Configuration
1. **OAuth Settings**:
   - Provider: generic_oauth
   - OIDC scopes: openid, profile, email, roles, offline_access
   - Auto login: disabled
   - Skip organization selection: true
2. **Role Mapping**:
   - Admin role: `grafana-admin`
   - Editor role: `grafana-editor`  
   - Viewer role: `grafana-viewer`
3. **Token Configuration**:
   - Access token lifespan: 3600 seconds
   - Refresh token enabled
4. **Kubernetes Secret**:
   - Name: `grafana-oauth-secret`
   - Contains client ID and secret

### Configuration Components
1. **ConfigMap**: Main Grafana configuration
2. **Admin Secret**: Initial admin credentials
3. **OAuth Secret**: Keycloak client credentials
4. **Prometheus Datasource**:
   - Automatic configuration
   - URL: `http://prometheus.monitoring.svc.cluster.local:9090`
5. **TLS Secret**: Certificate configuration

### Networking
1. **Service**: ClusterIP service
2. **Ingress**:
   - Hostname: `{{ grafana_hostname }}`
   - TLS termination
   - Custom ingress class
3. **Ports**:
   - HTTP: 3000

## Migration Plan

### Phase 1: Infrastructure Setup
1. Ensure namespace exists: `ansible/40_thinkube/optional/grafana/10_namespace.yaml`
2. Configure RBAC: `ansible/40_thinkube/optional/grafana/15_rbac.yaml`

### Phase 2: Keycloak Configuration
1. Create Keycloak client: `ansible/40_thinkube/optional/grafana/20_keycloak_client.yaml`
2. Configure realm roles: `ansible/40_thinkube/optional/grafana/25_keycloak_roles.yaml`
3. Create OAuth secret: `ansible/40_thinkube/optional/grafana/30_oauth_secret.yaml`

### Phase 3: Configuration
1. Create ConfigMap: `ansible/40_thinkube/optional/grafana/35_configmap.yaml`
2. Create admin secret: `ansible/40_thinkube/optional/grafana/40_admin_secret.yaml`
3. Configure datasources: `ansible/40_thinkube/optional/grafana/45_datasources.yaml`

### Phase 4: Deployment
1. Deploy Grafana: `ansible/40_thinkube/optional/grafana/50_deployment.yaml`
2. Create Service: `ansible/40_thinkube/optional/grafana/55_service.yaml`
3. Configure Ingress: `ansible/40_thinkube/optional/grafana/60_ingress.yaml`

### Phase 5: Testing
1. Validate OAuth login: `ansible/40_thinkube/optional/grafana/88_test_grafana.yaml`
2. Test role mappings
3. Verify Prometheus datasource
4. Check dashboard functionality

### Phase 6: Rollback
1. Create rollback playbook: `ansible/40_thinkube/optional/grafana/89_rollback_grafana.yaml`

## Implementation Checklist

- [ ] Create directory structure under `ansible/40_thinkube/optional/grafana/`
- [ ] Configure Keycloak client with protocol mappers
- [ ] Create realm roles for Grafana access
- [ ] Setup OAuth secrets in Kubernetes
- [ ] Create Grafana ConfigMap with OAuth settings
- [ ] Configure admin credentials secret
- [ ] Deploy Grafana with persistent storage
- [ ] Setup Prometheus datasource
- [ ] Create Service and Ingress
- [ ] Configure TLS certificates
- [ ] Create comprehensive test playbook
- [ ] Implement rollback procedures
- [ ] Update documentation

## Notes

- Shares namespace with Prometheus for easier communication
- OAuth integration provides role-based access control
- Direct access grants enabled for API access
- Persistent storage ensures dashboard persistence
- Automatic Prometheus datasource configuration
- Client credentials stored as Kubernetes secret

## Related Files

**Source Playbooks**:
- `services/91r_setup_grafana_keycloak.yaml` - Keycloak client setup
- `services/92_setup_grafana.yaml` - Grafana deployment

**Target Directory**: `ansible/40_thinkube/optional/grafana/`

**Roles Used**:
- `keycloak/keycloak_setup` - Comprehensive Keycloak configuration
- Includes client creation, role mapping, and secret management

---
*Migration tracking for Thinkube platform - Generated by Analysis System*