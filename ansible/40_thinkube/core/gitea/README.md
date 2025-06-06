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

## Configuration

### Manual Configuration
For manual setup with custom repositories:
```bash
./scripts/run_ansible.sh ansible/40_thinkube/core/gitea/15_configure.yaml
```

### Unattended Configuration
For fully automated setup with default repositories:
```bash
./scripts/run_ansible.sh ansible/40_thinkube/core/gitea/16_configure_unattended.yaml
```

## Testing

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/gitea/18_test.yaml
```

## Default Configuration

- Admin user: Created automatically ({{ admin_username }})
- OAuth2: Keycloak provider configured automatically
- API Token: Generated and stored in `gitea-admin-token` secret
- Database: PostgreSQL with `gitea` database
- Storage: 10Gi PVC for repositories
- Resources: 256Mi memory, 100m CPU

## Unattended Installation

The deployment now supports fully unattended installation:
1. Admin user created with environment variable credentials
2. OAuth2 provider configured automatically post-deployment
3. API token generated and stored in Kubernetes secret
4. Optional: Run `16_configure_unattended.yaml` to create default repositories

## Integration Points

- **Keycloak**: OAuth2 authentication (auto-configured)
- **PostgreSQL**: Database backend
- **ArgoCD**: Repository watching with webhooks
- **Harbor**: Container images

## API Access

After deployment, an admin API token is available:
```bash
kubectl get secret -n gitea gitea-admin-token -o jsonpath='{.data.token}' | base64 -d
```