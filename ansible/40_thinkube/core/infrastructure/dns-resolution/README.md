# DNS Resolution Component

## Overview

This component configures DNS resolution on all nodes in the Thinkube platform after CoreDNS has been deployed. It ensures that all nodes can resolve both internal Kubernetes services and external Thinkube domains.

## Playbooks

### 10_configure_all_nodes.yaml
- Configures DNS resolution on all nodes
- Sets up systemd-resolved with appropriate DNS servers
- Configures domain-specific routing
- Verifies DNS resolution is working

### 18_test.yaml
- Tests DNS resolution on all nodes
- Validates both internal and external domain resolution
- Reports DNS configuration status

### 19_rollback.yaml
- Removes DNS configuration changes
- Restores default DNS settings
- Requires confirmation flag for safety

## Requirements

- CoreDNS must be deployed and operational
- ZeroTier DNS server (dns1) must be running
- All nodes must have systemd-resolved or traditional resolv.conf

## DNS Architecture

### MicroK8s Nodes
- Primary DNS: CoreDNS (10.152.183.10)
- Secondary DNS: ZeroTier DNS (192.168.191.1)
- Domains: cluster.local (search domain only)
- IMPORTANT: Do not add thinkube.com or kn.thinkube.com to search domains

### Standard Nodes
- Primary DNS: ZeroTier DNS (192.168.191.1)
- Domains: thinkube.com, kn.thinkube.com

## Usage

### Configure DNS Resolution
```bash
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/dns-resolution/10_configure_all_nodes.yaml
```

### Test DNS Resolution
```bash
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/dns-resolution/18_test.yaml
```

### Rollback Changes
```bash
ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/core/infrastructure/dns-resolution/19_rollback.yaml -e confirm_rollback=true
```

## Troubleshooting

If DNS resolution fails:
1. Check systemd-resolved status: `systemctl status systemd-resolved`
2. Verify DNS configuration: `resolvectl status`
3. Test direct DNS queries: `nslookup domain.thinkube.com 192.168.191.1`
4. Check CoreDNS logs: `kubectl logs -n kube-system -l k8s-app=kube-dns`