# Thinkube Deployment Groups

This document outlines the deployment sequence and grouping for Phase 5 (Core Services) based on practical dependencies and operational requirements.

## Phase 5: Core Services Deployment Sequence

### 5.1: Kubernetes Foundation - Control Plane
**Deploy first on control node**
1. **MicroK8s Control Node**
   - Install MicroK8s on control node
   - Enable core addons: dns, storage, helm
   - Configure API server access
   - Initialize cluster networking

### 5.2: Kubernetes Foundation - Workers
**Deploy after control plane is ready**
1. **MicroK8s Worker Nodes**
   - Install MicroK8s on each worker
   - Join workers to control plane
   - Verify node status and connectivity
   - Configure node labels/taints

### 5.3: Core Networking & Security
**Essential infrastructure services**
1. **CoreDNS Configuration**
   - Advanced DNS configuration via Helm
   - Custom domain resolution
   - Service discovery setup
   
2. **Ingress Controllers**
   - Primary NGINX Ingress (namespace: ingress) - for regular services
   - Secondary NGINX Ingress (namespace: ingress-kn) - for Knative services  
   - Both deployed via Helm with separate configurations
   - Different ingress classes: "nginx" and "nginx-kn"
   - Separate external IPs for traffic isolation
   - SSL/TLS termination on both controllers
   - Note: Knative also deploys Kourier, but secondary NGINX is the primary ingress for Knative
   
3. **Cert-Manager**
   - Automated certificate management
   - Let's Encrypt integration
   - Replaces acme.sh
   - Certificate renewal automation
   
4. **GPU Operator**
   - NVIDIA GPU support
   - Device plugin installation
   - Container runtime configuration
   - Deploy early to avoid issues

### 5.4: Secrets Management
**Deploy before services requiring credentials**
1. **HashiCorp Vault**
   - Centralized secrets management
   - Dynamic credentials
   - Encryption as a service
   - Audit logging
   - Dependencies: None (uses Raft storage)

### 5.5: Authentication Foundation
**Required before any service needing SSO**
1. **Keycloak**
   - SSO provider for entire platform
   - Must be deployed before Harbor and other SSO-enabled services
   - Can integrate with Vault for secrets

### 5.6: CI/CD Infrastructure Group
**Core CI/CD services for build, deploy, and artifact management**
1. **Harbor**
   - Container registry with SSO
   - Image proxy/cache to minimize Docker Hub traffic
   - Mirrors public images to avoid rate limits
   - CI/CD artifact storage
   - Deployed with full SSO integration from the start
   
2. **Argo Workflows**
   - CI/CD pipeline orchestration
   - DAG-based workflows
   - Integrates with Harbor for images
   - Required for DevPi deployment
   
3. **ArgoCD**
   - GitOps continuous deployment
   - Application lifecycle management
   - Uses Harbor as image source
   - Required for DevPi deployment

4. **DevPi**
   - Python package index
   - PyPI mirroring to reduce external dependencies
   - Private package hosting
   - Deployed using Argo Workflows and ArgoCD
   - Dependencies: Argo Workflows, ArgoCD, Keycloak

### 5.7: Data Services Group
**Shared data infrastructure for applications**
1. **PostgreSQL**
   - Shared relational database
   - Used by: Keycloak, MLflow, Penpot, AWX
   
2. **MinIO**
   - S3-compatible object storage
   - Used by: Harbor, MLflow, Argo, JupyterHub
   
3. **Qdrant**
   - Vector database for AI/ML workloads
   - Standalone service
   
4. **Valkey**
   - Redis-compatible cache/message broker
   - High-performance key-value store

### 5.8: Development Environment Group
**Deploy after CI/CD and Data Services are ready**
1. **JupyterHub**
   - Multi-user notebook environment
   - Dependencies: PostgreSQL, MinIO, Harbor, Keycloak
   - GPU support for ML workloads
   
2. **Code Server**
   - Web-based VS Code
   - Dependencies: Harbor (for base image), Keycloak
   - Terminal and extension support

### 5.9: Monitoring & Observability
**Deploy after core infrastructure is stable**
1. Prometheus
2. Grafana (with SSO)
3. Loki (optional)

### 5.10: Security & Access Services
**Deploy for secure access and management**
1. **SSL Certificate Management**
   - Let's Encrypt or self-signed certificates
   - Required for all HTTPS services
   
2. **Keycloak for Kubernetes**
   - K8s authentication integration
   - OIDC provider for kubectl access

### 5.11: ML/Data Science Tools
**After development environments are ready**
1. MLflow (needs PostgreSQL, MinIO)
2. Model serving infrastructure

### 5.12: Platform Management Tools
**Administrative and management interfaces**
1. **PgAdmin**
   - PostgreSQL administration
   - Database management UI
   - Essential for database management
   
2. **Thinkube Dashboard** (prioritize development)
   - Custom platform dashboard
   - Tailored to your specific needs
   - No commercial restrictions
   - Can integrate all your services

### 5.13: Application Services
**Deploy as needed based on requirements**
1. **OpenSearch**
   - Search and analytics engine
   - Log aggregation and analysis
   
2. **Penpot**
   - Design and prototyping platform
   - Requires PostgreSQL, Valkey
   
3. **AWX**
   - Ansible automation platform
   - Playbook execution and management
   - Dependencies: PostgreSQL, Keycloak
   
4. **MkDocs**
   - Documentation site generator

### 5.14: Advanced Services (Optional)
1. **Knative**
   - Serverless platform
   - Event-driven architecture
   
2. **Code Server Monitor**
   - Repository monitoring service
   - Git integration

## Key Deployment Principles

1. **Infrastructure First**: Establish solid K8s foundation before services
2. **Authentication Early**: Deploy Keycloak before SSO-dependent services
3. **CI/CD as Foundation**: Harbor + DevPi provide artifact isolation from external registries
4. **Shared Data Services**: Single instances of PostgreSQL/MinIO serving multiple applications
5. **Progressive Enhancement**: Start minimal, add services based on actual needs

## Dependency Chain

```
MicroK8s Control → MicroK8s Workers → Core Addons (dns, storage, helm)
                                           ↓
                        CoreDNS Config → Ingress Controllers → Cert-Manager
                                           ↓
                                    GPU Operator → Vault (optional)
                                           ↓
                                       Keycloak
                                           ↓
                        ┌──────────────────┴──────────────────┐
                        ↓                                    ↓
                 Harbor (CI/CD)                     PostgreSQL (Data)
                        ↓                                    ↓
               Argo Workflows, ArgoCD                    MinIO
                        ↓                                    ↓
                      DevPi                        Qdrant, Valkey
                        ↓                                    ↓
                Mirror Public Images                      ↓
                        ↓                                    ↓
                             Development Environments (JupyterHub, Code Server)
                                           ↓
                                    Monitoring & Other Services
```

This grouping ensures:
- Minimal external dependencies (Harbor/DevPi buffer)
- SSO available when needed
- CI/CD infrastructure ready for application deployment
- Shared data services available for all applications