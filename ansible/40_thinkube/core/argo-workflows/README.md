# Argo Workflows & Argo Events

This component deploys [Argo Workflows](https://argoproj.github.io/workflows/) and [Argo Events](https://argoproj.github.io/events/) for workflow automation and event-driven processing in the Thinkube environment.

## Features

- Full deployment of Argo Workflows and Argo Events with Keycloak SSO integration
- Configuration of artifact storage using MinIO
- Secure UI and gRPC access with TLS certificates (via cert-manager)
- CLI installation and token-based authentication
- Test workflow execution
- Complete rollback capability

## Prerequisites

- MicroK8s Kubernetes cluster (CORE-001 and CORE-002)
- Cert-Manager (CORE-003) for TLS certificates
- Keycloak (CORE-004) for SSO authentication
- MinIO (CORE-006) for artifact storage

## Deployment

The deployment process consists of multiple stages:

1. **Configure Keycloak Client**: Set up the OAuth2/OIDC client in Keycloak
2. **Deploy Argo Workflows & Events**: Deploy the main services with Helm
3. **Set Up CLI & Token Authentication**: Configure service account token
4. **Configure Artifact Storage**: Set up MinIO integration

### 1. Configure Keycloak Client

```bash
cd ~/thinkube
ADMIN_PASSWORD=your_password ./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/10_configure_keycloak.yaml
```

This creates a new OAuth2/OIDC client in Keycloak for Argo with proper redirect URIs and audience mappings.

### 2. Deploy Argo Workflows & Events

```bash
cd ~/thinkube
ADMIN_PASSWORD=your_password ./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/11_deploy.yaml
```

This installs both Argo Workflows and Argo Events using Helm and configures:
- TLS certificates for UI and gRPC access
- OIDC authentication with Keycloak
- Resource limits for all components
- Ingress for web UI and gRPC API

### 3. Set Up CLI & Token Authentication

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/12_setup_token.yaml
```

This installs the Argo CLI and configures service account token authentication for programmatic access.

### 4. Configure Artifact Storage

```bash
cd ~/thinkube
ADMIN_PASSWORD=your_password ./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/13_setup_artifacts.yaml
```

This integrates Argo with MinIO for artifact storage, creating:
- Credentials secret
- Artifact repository configuration
- Test workflow with artifact storage

## Testing

To verify the installation is working correctly:

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/18_test.yaml
```

The test script verifies:
- Argo pods are running
- TLS certificates are valid
- OIDC authentication is configured
- Service account token is working
- Artifact storage is properly configured
- Test workflow executes successfully

## Accessing Argo

After deployment, Argo UI is available at: `https://argo.thinkube.com`

The gRPC API endpoint is available at: `https://grpc-argo.thinkube.com`

## Rollback

To completely remove Argo Workflows & Events:

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/argo-workflows/19_rollback.yaml
```

This removes:
- Helm releases
- Namespace and all resources
- Ingress configurations
- (Optionally) CLI binary

Note: The Keycloak client is not automatically removed.

## Variables

The following variables are used:

| Variable | Description | Default |
|----------|-------------|---------|
| `domain_name` | Base domain name | `thinkube.com` |
| `admin_username` | Admin username | `tkadmin` |
| `auth_realm_username` | Realm username for SSO | `thinkube` |
| `argo_namespace` | Kubernetes namespace | `argo` |
| `minio_api_hostname` | MinIO S3 API hostname | `s3.thinkube.com` |
| `kubeconfig` | Kubernetes config path | `/var/snap/microk8s/current/credentials/client.config` |
| `kubectl_bin` | Path to kubectl binary | `/snap/bin/microk8s.kubectl` |
| `helm_bin` | Path to helm binary | `/snap/bin/microk8s.helm3` |

## Environment Variables

These environment variables are required:

| Variable | Description |
|----------|-------------|
| `ADMIN_PASSWORD` | Admin password for Keycloak and MinIO |

## Troubleshooting

### Common Issues

1. **OIDC Login Failure**: Verify Keycloak client configuration and redirect URIs
   ```bash
   ./scripts/run_ssh_command.sh tkc "microk8s.kubectl get secret -n argo argo-server-sso -o yaml"
   ```

2. **Artifact Storage Issues**: Check MinIO connectivity
   ```bash
   ./scripts/run_ssh_command.sh tkc "mc ls minio/argo-artifacts"
   ```

3. **Pod Startup Issues**: Check events and logs
   ```bash
   ./scripts/run_ssh_command.sh tkc "microk8s.kubectl get events -n argo"
   ./scripts/run_ssh_command.sh tkc "microk8s.kubectl logs -n argo deploy/argo-workflows-server -c argo-workflows-server"
   ```

## References

- [Argo Workflows Documentation](https://argoproj.github.io/argo-workflows/)
- [Argo Events Documentation](https://argoproj.github.io/argo-events/)
- [Argo Helm Charts](https://github.com/argoproj/argo-helm)