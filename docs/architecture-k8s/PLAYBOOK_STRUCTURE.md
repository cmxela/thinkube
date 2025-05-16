# Playbook Structure for Core Services

## Overview

This document defines the directory structure and organization for all Kubernetes-related playbooks in the Thinkube project. The structure separates core (essential) and optional components, with each service in its own directory.

## Directory Structure

```
ansible/40_thinkube/
├── core/                           # Essential platform components
│   ├── infrastructure/
│   │   ├── microk8s/
│   │   │   ├── 10_setup_control.yaml
│   │   │   ├── 15_join_workers.yaml
│   │   │   ├── 18_test_cluster.yaml
│   │   │   └── 19_rollback_cluster.yaml
│   │   ├── ingress/
│   │   │   ├── 10_deploy_controllers.yaml
│   │   │   ├── 18_test_ingress.yaml
│   │   │   └── 19_rollback_ingress.yaml
│   │   ├── cert-manager/
│   │   │   ├── 10_deploy.yaml
│   │   │   ├── 15_configure_issuers.yaml
│   │   │   ├── 18_test.yaml
│   │   │   └── 19_rollback.yaml
│   │   └── coredns/
│   │       ├── 10_configure.yaml
│   │       ├── 18_test.yaml
│   │       └── 19_rollback.yaml
│   ├── keycloak/
│   │   ├── 10_deploy.yaml
│   │   ├── 15_configure_realms.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── postgresql/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── minio/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── harbor/
│   │   ├── 10_deploy.yaml
│   │   ├── 15_configure_projects.yaml
│   │   ├── 20_mirror_images.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── argo-workflows/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── argocd/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── devpi/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── awx/
│   │   ├── 10_deploy.yaml
│   │   ├── 15_configure_templates.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   ├── mkdocs/
│   │   ├── 10_deploy.yaml
│   │   ├── 18_test.yaml
│   │   └── 19_rollback.yaml
│   └── thinkube-dashboard/
│       ├── 10_deploy.yaml
│       ├── 18_test.yaml
│       └── 19_rollback.yaml
└── optional/                       # Components deployed via AWX
    ├── prometheus/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── grafana/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── opensearch/
    │   ├── 10_deploy.yaml
    │   ├── 15_configure_dashboards.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── jupyterhub/
    │   ├── 10_deploy.yaml
    │   ├── 15_configure_gpu.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── code-server/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── mlflow/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── qdrant/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── pgadmin/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── knative/
    │   ├── 10_deploy.yaml
    │   ├── 15_configure_kourier.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    ├── penpot/
    │   ├── 10_deploy.yaml
    │   ├── 18_test.yaml
    │   └── 19_rollback.yaml
    └── valkey/
        ├── 10_deploy.yaml
        ├── 18_test.yaml
        └── 19_rollback.yaml
```

## Numbering Convention

- **10-17**: Main deployment and configuration playbooks
  - `10_deploy.yaml` - Primary deployment playbook
  - `15_configure_*.yaml` - Additional configuration steps
- **18**: Test playbooks
  - `18_test.yaml` - Component testing
- **19**: Rollback playbooks
  - `19_rollback.yaml` - Remove or revert component

## Component Organization

### Infrastructure Components
Core infrastructure services are grouped under the `infrastructure/` directory:
- **microk8s**: Kubernetes cluster setup
- **ingress**: NGINX ingress controllers (primary and secondary)
- **cert-manager**: Certificate management
- **coredns**: DNS configuration

### Core Services
Each service has its own directory containing all related playbooks:
- Deployment playbooks
- Configuration playbooks
- Test playbooks
- Rollback playbooks

## Benefits

1. **Component Isolation**: Each component is self-contained
2. **Easy Navigation**: All related files in one directory
3. **AWX Integration**: Simple job template creation
4. **Consistent Structure**: Same layout for all components
5. **Clear Dependencies**: Easier to understand component relationships

## AWX Integration

Job templates reference playbooks in the optional directory:

```yaml
job_templates:
  # Optional component deployment
  - name: "Deploy Prometheus"
    playbook: "ansible/40_thinkube/optional/prometheus/10_deploy.yaml"
    
  - name: "Deploy JupyterHub"
    playbook: "ansible/40_thinkube/optional/jupyterhub/10_deploy.yaml"
    
  - name: "Test OpenSearch"
    playbook: "ansible/40_thinkube/optional/opensearch/18_test.yaml"
    
  - name: "Rollback MLflow"
    playbook: "ansible/40_thinkube/optional/mlflow/19_rollback.yaml"
```

## Master Deployment

Two master playbooks orchestrate deployments:

### Core Platform Deployment
```yaml
# ansible/40_thinkube/deploy_core_platform.yaml
---
- name: Deploy Core Platform Components
  
  # Infrastructure components
  - import_playbook: core/infrastructure/microk8s/10_setup_control.yaml
  - import_playbook: core/infrastructure/microk8s/15_join_workers.yaml
  - import_playbook: core/infrastructure/cert-manager/10_deploy.yaml
  - import_playbook: core/infrastructure/ingress/10_deploy_controllers.yaml
  
  # Core services
  - import_playbook: core/keycloak/10_deploy.yaml
  - import_playbook: core/postgresql/10_deploy.yaml
  - import_playbook: core/minio/10_deploy.yaml
  - import_playbook: core/harbor/10_deploy.yaml
  
  # CI/CD stack
  - import_playbook: core/argo-workflows/10_deploy.yaml
  - import_playbook: core/argocd/10_deploy.yaml
  - import_playbook: core/devpi/10_deploy.yaml
  - import_playbook: core/awx/10_deploy.yaml
  
  # Essential platform services
  - import_playbook: core/mkdocs/10_deploy.yaml
  - import_playbook: core/thinkube-dashboard/10_deploy.yaml
```

### Optional Components (via AWX)
```yaml
# ansible/40_thinkube/deploy_optional_component.yaml
---
# This is a template for AWX job templates
# AWX will parameterize the component name
- name: Deploy Optional Component
  vars:
    component: "{{ awx_component_name }}"
  
  - import_playbook: "optional/{{ component }}/10_deploy.yaml"
```

## Component README

Each component directory should contain a README.md with:
- Component description
- Dependencies
- Configuration options
- Testing procedures
- Known issues
- Maintenance notes