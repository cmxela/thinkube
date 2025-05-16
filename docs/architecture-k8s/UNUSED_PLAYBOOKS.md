# Unused Playbooks Analysis

## Playbooks NOT called by orchestration playbooks

### Core Playbooks (in core/ but not in 00_main_cluster_setup.yaml):
1. `00_main_cluster_setup copy.yaml` - Duplicate/backup file
2. `build_jupyter_image.yaml` - Standalone Jupyter image build
3. `build_simple_jupyter_image.yaml` - Standalone simple Jupyter image build
4. `check_jupyter_image.yaml` - Jupyter image check utility
5. `process_image.yaml` - Image processing utility
6. `104_build_jupyter_images.yaml` - Additional Jupyter image builds (not in main setup)
7. `110_setup_knative.yaml` - Knative deployment (not in main cluster setup)
8. `20_deploy_awx.yaml` - AWX deployment is imported as `110_deploy_awx.yaml`

### Service Playbooks (in services/ but not in 00_setup_services.yaml):
1. `2099_clean_knative.yaml` - Knative cleanup utility

## Observations:

1. The main cluster setup includes AWX deployment but calls it as `110_deploy_awx.yaml` (instead of the actual `20_deploy_awx.yaml` in services/)
2. Knative is deployed in services (`20_setup_knative.yaml`) but also has a playbook in core (`110_setup_knative.yaml`) that's not used
3. Several utility playbooks for Jupyter image management are not included in the orchestration
4. The copy of the main cluster setup is just a backup

## Components that ARE used:

All playbooks for the following components are properly orchestrated:
- MicroK8s (control and worker)
- Ingress
- CoreDNS
- GPU Operator
- SSL Certificates
- Keycloak
- Harbor
- AWX (as part of core setup)
- Qdrant
- OpenSearch
- MinIO
- PostgreSQL
- PgAdmin
- Argo Workflows & Events
- ArgoCD
- Prometheus
- Grafana
- Code Server
- JupyterHub
- DevPi
- Helm Dashboard
- Portainer
- MkDocs
- Thinkube Dashboard
- MLflow
- Valkey
- Penpot