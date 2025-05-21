# Certificate Management Architecture

## Overview

This document outlines the certificate management architecture for Thinkube platform, focusing on how to properly use cert-manager with ingress-based TLS termination.

## Core Principles

1. **TLS Termination at Ingress**: SSL/TLS is terminated at the ingress controllers
2. **Minimal Certificate Distribution**: Certificates primarily reside with ingress controllers
3. **Native Kubernetes Resources**: Use cert-manager's Certificate resources
4. **Default Certificates for Ingress Controllers**: Configure ingress controllers with default certificates
5. **Automated Management**: All certificate lifecycle operations handled by cert-manager

## Certificate Architecture

### Certificate Structure

We use separate certificates to avoid DNS challenge validation conflicts:

1. **Wildcard Certificate**: For all subdomains
   ```yaml
   dnsNames:
     - *.thinkube.com              # Wildcard for all subdomains
     - *.kn.thinkube.com           # Wildcard for Knative services
   ```

2. **Base Domain Certificate**: Created on-demand for specific services
   ```yaml
   dnsNames:
     - thinkube.com                # Base domain only
   ```

This separation prevents conflicts in Let's Encrypt DNS-01 validation when both a domain and its wildcard are requested in a single certificate.

### Ingress-Based TLS Termination

In Kubernetes, SSL/TLS is typically terminated at the ingress controller level:

1. External HTTPS traffic reaches the ingress controller
2. Ingress controller terminates SSL/TLS using the configured certificates
3. Internal traffic within the cluster is unencrypted HTTP
4. Components communicate via internal service names or via ingress endpoints

### Issuer Configuration

We use Let's Encrypt with DNS-01 validation through Cloudflare:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@thinkube.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - dns01:
        cloudflare:
          email: admin@thinkube.com
          apiTokenSecretRef:
            name: cloudflare-api-token
            key: api-token
```

### Certificate Management Approach

Two primary approaches for certificate management:

1. **Centralized Certificate with Default Configuration**:
   - Create one wildcard Certificate in each ingress controller namespace
   - Configure ingress controllers to use these as default certificates
   - Simplifies management but requires wildcard certificates

2. **Per-Host Certificates**:
   - Create individual Certificate resources for specific hostnames
   - Reference these in Ingress resources
   - More granular but requires more management overhead

We use approach #1 for simplicity and reduced management overhead.

## Ingress Controller Configuration

### Primary Ingress Controller (for *.thinkube.com)

```yaml
controller:
  extraArgs:
    default-ssl-certificate: "ingress/ingress-tls-secret"
```

### Secondary Ingress Controller (for *.kn.thinkube.com)

```yaml
controller:
  extraArgs:
    default-ssl-certificate: "ingress-kn/ingress-kn-tls-secret"
```

## Certificate Implementation

### Certificate Resources

Create a wildcard Certificate resource in each ingress controller namespace:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wildcard-certificate
  namespace: ingress
  annotations:
    cert-manager.io/issue-temporary-certificate: "true"
    cert-manager.io/dns01-recursive-nameservers: "8.8.8.8:53,1.1.1.1:53"
    cert-manager.io/dns01-recursive-nameservers-only: "true"
    acme.cert-manager.io/dns01-check-interval: "10s"
    acme.cert-manager.io/dns01-propagation-timeout: "180s"
spec:
  secretName: ingress-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: "*.thinkube.com"
  dnsNames:
  - "*.thinkube.com"
  - "*.kn.thinkube.com"
  renewBefore: 720h
```

For services on the base domain, create a separate certificate:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: base-domain-certificate
  namespace: ingress
  annotations:
    cert-manager.io/issue-temporary-certificate: "true"
    cert-manager.io/dns01-recursive-nameservers: "8.8.8.8:53,1.1.1.1:53"
    cert-manager.io/dns01-recursive-nameservers-only: "true"
    acme.cert-manager.io/dns01-check-interval: "10s"
    acme.cert-manager.io/dns01-propagation-timeout: "180s"
spec:
  secretName: base-domain-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: "thinkube.com"
  dnsNames:
  - "thinkube.com"
  renewBefore: 720h
```

### Component Ingress Resources

For each component that needs HTTPS, create an Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: component-ingress
  namespace: component-namespace
  annotations:
    kubernetes.io/ingress.class: "nginx"  # Use primary or secondary as needed
spec:
  # TLS section is optional when using default cert on ingress controller
  tls:
  - hosts:
    - component.thinkube.com
  rules:
  - host: component.thinkube.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: component-service
            port:
              number: 80
```

## Inter-Service Communication

For services that need to communicate with each other (like Harbor with Keycloak):

1. **Internal Communication**: Use internal service names when possible (no TLS needed)
2. **External Communication**: For services communicating via ingress endpoints:
   - Configure components to trust the Let's Encrypt CA certificates
   - Ensure proper hostname validation
   - Use SNI (Server Name Indication) for TLS connections

### Base Domain Handling

For services that need to use the base domain (thinkube.com):

1. Create a dedicated certificate specifically for the base domain in the service's deployment playbook
2. Reference this certificate in the ingress resource for the service
3. Keep the base domain certificate separate from wildcard certificates to avoid DNS challenge conflicts

## Certificate Validation Issues and Solutions

Common certificate validation issues:

1. **Missing CA Trust**: Client doesn't trust the CA that issued the server certificate
   - Solution: Add Let's Encrypt root and intermediate certificates to client trust store

2. **Hostname Mismatch**: Certificate doesn't match the hostname being accessed
   - Solution: Ensure client uses the correct hostname matching a certificate SAN

3. **Certificate Chain Issues**: Incomplete certificate chain presented by server
   - Solution: Ensure ingress controller presents the full certificate chain

4. **SNI Issues**: Client doesn't send SNI header or server ignores it
   - Solution: Configure clients to use SNI when connecting

5. **DNS Challenge Conflicts**: Validation fails when both domain and wildcard in same certificate
   - Solution: Use separate certificates for base domain and wildcards as documented above
   - This prevents conflicts in DNS-01 challenges for Let's Encrypt validation

6. **Challenge Cleanup Errors**: Certificate valid but errors during DNS record cleanup
   - Solution: These don't prevent certificate issuance, just leave stale TXT records
   - Periodically check for old _acme-challenge DNS records and clean them manually if needed

## Testing and Validation

Test certificate configuration for each component:

```yaml
- name: Test certificate validation
  ansible.builtin.command: |
    curl -v https://{{ component_hostname }}
  register: cert_test
  failed_when: "'SSL certificate verify ok' not in cert_test.stderr"
```

## Component Implementation Checklist

- [ ] Verify wildcard certificates exist in ingress controller namespaces
- [ ] Configure ingress controllers with default certificates
- [ ] Create Ingress resources for component with proper annotations
- [ ] Configure clients to trust Let's Encrypt certificates when needed
- [ ] Test certificate validation for all components

## Core Infrastructure Deployment Sequence

Based on the actual component dependencies, the correct deployment sequence is:

1. **Deploy Kubernetes Infrastructure**
   - MicroK8s (CORE-001, CORE-002)
   - cert-manager (CORE-003a) - Creates wildcard certificates
   - Ingress Controllers (CORE-003b) - Configures default certificates

2. **Deploy Keycloak Identity Provider** (CORE-004)
   - Depends on cert-manager and ingress controllers
   - Uses wildcard certificates for TLS termination

3. **Deploy Harbor Container Registry** (CORE-005)
   - Depends on Keycloak for OIDC authentication
   - Uses wildcard certificates for TLS termination
   - Integrates with Keycloak for user authentication

4. **Deploy Further Components**
   - PostgreSQL, MinIO, and other components
   - All use Harbor as container registry

This sequence ensures that all components have proper certificate validation when communicating with each other.