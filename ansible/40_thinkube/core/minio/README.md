# MinIO S3-Compatible Object Storage

This component deploys MinIO, an S3-compatible object storage service, with Keycloak SSO integration for Thinkube platform.

## Features

- S3-compatible API for object storage
- Web-based management console
- Keycloak SSO integration with persistent authentication
- Policy-based access control
- StatefulSet deployment with persistent storage
- TLS secured endpoints

## Deployment Architecture

MinIO is deployed as a StatefulSet with the following components:

- MinIO server with S3 API (port 9000) and management console (port 9090)
- Persistent Volume Claim for data storage
- Ingress routes for API and console access
- Keycloak client for SSO authentication
- TLS certificates for secure communication

## Prerequisites

- MicroK8s Kubernetes cluster
- Keycloak identity provider
- NGINX Ingress Controller
- Storage class for persistence
- Wildcard TLS certificate

## Deployment Steps

1. Deploy MinIO with base configuration:
   ```bash
   cd ~/thinkube
   ./scripts/run_ansible.sh ansible/40_thinkube/core/minio/10_deploy.yaml
   ```

2. Configure Keycloak client for MinIO:
   ```bash
   export ADMIN_PASSWORD=your_admin_password
   ./scripts/run_ansible.sh ansible/40_thinkube/core/minio/11_configure_keycloak.yaml
   ```

3. Set up OIDC integration:
   ```bash
   export ADMIN_PASSWORD=your_admin_password
   ./scripts/run_ansible.sh ansible/40_thinkube/core/minio/12_configure_oidc.yaml
   ```

4. Verify the deployment:
   ```bash
   export ADMIN_PASSWORD=your_admin_password
   ./scripts/run_ansible.sh ansible/40_thinkube/core/minio/18_test.yaml
   ```

## Accessing MinIO

- **S3 API Endpoint**: `https://s3.thinkube.com`
- **Console URL**: `https://minio.thinkube.com`
- **Authentication**: Use Keycloak SSO login via the console or use your admin credentials for direct access

## Integration with Other Services

Services can access MinIO using:

1. **In-cluster access**: Use service name `minio.minio.svc.cluster.local`
2. **External API access**: Use `https://s3.thinkube.com`
3. **Console access**: Use `https://minio.thinkube.com`

## Persistent Authentication

MinIO is configured with persistent authentication via:

- Extended token lifespans (24h access tokens, 30d offline sessions)
- Offline access capability for persistent authentication
- Policy claim mapping in both access and refresh tokens

This prevents the "Policy claim missing from JWT token" error that would otherwise occur when tokens expire.

## Policy-Based Authorization

User permissions are controlled via the `policy` attribute in Keycloak:

- `consoleAdmin`: Full administrative access to MinIO
- Add other policies as needed for granular permissions

## Rolling Back

To remove MinIO completely:

```bash
export ADMIN_PASSWORD=your_admin_password
./scripts/run_ansible.sh ansible/40_thinkube/core/minio/19_rollback.yaml
```

## Troubleshooting

To check MinIO logs:

```bash
kubectl -n minio logs deploy/minio -f
```

For OIDC configuration issues:

```bash
mc admin trace minio
```

Then access the console to see detailed logging of the OIDC authentication flow.