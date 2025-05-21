# Cert-Manager Component

This directory contains Ansible playbooks for deploying and managing cert-manager on MicroK8s.

## Overview

Cert-manager replaces manual SSL certificate management by automatically issuing and renewing certificates from Let's Encrypt using Cloudflare DNS validation.

## Prerequisites

- MicroK8s control and worker nodes (CORE-001, CORE-002)
- Cloudflare API token with DNS edit permissions
- DNS zones configured in Cloudflare

## Environment Variables

- `CLOUDFLARE_API_TOKEN`: Required - Your Cloudflare API token with DNS edit permissions
- `CLOUDFLARE_ZONE_ID`: Required - Your Cloudflare zone ID for the domain (required for API compatibility)

## Playbooks

### 10_deploy.yaml
Deploys cert-manager and configures ClusterIssuers for Let's Encrypt.

Features:
- Enables MicroK8s cert-manager addon
- Creates Cloudflare API token secret
- Configures staging and production ClusterIssuers
- Creates wildcard certificate for all domains

### 18_test.yaml
Tests cert-manager installation and certificate issuance.

Verifies:
- Addon is enabled
- Pods are running
- ClusterIssuers are ready
- Certificates are issued
- Secrets contain valid data

### 19_rollback.yaml
Removes cert-manager and all associated resources.

Actions:
- Deletes all certificates
- Removes ClusterIssuers
- Disables addon
- Cleans up secrets

**WARNING**: This will delete all managed certificates!

## Variables

Key variables used (from inventory):
- `domain_name`: Base domain for certificates
- `k8s_domain`: Kubernetes subdomain (defaults to k8s.domain_name)
- `cert_manager_namespace`: Namespace for cert-manager (default: cert-manager)

## Certificate Configuration

The deployment creates a wildcard certificate covering:
- `*.thinkube.com`
- `*.kn.thinkube.com`

Note: The base domain (`thinkube.com`) is not included in the wildcard certificate to avoid conflicts with DNS challenge validation. When you need to use the base domain, create a separate certificate for it during the specific service deployment using a template like:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: thinkube-base-tls
  namespace: your-service-namespace
  annotations:
    cert-manager.io/issue-temporary-certificate: "true"
    cert-manager.io/dns01-recursive-nameservers: "8.8.8.8:53,1.1.1.1:53" 
    cert-manager.io/dns01-recursive-nameservers-only: "true"
    acme.cert-manager.io/dns01-check-interval: "10s"
    acme.cert-manager.io/dns01-propagation-timeout: "180s"
spec:
  secretName: thinkube-base-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: "thinkube.com"
  dnsNames:
  - "thinkube.com"
  renewBefore: 720h
```

## Usage

**IMPORTANT**: This component requires testing before use. See [TESTING_REQUIRED.md](./TESTING_REQUIRED.md) for details.

1. Set the Cloudflare API token:
   ```bash
   export CLOUDFLARE_API_TOKEN='your-token-here'
   ```

2. Deploy cert-manager:
   ```bash
   ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/cert-manager/10_deploy.yaml
   ```

3. Test the installation:
   ```bash
   ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/cert-manager/18_test.yaml
   ```

4. To rollback (if needed):
   ```bash
   ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/cert-manager/19_rollback.yaml -e confirmation=true
   ```

## Using Certificates in Ingress

### Using the Wildcard Certificate

For any subdomain (like example.thinkube.com), use the wildcard certificate:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  tls:
    - hosts:
        - example.thinkube.com
      secretName: thinkube-com-tls
  rules:
    - host: example.thinkube.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: example-service
                port:
                  number: 80
```

### Using the Base Domain Certificate

For the base domain (thinkube.com), create a separate certificate first, then use it:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: base-domain-ingress
spec:
  tls:
    - hosts:
        - thinkube.com
      secretName: thinkube-base-tls
  rules:
    - host: thinkube.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: main-website
                port:
                  number: 80
```

## Troubleshooting

1. Certificate not issuing:
   - Check ClusterIssuer status: `kubectl describe clusterissuer letsencrypt-prod`
   - Check certificate status: `kubectl describe certificate -n default`
   - Check cert-manager logs: `kubectl logs -n cert-manager deployment/cert-manager`
   - Check certificate requests: `kubectl get certificaterequests -A`
   - Check order status: `kubectl get order -A`

2. DNS validation failing:
   - Verify Cloudflare API token has correct permissions
   - Check DNS challenge status: `kubectl get challenges -A`
   - Check challenge details: `kubectl describe challenges -A`
   - Ensure domain is managed by Cloudflare

3. Handling DNS challenge conflicts:
   - Use separate certificates for base domain and wildcards
   - Never include both `domain.com` and `*.domain.com` in the same certificate
   - For base domain certificates, create them during the specific service deployment
   - Monitor challenges with `kubectl get challenges -A` during issuance

4. Pods not starting:
   - Check namespace: `kubectl get pods -n cert-manager`
   - Check events: `kubectl get events -n cert-manager`
   - Verify CRDs: `kubectl get crds | grep cert-manager`

## Migration from Manual Certificates

This component replaces the manual certificate management from `thinkube-core/playbooks/core/70_create_ssl_certificates.yaml`. 

Key differences:
- Automatic renewal (no cron jobs needed)
- Native Kubernetes integration
- Certificate stored as K8s secrets
- No filesystem access required
- Better observability through CRDs