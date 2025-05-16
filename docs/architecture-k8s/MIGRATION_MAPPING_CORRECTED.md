# Thinkube-Core Migration Mapping (Corrected)

This document maps each component to the ACTUAL playbooks that exist in thinkube-core.

## Infrastructure Components

### CORE-001: MicroK8s Control Node
**Source Playbooks**:
- `core/20_install_microk8s_planner.yaml` - Main MicroK8s installation on control plane

### CORE-002: MicroK8s Worker Nodes  
**Source Playbooks**:
- `core/30_install_microk8s_worker.yaml` - Worker node joining

### CORE-003: Cert-Manager
**Source Playbooks**:
- `core/70_create_ssl_certificates.yaml` - SSL certificate creation (to be replaced with cert-manager)
- Note: This playbook uses manual cert generation - will be replaced with cert-manager deployment

## Core Platform Services

### CORE-004: Keycloak
**Source Playbooks**:
- `core/80_setup_keycloak.yaml` - Keycloak deployment and configuration
- `core/90_setup_keycloak4kubernetes.yaml` - Keycloak Kubernetes integration

### CORE-005: PostgreSQL
**Source Playbooks**:
- `services/50_setup_postgress.yaml` - PostgreSQL deployment

### CORE-006: MinIO
**Source Playbooks**:
- `services/40_setup_minio.yaml` - MinIO deployment
- `services/41r_setup_minio_keycloak_client.yaml` - MinIO Keycloak client setup
- `services/42_setup_minio_oidc.yaml` - MinIO OIDC configuration

### CORE-007: Harbor
**Source Playbooks**:
- `core/100_setup_harbor.yaml` - Harbor deployment
- `core/101_setup_harbor_thinkube.yaml` - Harbor Thinkube project configuration
- `core/102_setup_harbor_default_registry.yaml` - Default registry configuration
- `core/103_mirror_public_images.yaml` - Public image mirroring

### CORE-008: Argo Workflows
**Source Playbooks**:
- `services/70r_setup_argo_keycloak.yaml` - Argo Keycloak integration
- `services/71_setup_argo.yaml` - Argo Workflows and Argo Events deployment
- `services/72_setup_argo_token.yaml` - Argo token configuration
- `services/73_setup_argo_artifacts.yaml` - Argo artifact storage configuration

### CORE-009: ArgoCD
**Source Playbooks**:
- `services/80r_setup_argocd_keycloak.yaml` - ArgoCD Keycloak integration
- `services/81_setup_argocd.yaml` - ArgoCD deployment
- `services/82_get_argocd_credentials.yaml` - Credential retrieval
- `services/83_setup_argocd_serviceaccount.yaml` - Service account configuration

### CORE-010: DevPi
**Source Playbooks**:
- `services/120_setup_devpi.yaml` - DevPi deployment

### CORE-011: AWX
**Source Playbooks**:
- `services/20_deploy_awx.yaml` - AWX deployment and configuration
- Note: Core orchestration incorrectly references as `110_deploy_awx.yaml`

### CORE-012: MkDocs
**Source Playbooks**:
- `services/150_deploy_mkdocs.yaml` - MkDocs deployment

### CORE-013: Thinkube Dashboard
**Source Playbooks**:
- `services/160_setup_thinkube_dashboard.yaml` - Thinkube Dashboard deployment

## Core Infrastructure Components

### Ingress Controllers
**Source Playbooks**:
- `core/40_setup_ingress.yaml` - Primary and secondary ingress setup

### CoreDNS Configuration
**Source Playbooks**:
- `core/50_setup_coredns.yaml` - CoreDNS configuration

### GPU Operator
**Source Playbooks**:
- `core/60_install_gpu_operator.yaml` - GPU operator installation

## Optional Components

### OPT-001: Prometheus
**Source Playbooks**:
- `services/90_setup_prometheus.yaml` - Prometheus deployment

### OPT-002: Grafana
**Source Playbooks**:
- `services/91r_setup_grafana_keycloak.yaml` - Grafana Keycloak integration
- `services/92_setup_grafana.yaml` - Grafana deployment

### OPT-003: OpenSearch
**Source Playbooks**:
- `services/30r_setup_opensearch_keycloak.yaml` - OpenSearch Keycloak integration
- `services/31_setup_opensearch.yaml` - OpenSearch deployment

### OPT-004: JupyterHub
**Source Playbooks**:
- `services/100_jupyterhub_image_build.yaml` - JupyterHub image building
- `services/101_setup_jupyterhub.yaml` - JupyterHub deployment
- NOTE: `core/104_build_jupyter_images.yaml` is NOT used (per your instructions)

### OPT-005: Code Server
**Source Playbooks**:
- `services/110_setup_codeserver.yaml` - Code Server deployment
- `services/111_setup_codeserver_monitor.yaml` - Code Server monitoring

### OPT-006: MLflow
**Source Playbooks**:
- `services/170_mlflow_image_build.yaml` - MLflow image building
- `services/171_setup_mlflow.yaml` - MLflow deployment

### OPT-007: Knative
**Source Playbooks**:
- `core/110_setup_knative.yaml` - Knative deployment
- Note: Services orchestration incorrectly references as `20_setup_knative.yaml`

### OPT-008: Qdrant
**Source Playbooks**:
- `services/10r_setup_qdrant.yaml` - Qdrant deployment

### OPT-009: PgAdmin
**Source Playbooks**:
- `services/60_setup_pgadmin.yaml` - PgAdmin deployment
- `services/61r_setup_pgadmin_keycloak.yaml` - PgAdmin Keycloak integration
- `services/62_setup_pgadmin_oidc.yaml` - PgAdmin OIDC configuration

### OPT-010: Penpot
**Source Playbooks**:
- `services/180_setup_penpot_keycloak.yaml` - Penpot Keycloak integration
- `services/181_setup_penpot.yaml` - Penpot deployment

### OPT-011: Valkey
**Source Playbooks**:
- `services/189_valkey_image_build.yaml` - Valkey image building
- `services/190_setup_valkey.yaml` - Valkey deployment

## Additional Components (in orchestration but not in our list)

### Helm Dashboard
**Source Playbooks**:
- `services/130r_deploy_helm_dashboard.yaml` - Helm Dashboard deployment

### Portainer
**Source Playbooks**:
- `services/140r_setup_portainer.yaml` - Portainer deployment

## Files NOT to migrate:
- `core/00_main_cluster_setup copy.yaml` - Just a backup
- `core/build_jupyter_image.yaml` - Utility script
- `core/build_simple_jupyter_image.yaml` - Utility script
- `core/check_jupyter_image.yaml` - Utility script
- `core/process_image.yaml` - Utility script
- `core/104_build_jupyter_images.yaml` - Not used, per instructions
- `services/2099_clean_knative.yaml` - Cleanup utility
- `services/ns.json` - Empty file