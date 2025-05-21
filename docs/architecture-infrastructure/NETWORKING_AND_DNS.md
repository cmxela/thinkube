# Thinkube Networking and DNS Configuration

This document outlines the networking architecture and DNS configuration for the Thinkube platform, enabling remote development and service access through ZeroTier.

## Network Architecture

### Overview

The Thinkube platform uses multiple network layers, all configured through inventory variables without hardcoded values:

1. **LAN Network (defined in inventory as `network_cidr`)**
   - Physical network connecting baremetal hosts
   - Used for direct communication between physical machines
   - Typically 192.168.1.0/24 but configurable in inventory

2. **ZeroTier Network (defined in inventory as `zerotier_cidr`)**
   - Overlay network for remote access
   - Enables development from anywhere with internet access
   - Secure access to all services and hosts
   - Typically 192.168.191.0/24 but configurable in inventory

3. **VM Networks**
   - Bridge networks for VMs (typically 192.168.100.0/24)
   - Used for communication between VMs on the same host
   - Configured via inventory variables

4. **Kubernetes Pod Network**
   - Internal MicroK8s pod communication
   - Managed by MicroK8s networking plugins

### IP Allocation

All IP addresses are defined in inventory and never hardcoded in playbooks. Typical allocation:

#### Baremetal Hosts

| Host | LAN IP (br0) | ZeroTier IP |
|------|--------------|-------------|
| bcn1 | `{{ hostvars['bcn1'].lan_ip }}` | `{{ hostvars['bcn1'].zerotier_ip }}` |
| bcn2 | `{{ hostvars['bcn2'].lan_ip }}` | `{{ hostvars['bcn2'].zerotier_ip }}` |

#### LXD VMs

| VM | LAN IP (br0) | Internal IP (lxdbr0) | ZeroTier IP |
|-----------|--------------|----------------------|-------------|
| tkc | `{{ hostvars['tkc'].lan_ip }}` | `{{ hostvars['tkc'].internal_ip }}` | `{{ hostvars['tkc'].zerotier_ip }}` |
| tkw1 | `{{ hostvars['tkw1'].lan_ip }}` | `{{ hostvars['tkw1'].internal_ip }}` | `{{ hostvars['tkw1'].zerotier_ip }}` |
| tkw2 | `{{ hostvars['tkw2'].lan_ip }}` | `{{ hostvars['tkw2'].internal_ip }}` | `{{ hostvars['tkw2'].zerotier_ip }}` |
| dns1 | `{{ hostvars['dns1'].lan_ip }}` | `{{ hostvars['dns1'].internal_ip }}` | `{{ hostvars['dns1'].zerotier_ip }}` |

#### MetalLB Range

The IP range for MetalLB is defined in inventory variables:

- **Range**: `{{ zerotier_subnet_prefix }}{{ metallb_ip_start_octet }}` to `{{ zerotier_subnet_prefix }}{{ metallb_ip_end_octet }}`
- **Primary Ingress IP**: `{{ zerotier_subnet_prefix }}{{ primary_ingress_ip_octet }}`
- **Knative Ingress IP**: `{{ zerotier_subnet_prefix }}{{ secondary_ingress_ip_octet }}`

## ZeroTier Configuration

### Installation and Setup

1. ZeroTier is installed on all hosts and VMs by the deployment playbooks:
   ```bash
   # This is handled by the playbook, not manual installation
   ansible-playbook -i inventory/inventory.yaml ansible/30_networking/10_setup_zerotier.yaml
   ```

2. Joining the ZeroTier network is automated using the network ID from inventory:
   ```bash
   # Example from playbook (not manual execution)
   zerotier-cli join "{{ zerotier_network_id }}"
   ```

3. Static IP assignments in ZeroTier Central use inventory values:
   - Assign IPs from inventory (zerotier_ip)
   - "Allow Ethernet Bridging" for the controller node

### ZeroTier Routes

Configure routes in ZeroTier Central based on inventory variables:

1. Route for MetalLB range:
   - **Destination**: `{{ zerotier_subnet_prefix }}{{ metallb_ip_start_octet }}/29`
   - **Via**: `{{ hostvars['tkc'].zerotier_ip }}` (control plane VM)

2. Internal VM network route (optional):
   - **Destination**: Subnet from inventory
   - **Via**: ZeroTier IPs of baremetal hosts from inventory

### ZeroTier Host Configuration

Each host with ZeroTier should have:

1. Proper interface configuration
2. IP forwarding enabled
3. NAT configured if needed

Example configuration for enabling IP forwarding (handled by playbooks):
```bash
# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Allow forwarding in firewall
iptables -A FORWARD -i zt+ -j ACCEPT
iptables -A FORWARD -o zt+ -j ACCEPT
```

## DNS Configuration

### DNS Architecture Overview

Thinkube uses a multi-layered DNS approach:

1. **External DNS (dns1 VM)**: Bind9 server for external domain resolution of thinkube.com services
2. **Internal DNS (CoreDNS)**: Kubernetes cluster DNS for service discovery
3. **Node-level DNS (systemd-resolved)**: Client configuration on all nodes

This layered approach ensures both Kubernetes services and external domains can be resolved correctly from any location.

### DNS Server Setup (dns1 VM)

The DNS server (dns1) is configured using bind9 to provide name resolution for all Thinkube services.

#### Bind9 Configuration

1. Installation is handled by the playbook:
   ```bash
   # This is handled by the playbook, not manual installation
   ansible-playbook -i inventory/inventory.yaml ansible/30_networking/20_setup_dns.yaml
   ```

2. Configure named.conf.local:
   ```
   zone "{{ domain_name }}" {
       type master;
       file "/etc/bind/zones/db.{{ domain_name }}";
   };
   
   zone "kn.{{ domain_name }}" {
       type master;
       file "/etc/bind/zones/db.kn.{{ domain_name }}";
   };
   ```

3. Create zone files with wildcard records (templated from inventory variables):

   **db.{{ domain_name }}**:
   ```
   $TTL    604800
   @       IN      SOA     dns.{{ domain_name }}. {{ app_admin_username }}.{{ domain_name }}. (
                           2         ; Serial
                           604800    ; Refresh
                           86400     ; Retry
                           2419200   ; Expire
                           604800 )  ; Negative Cache TTL
   
   ; Name servers
   @       IN      NS      dns.{{ domain_name }}.
   
   ; Base domain records
   @       IN      A       {{ hostvars['tkc'].zerotier_ip }}
   dns     IN      A       {{ hostvars['dns1'].zerotier_ip }}
   
   ; Wildcard record for all services
   *       IN      A       {{ zerotier_subnet_prefix }}{{ primary_ingress_ip_octet }}
   ```

   **db.kn.{{ domain_name }}**:
   ```
   $TTL    604800
   @       IN      SOA     dns.{{ domain_name }}. {{ app_admin_username }}.{{ domain_name }}. (
                           1         ; Serial
                           604800    ; Refresh
                           86400     ; Retry
                           2419200   ; Expire
                           604800 )  ; Negative Cache TTL
   
   ; Name servers
   @       IN      NS      dns.{{ domain_name }}.
   
   ; Wildcard record for all Knative services
   *       IN      A       {{ zerotier_subnet_prefix }}{{ secondary_ingress_ip_octet }}
   ```

4. Configure named.conf.options for proper recursion (using inventory variables):
   ```
   options {
       directory "/var/cache/bind";
       recursion yes;
       allow-recursion { any; };
       listen-on { 127.0.0.1; {{ hostvars['dns1'].zerotier_ip }}; {{ hostvars['dns1'].lan_ip }}; {{ hostvars['dns1'].internal_ip }}; };
       forwarders {
           8.8.8.8;
           8.8.4.4;
       };
       dnssec-validation auto;
   };
   ```

### DNS Client Configuration (All Nodes)

The client DNS configuration for all nodes (MicroK8s, LXD containers, and baremetal) is managed by the CoreDNS component's node configuration playbook:

```bash
# Deploy CoreDNS in Kubernetes
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/10_deploy.yaml

# Configure all nodes to use the correct DNS settings
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/15_configure_node_dns.yaml
```

The node configuration sets up systemd-resolved on all hosts:

1. Creates a drop-in configuration file at `/etc/systemd/resolved.conf.d/thinkube-dns.conf`:
   ```
   [Resolve]
   DNS={{ hostvars['dns1'].zerotier_ip }}
   # Only use cluster.local as search domain to prevent wildcard matching with external domains
   Domains={{ k8s_cluster_domain }}
   ```

2. Restarts systemd-resolved to apply changes:
   ```bash
   systemctl restart systemd-resolved
   ```

> **IMPORTANT**: Do not add `{{ domain_name }}` or `kn.{{ domain_name }}` to search domains as this will cause external domain resolution issues. CoreDNS will forward requests for these domains to ZeroTier DNS server without needing them in search domains.

### MicroK8s DNS Integration (CoreDNS)

CoreDNS is deployed in MicroK8s for in-cluster DNS resolution with proper forwarding to external DNS:

1. **CoreDNS Deployment**:
   ```bash
   # Deploy CoreDNS in Kubernetes
   ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/10_deploy.yaml
   ```

2. **CoreDNS Configuration** (via ConfigMap):
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: coredns
     namespace: kube-system
   data:
     Corefile: |
       .:53 {
           errors
           health {
               lameduck 5s
           }
           ready
           
           hosts {
               {{ secondary_ingress_ip }} *.{{ kn_subdomain }}.{{ domain_name }}
               fallthrough
           }
       
           # CRITICAL: Forward ALL {{ domain_name }} queries to ZeroTier BEFORE kubernetes plugin
           forward {{ domain_name }} {{ zerotier_dns_server }} {
               policy sequential
               health_check 5s
           }
           
           # Forward kn.{{ domain_name }} queries to ZeroTier DNS server
           forward kn.{{ domain_name }} {{ zerotier_dns_server }} {
               policy sequential
               health_check 5s
           }
           
           kubernetes cluster.local in-addr.arpa ip6.arpa {
               pods insecure
               fallthrough in-addr.arpa ip6.arpa
               ttl 30
           }
           
           # Direct mapping from external to internal domains 
           rewrite name regex (.+)\.{{ kn_subdomain }}\.{{ domain_name }}$ {1}.{{ kn_subdomain }}.svc.cluster.local answer auto
           
           prometheus :9153
           
           # Forward everything else to upstream DNS
           forward . /etc/resolv.conf {
               max_concurrent 1000
           }
           
           cache 30
           loop
           reload
           loadbalance
       }
   ```

3. **Key Configuration Points**:
   - Forwards `.thinkube.com` and `.kn.thinkube.com` domains to ZeroTier DNS server
   - Uses Kubernetes internal DNS for cluster services
   - Has domain rewriting for knative services
   - Falls back to upstream DNS for all other domains

4. **Testing CoreDNS Configuration**:
   ```bash
   # Comprehensive DNS test suite
   ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/18_test.yaml
   ```
   
This configuration ensures:
- Kubernetes services can resolve each other (via `cluster.local` domain)
- All nodes can resolve external domains correctly
- Thinkube services are accessible via their domain names
- Knative services are accessible via specific domains

## Service Exposure Strategy

### Ingress Controllers

1. **Main Ingress**:
   - IP: Configured from inventory (`{{ zerotier_subnet_prefix }}{{ primary_ingress_ip_octet }}`)
   - Handles all standard services (`*.{{ domain_name }}`)

2. **Knative Ingress**:
   - IP: Configured from inventory (`{{ zerotier_subnet_prefix }}{{ secondary_ingress_ip_octet }}`)
   - Handles all Knative services (`*.kn.{{ domain_name }}`)

### Service Deployment

When deploying new services, use inventory variables:

1. Create an Ingress resource with appropriate hostname:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: service-name
     namespace: service-namespace
   spec:
     rules:
     - host: service-name.{{ domain_name }}
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: service-name
               port:
                 number: 80
   ```

2. No additional DNS configuration is required thanks to wildcard DNS records

## Validation and Testing

### DNS Resolution Testing

Test DNS resolution from different locations:

1. From ZeroTier-connected host:
   ```bash
   nslookup service-name.{{ domain_name }} {{ hostvars['dns1'].zerotier_ip }}
   ```

2. From inside Kubernetes pod:
   ```bash
   kubectl run -it --rm dnsutils --image=tutum/dnsutils -- nslookup service-name.{{ domain_name }}
   ```

3. Run the comprehensive DNS test playbook:
   ```bash
   cd ~/thinkube
   ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/18_test.yaml
   ```

### Connectivity Testing

Test service connectivity:

1. From ZeroTier-connected host:
   ```bash
   curl -v https://service-name.{{ domain_name }}
   ```

2. From inside Kubernetes pod (e.g., JupyterHub):
   ```python
   import requests
   response = requests.get("https://service-name.{{ domain_name }}")
   print(response.status_code)
   ```

## Troubleshooting

Following our "fail fast" error handling principle, here are structured troubleshooting steps:

### DNS Issues

1. **Basic DNS Resolution Testing**:

If DNS resolution fails, run the comprehensive test playbook first to diagnose:

```bash
cd ~/thinkube
./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/18_test.yaml
```

2. **Common DNS Issues and Fixes**:

```
ERROR: DNS Server Not Responding

DETAILS:
- DNS server at {{ hostvars['dns1'].zerotier_ip }} is not responding
- Current zone configuration may be invalid
- Service may not be running

REQUIRED ACTION:
- Check if bind9 is running: systemctl status bind9
- Verify zone files: named-checkzone {{ domain_name }} /etc/bind/zones/db.{{ domain_name }}
- Test DNS resolution: dig @{{ hostvars['dns1'].zerotier_ip }} service-name.{{ domain_name }}
- Check pod DNS configuration: kubectl run -it --rm dnsutils --image=tutum/dnsutils -- cat /etc/resolv.conf
- Test from inside pods: kubectl run -it --rm dnsutils --image=tutum/dnsutils -- nslookup google.com
- Test with trailing dot: kubectl run -it --rm dnsutils --image=tutum/dnsutils -- nslookup google.com.
```

3. **Resolving External Domain Issues**:

If pods can't resolve external domains (frequent issue):
```
ERROR: External Domain Resolution Failed

DETAILS:
- Pods can't resolve external domains but can resolve kubernetes.default.svc.cluster.local
- This often happens when search domains include {{ domain_name }} or kn.{{ domain_name }}
- Search domains cause DNS queries to try different combinations before the direct lookup

REQUIRED ACTION:
- Check search domains in /etc/systemd/resolved.conf: should ONLY include cluster.local
- Fix with node DNS configuration playbook:
  ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/15_configure_node_dns.yaml
- Verify fix with:
  kubectl run -it --rm dnsutils --image=tutum/dnsutils -- nslookup google.com
```

4. **Resolving CoreDNS Configuration Issues**:

If CoreDNS configuration seems incorrect:
```
ERROR: CoreDNS Configuration Issue

DETAILS:
- CoreDNS ConfigMap may have incorrect settings
- Domain forwarding may be misconfigured

REQUIRED ACTION:
- Reset to default configuration with rollback playbook:
  ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/19_rollback.yaml
- Re-apply proper configuration:
  ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/10_deploy.yaml
  ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/15_configure_node_dns.yaml
- Test with the comprehensive DNS test playbook
```

### ZeroTier Connectivity

If ZeroTier connectivity fails:

```
ERROR: ZeroTier Network Unreachable

DETAILS:
- ZeroTier network {{ zerotier_network_id }} is not connected
- Network routes may be misconfigured
- ZeroTier service may not be running

REQUIRED ACTION:
- Check ZeroTier status: zerotier-cli info
- List networks: zerotier-cli listnetworks
- Verify routing: ip route
- Test connectivity: ping {{ hostvars['dns1'].zerotier_ip }}
```

## References

- ZeroTier Documentation: https://docs.zerotier.com/
- Bind9 Documentation: https://bind9.readthedocs.io/
- MicroK8s Documentation: https://microk8s.io/docs
- CoreDNS Documentation: https://coredns.io/manual/toc/
- Kubernetes DNS: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/

## DNS Component Architecture

### DNS Component Consolidation

In the initial architecture, DNS configuration was split between two components:

1. **CoreDNS Component** (`ansible/40_thinkube/core/infrastructure/coredns/`):
   - Handled CoreDNS deployment in Kubernetes
   - Configured Kubernetes pods DNS resolution
   - Previously limited to MicroK8s nodes only

2. **DNS Resolution Component** (`ansible/40_thinkube/core/infrastructure/dns-resolution/`):
   - Configured systemd-resolved on all nodes
   - Set appropriate search domains

These components were consolidated for simplicity and maintainability:

- The `dns-resolution` functionality was merged into the CoreDNS component
- The `15_configure_node_dns.yaml` playbook was enhanced to target all hosts
- Node-specific configurations are handled within a single playbook

### Current DNS Component Structure

The unified CoreDNS component now:

1. Handles CoreDNS deployment in Kubernetes (`10_deploy.yaml`)
2. Configures systemd-resolved on all nodes (`15_configure_node_dns.yaml`)
3. Provides comprehensive testing (`18_test.yaml`)
4. Includes rollback capability (`19_rollback.yaml`)

This consolidation follows our principle of eliminating redundancy and making the architecture more maintainable.

## Important Principles

- **No Hardcoded Values**: All network configuration must come from inventory
- **Inventory as Single Source of Truth**: All IP addresses and network configuration must be defined in the inventory
- **Variable-Based Configuration**: Use templating for all configuration files
- **VM-Based Deployment**: All services run in LXD VMs, not containers
- **Component Consolidation**: Eliminate redundant components when functions overlap

## Known Issues and Best Practices

### External Domain Resolution in Pods

1. **Minimize Search Domains**: Only include essential domains like `cluster.local` in search domains. Do not add `{{ domain_name }}` or `kn.{{ domain_name }}` to search domains.

2. **Keep CoreDNS and systemd-resolved in Sync**: If you update CoreDNS, make sure to update systemd-resolved configuration consistently.

3. **Use Fully Qualified Domain Names**: When resolving external domains from code running in pods, consider using the trailing dot notation to ensure the domain is treated as a fully qualified domain name (FQDN):
   ```python
   response = requests.get("https://api.github.com./v3")
   ```

4. **DNS Test First Approach**: Always run DNS tests after any network or DNS changes:  
   ```bash
   ./scripts/run_ansible.sh ansible/40_thinkube/core/infrastructure/coredns/18_test.yaml
   ```