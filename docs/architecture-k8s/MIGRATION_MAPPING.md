# Thinkube-Core Migration Mapping

This document maps each component to the playbooks that need to be migrated from thinkube-core.

## Infrastructure Components

### CORE-001: MicroK8s Control Node
**Source Playbooks**:
- `20_install_microk8s_planner.yaml` - Main MicroK8s installation on control plane

### CORE-002: MicroK8s Worker Nodes  
**Source Playbooks**:
- `30_install_microk8s_worker.yaml` - Worker node joining
- `00_main_cluster_setup.yaml` - Main cluster setup (partial - worker aspects)

### CORE-003: Cert-Manager
**Source Playbooks**:
- `70_create_ssl_certificates.yaml` - SSL certificate creation (to be replaced with cert-manager)
- Note: This playbook uses manual cert generation - will be replaced with cert-manager deployment

## Core Platform Services

### CORE-004: Keycloak
**Source Playbooks**:
- `80_setup_keycloak.yaml` - Keycloak deployment and configuration
- `90_setup_keycloak4kubernetes.yaml` - Keycloak Kubernetes integration

### CORE-005: PostgreSQL
**Source Playbooks**:
- `50_setup_postgress.yaml` - PostgreSQL deployment

### CORE-006: MinIO
**Source Playbooks**:
- `40_setup_minio.yaml` - MinIO deployment
- `41r_setup_minio_keycloak_client.yaml` - MinIO Keycloak client setup
- `42_setup_minio_oidc.yaml` - MinIO OIDC configuration

### CORE-007: Harbor
**Source Playbooks**:
- `100_setup_harbor.yaml` - Harbor deployment
- `101_setup_harbor_thinkube.yaml` - Harbor Thinkube project configuration
- `102_setup_harbor_default_registry.yaml` - Default registry configuration
- `103_mirror_public_images.yaml` - Public image mirroring

### CORE-008: Argo Workflows
**Source Playbooks**:
- `70r_setup_argo_keycloak.yaml` - Argo Keycloak integration
- `71_setup_argo.yaml` - Argo Workflows and Argo Events deployment
- `72_setup_argo_token.yaml` - Argo token configuration
- `73_setup_argo_artifacts.yaml` - Argo artifact storage configuration

### CORE-009: ArgoCD
**Source Playbooks**:
- `80r_setup_argocd_keycloak.yaml` - ArgoCD Keycloak integration
- `81_setup_argocd.yaml` - ArgoCD deployment
- `82_get_argocd_credentials.yaml` - Credential retrieval
- `83_setup_argocd_serviceaccount.yaml` - Service account configuration

### CORE-010: DevPi
**Source Playbooks**:
- `120_setup_devpi.yaml` - DevPi deployment

### CORE-011: AWX
**Source Playbooks**:
- `20_deploy_awx.yaml` - AWX deployment and configuration

### CORE-012: MkDocs
**Source Playbooks**:
- `150_deploy_mkdocs.yaml` - MkDocs deployment

### CORE-013: Thinkube Dashboard
**Source Playbooks**:
- `160_setup_thinkube_dashboard.yaml` - Thinkube Dashboard deployment

## Core Infrastructure Components

### Ingress Controllers
**Source Playbooks**:
- `40_setup_ingress.yaml` - Primary and secondary ingress setup

### CoreDNS Configuration
**Source Playbooks**:
- `50_setup_coredns.yaml` - CoreDNS configuration

### GPU Operator
**Source Playbooks**:
- `60_install_gpu_operator.yaml` - GPU operator installation

## Optional Components

### OPT-001: Prometheus
**Source Playbooks**:
- `90_setup_prometheus.yaml` - Prometheus deployment

### OPT-002: Grafana
**Source Playbooks**:
- `91r_setup_grafana_keycloak.yaml` - Grafana Keycloak integration
- `92_setup_grafana.yaml` - Grafana deployment

### OPT-003: OpenSearch
**Source Playbooks**:
- `30r_setup_opensearch_keycloak.yaml` - OpenSearch Keycloak integration
- `31_setup_opensearch.yaml` - OpenSearch deployment

### OPT-004: JupyterHub
**Source Playbooks**:
- `100_jupyterhub_image_build.yaml` - JupyterHub image building
- `101_setup_jupyterhub.yaml` - JupyterHub deployment
- `104_build_jupyter_images.yaml` - Additional Jupyter image builds

### OPT-005: Code Server
**Source Playbooks**:
- `110_setup_codeserver.yaml` - Code Server deployment
- `111_setup_codeserver_monitor.yaml` - Code Server monitoring

### OPT-006: MLflow
**Source Playbooks**:
- `170_mlflow_image_build.yaml` - MLflow image building
- `171_setup_mlflow.yaml` - MLflow deployment

### OPT-007: Knative
**Source Playbooks**:
- `110_setup_knative.yaml` - Knative deployment

### OPT-008: Qdrant
**Source Playbooks**:
- `10r_setup_qdrant.yaml` - Qdrant deployment

### OPT-009: PgAdmin
**Source Playbooks**:
- `60_setup_pgadmin.yaml` - PgAdmin deployment
- `61r_setup_pgadmin_keycloak.yaml` - PgAdmin Keycloak integration
- `62_setup_pgadmin_oidc.yaml` - PgAdmin OIDC configuration

### OPT-010: Penpot
**Source Playbooks**:
- `180_setup_penpot_keycloak.yaml` - Penpot Keycloak integration
- `181_setup_penpot.yaml` - Penpot deployment

### OPT-011: Valkey
**Source Playbooks**:
- `189_valkey_image_build.yaml` - Valkey image building
- `190_setup_valkey.yaml` - Valkey deployment

## Additional Playbooks to Review

### Master Service Setup
- `00_setup_services.yaml` - Master service deployment orchestration

### Other Components (Not in current list)
- `130r_deploy_helm_dashboard.yaml` - Helm Dashboard
- `140r_setup_portainer.yaml` - Portainer

## Notes

1. Playbooks marked with 'r' in the name typically handle Keycloak/SSO integration
2. Some components have multiple playbooks for different aspects (deployment, SSO, configuration)
3. Image building playbooks should be reviewed for Harbor integration
4. The numbering indicates deployment order dependencies