# Gitea - Git Service for Thinkube

Gitea provides a lightweight Git service with web UI for managing deployment repositories within Thinkube.

## Overview

- **Component**: CORE-014 (Gitea)
- **Namespace**: gitea
- **Service URL**: https://git.{{ domain_name }}
- **Authentication**: Keycloak OAuth2/OIDC
- **Database**: PostgreSQL (shared)
- **Storage**: PVC for repositories

## Features

- Git repository hosting
- Web-based UI
- Keycloak SSO integration
- Webhook support for ArgoCD
- Mirror repositories from GitHub
- Organizations and teams
- API for automation

## Architecture

```
GitHub (templates) → Gitea (deployments) → ArgoCD
                        ↑
                        |
                  Argo Workflows
                  (updates repos)
```

## Deployment

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/gitea/10_deploy.yaml
```

## Testing

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/gitea/18_test.yaml
```

## Default Configuration

- Admin user: Created via Keycloak
- Database: PostgreSQL with `gitea` database
- Storage: 10Gi PVC for repositories
- Resources: 256Mi memory, 100m CPU

## Integration Points

- **Keycloak**: OAuth2 authentication
- **PostgreSQL**: Database backend
- **ArgoCD**: Repository watching
- **Harbor**: Container images