# CORE-003c: DNS Resolution Service Configuration

## Overview

Implement comprehensive DNS resolution configuration for all nodes in the Thinkube platform. This component ensures all nodes can properly resolve both internal Kubernetes services and external Thinkube domains.

## Requirements

- Must run after CoreDNS deployment (CORE-003b)
- All nodes must be able to resolve `*.thinkube.com` domains
- MicroK8s nodes must resolve both `*.cluster.local` and `*.thinkube.com` domains
- DNS configuration must persist across system reboots

## Technical Specification

### Component Structure
```
ansible/40_thinkube/core/infrastructure/dns-resolution/
├── 10_configure_all_nodes.yaml
├── 18_test.yaml
├── 19_rollback.yaml
└── README.md
```

### Functionality

The DNS resolution component configures systemd-resolved on all nodes with appropriate DNS servers based on node type:

1. **MicroK8s nodes**: Configure to use CoreDNS as primary DNS with ZeroTier DNS as fallback
2. **Standard nodes**: Configure to use ZeroTier DNS directly
3. **Domain routing**: Ensure proper domain-specific DNS routing
4. **Fallback configuration**: Configure external DNS servers for non-Thinkube domains

### Implementation Details

- Uses systemd-resolved drop-in configuration files
- Configures different DNS settings based on node membership in groups
- Verifies DNS resolution after configuration
- Provides rollback capability

## Acceptance Criteria

- [ ] All nodes can resolve `*.thinkube.com` domains
- [ ] MicroK8s nodes can resolve `*.cluster.local` domains
- [ ] DNS configuration survives system restarts
- [ ] Test playbook validates DNS resolution
- [ ] Rollback playbook can restore previous DNS configuration

## Dependencies

- CORE-001: MicroK8s installation
- CORE-003: Certificate Manager  
- CORE-003b: CoreDNS configuration
- ZeroTier DNS server (dns1) must be operational