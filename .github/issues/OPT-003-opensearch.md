# OPT-003: OpenSearch

## Component Requirements

**Component**: OpenSearch  
**Type**: Optional  
**Priority**: Medium  
**Dependencies**: Keycloak, MicroK8s  

## Description

Migrate OpenSearch and OpenSearch Dashboards deployment from thinkube-core to thinkube. OpenSearch is the search and analytics engine used for log aggregation and analysis.

## Requirements Analysis

Based on source playbooks analysis:

### Deployment Requirements
1. **Namespace**: `opensearch`
2. **Components**:
   - OpenSearch cluster (data nodes)
   - OpenSearch Dashboards (UI)
   - Both deployed as StatefulSets
3. **Storage**:
   - Persistent volumes for data nodes
   - StatefulSet for data persistence
4. **Authentication**:
   - Basic auth for internal cluster communication
   - Keycloak OIDC for dashboard access

### Keycloak Integration
1. **Client Configuration**:
   - Client ID: `opensearch`
   - Protocol: `openid-connect`
   - Public client: false
   - PKCE: Explicitly disabled
   - Redirect URIs: Dashboard access paths
2. **Scopes and Mappers**:
   - Custom scope: `opensearch-authorization`
   - Protocol mappers:
     - `preferred_username` - User attribute mapping
     - `roles` - Realm role mapping
   - Scope mappers for authorization
3. **Roles Configuration**:
   - `opensearch-admin`
   - `opensearch-editor`
   - `opensearch-viewer`
   - User assignment to roles

### Security Configuration
1. **TLS/SSL**:
   - Certificate conversion to PEM format
   - TLS secret creation for both services
   - Internal cluster communication encryption
2. **Basic Authentication**:
   - Admin password from environment: `OPENSEARCH_PASSWORD`
   - Password hashing for internal security
   - Security configuration in ConfigMap
3. **OIDC Integration**:
   - Dashboards configured for Keycloak
   - Client secret retrieval from Keycloak
   - Token validation configuration

### Configuration Components
1. **Security ConfigMap**:
   - Internal users configuration
   - Roles and role mappings
   - Authentication backends
   - OIDC settings
2. **Dashboard ConfigMap**:
   - OpenID configuration
   - Server settings
   - OpenSearch connection
3. **Certificates**:
   - Admin certificates for cluster management
   - Node certificates for inter-node communication
   - Transport layer security

### Networking
1. **Services**:
   - OpenSearch service (ClusterIP)
   - Dashboards service (ClusterIP)
2. **Ingress**:
   - OpenSearch: `{{ opensearch_hostname }}`
   - Dashboards: `{{ opensearch_dashboards_hostname }}`
   - TLS termination

## Migration Plan

### Phase 1: Infrastructure Setup
1. Create namespace and RBAC: `ansible/40_thinkube/optional/opensearch/10_namespace.yaml`
2. Generate certificates: `ansible/40_thinkube/optional/opensearch/15_certificates.yaml`

### Phase 2: Keycloak Configuration
1. Create Keycloak client: `ansible/40_thinkube/optional/opensearch/20_keycloak_client.yaml`
2. Configure roles and mappers: `ansible/40_thinkube/optional/opensearch/25_keycloak_roles.yaml`

### Phase 3: Security Setup
1. Create security ConfigMap: `ansible/40_thinkube/optional/opensearch/30_security_config.yaml`
2. Configure internal users: `ansible/40_thinkube/optional/opensearch/35_internal_users.yaml`

### Phase 4: OpenSearch Deployment
1. Deploy StatefulSet: `ansible/40_thinkube/optional/opensearch/40_opensearch_cluster.yaml`
2. Create Service: `ansible/40_thinkube/optional/opensearch/45_opensearch_service.yaml`

### Phase 5: Dashboards Deployment
1. Configure Dashboards: `ansible/40_thinkube/optional/opensearch/50_dashboards_config.yaml`
2. Deploy Dashboards: `ansible/40_thinkube/optional/opensearch/55_dashboards_deployment.yaml`
3. Create Service: `ansible/40_thinkube/optional/opensearch/60_dashboards_service.yaml`

### Phase 6: Ingress Configuration
1. Setup Ingress: `ansible/40_thinkube/optional/opensearch/65_ingress.yaml`

### Phase 7: Testing
1. Validate cluster health: `ansible/40_thinkube/optional/opensearch/88_test_opensearch.yaml`
2. Test OIDC authentication
3. Verify dashboard access
4. Check data persistence

### Phase 8: Rollback
1. Create rollback playbook: `ansible/40_thinkube/optional/opensearch/89_rollback_opensearch.yaml`

## Implementation Checklist

- [ ] Create directory structure under `ansible/40_thinkube/optional/opensearch/`
- [ ] Migrate namespace and RBAC configuration
- [ ] Port certificate generation and management
- [ ] Configure Keycloak client with proper scopes
- [ ] Setup security configuration and internal users
- [ ] Deploy OpenSearch cluster as StatefulSet
- [ ] Configure and deploy OpenSearch Dashboards
- [ ] Setup Services and Ingress
- [ ] Configure TLS for all components
- [ ] Create comprehensive test playbook
- [ ] Implement rollback procedures
- [ ] Update documentation

## Notes

- PKCE is explicitly disabled in Keycloak client
- Certificate conversion to PEM format is required
- Security configuration is critical for cluster setup
- Password must be set in environment variables
- Role mappings provide fine-grained access control
- StatefulSets ensure data persistence

## Related Files

**Source Playbooks**:
- `services/30r_setup_opensearch_keycloak.yaml` - Keycloak client setup
- `services/31_setup_opensearch.yaml` - OpenSearch deployment

**Target Directory**: `ansible/40_thinkube/optional/opensearch/`

**Key Components**:
- Security ConfigMap for authentication
- Dashboard ConfigMap for OIDC
- StatefulSets for data persistence
- Certificate management for TLS

---
*Migration tracking for Thinkube platform - Generated by Analysis System*