# Thinkube Control

Thinkube Control is the central management interface for the Thinkube platform. It provides a unified API and web interface for platform management, with plans to evolve into an MCP (Model Context Protocol) server for LLM-based management.

## Architecture

The control system consists of:
- **Frontend**: Vue.js application with DaisyUI components
- **Backend**: FastAPI application with Keycloak integration (evolving to MCP server)
- **Authentication**: OAuth2 Proxy with Keycloak OIDC
- **Session Management**: Redis for OAuth2 session storage
- **Build System**: Argo Workflows with Kaniko
- **Deployment**: GitOps via ArgoCD

## Prerequisites

Before deploying the control system, ensure the following components are deployed:
- CORE-004: SSL/TLS Certificates (wildcard certificate in default namespace)
- CORE-006: Keycloak (authentication provider)
- CORE-010: Argo Workflows (for container builds)
- CORE-011: ArgoCD (for GitOps deployment)
- GitHub token configured in inventory or environment

## Deployment

Deploy the control system using:

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/thinkube-control/10_deploy.yaml
```

This will:
1. Create the `control-hub` namespace
2. Copy TLS certificates from the default namespace
3. Deploy Redis for session storage
4. Configure Keycloak client for OIDC authentication
5. Deploy OAuth2 Proxy for authentication
6. Setup GitHub repository integration
7. Configure Argo Workflows for building containers
8. Deploy frontend and backend via ArgoCD

## Testing

Verify the deployment:

```bash
./scripts/run_ansible.sh ansible/40_thinkube/core/thinkube-control/18_test.yaml
```

Tests include:
- Namespace and resource verification
- Service connectivity checks
- ArgoCD application status
- OAuth2 Proxy health
- DNS resolution
- HTTPS endpoint accessibility

## Access

Once deployed, the control interface is accessible at:
- URL: `https://control.thinkube.com`
- Authentication: Via Keycloak SSO
- Authorized users: Admin user configured during deployment

## Components

### OAuth2 Proxy
- Handles authentication with Keycloak
- Manages user sessions in Redis
- Protects control endpoints

### Redis
- Ephemeral Redis deployment
- Stores OAuth2 session data
- No persistence required

### Container Builds
- Argo Workflows builds frontend and backend images
- Kaniko used for rootless container builds
- Images pushed to Harbor registry

### GitOps Deployment
- ArgoCD manages application deployment
- Monitors Git repository for changes
- Automatic sync and rollout

## Configuration

Key configuration variables:
- `domain_name`: Base domain for the platform
- `admin_username`: Admin user granted access
- `github_token`: For repository access
- `kubeconfig`: Kubernetes configuration path

## Rollback

To remove the control deployment:

```bash
./scripts/run_ansible.sh ansible/40_thinkube/core/thinkube-control/19_rollback.yaml
```

This removes all control resources including:
- ArgoCD applications
- OAuth2 Proxy and Redis
- Namespace and secrets

## Troubleshooting

### Authentication Issues
- Verify Keycloak client configuration
- Check OAuth2 Proxy logs: `kubectl logs -n control-hub -l app.kubernetes.io/name=oauth2-proxy`
- Ensure user has `control-user` role in Keycloak

### Build Issues
- Check Argo Workflows: `kubectl -n argo get workflows`
- Verify GitHub token is valid
- Check Kaniko service account permissions

### Deployment Issues
- Verify ArgoCD applications: `kubectl -n argocd get applications`
- Check application sync status in ArgoCD UI
- Review pod logs in control-hub namespace

## Future Development

This application is designed to evolve into an MCP server that will:
- Provide LLM-friendly APIs for platform management
- Enable natural language control of Thinkube services
- Offer structured tool interfaces following the MCP specification
- Support autonomous platform operations

## Notes

- The control system uses the GitHub repository at `thinkube-control/` (local subtree)
- Images are built automatically when code is pushed to the repository
- Frontend and backend are deployed as separate applications
- OAuth2 Proxy provides the authentication layer for all control access