# Thinkube Networking and DNS Configuration

This document outlines the networking architecture and DNS configuration for the Thinkube platform, enabling remote development and service access through ZeroTier.

## Network Architecture

### Overview

The Thinkube platform uses multiple network layers:

1. **LAN Network (192.168.1.0/24)**
   - Physical network connecting baremetal hosts
   - Used for direct communication between physical machines

2. **ZeroTier Network (192.168.191.0/24)**
   - Overlay network for remote access
   - Enables development from anywhere with internet access
   - Secure access to all services and hosts

3. **Container Networks**
   - Bridge networks for containers (such as 192.168.100.0/24)
   - Used for communication between containers on the same host

4. **Kubernetes Pod Network**
   - Internal MicroK8s pod communication
   - Managed by MicroK8s networking plugins

### IP Allocation

#### Baremetal Hosts

| Host | LAN IP (br0) | ZeroTier IP |
|------|--------------|-------------|
| bcn1 | 192.168.1.101 | 192.168.191.101 |
| bcn2 | 192.168.1.102 | 192.168.191.102 |

#### LXD Containers

| Container | LAN IP (br0) | Internal IP (lxdbr0) | ZeroTier IP |
|-----------|--------------|----------------------|-------------|
| tkc       | 192.168.1.110 | 192.168.100.10 | 192.168.191.110 |
| tkw1      | 192.168.1.111 | 192.168.100.11 | 192.168.191.111 |
| tkw2      | 192.168.1.112 | 192.168.100.12 | 192.168.191.112 |
| dns1      | 192.168.1.100 | 192.168.100.50 | 192.168.191.1 |

#### MetalLB Range (Assigned to tkc)

The following IP range is allocated for MetalLB to assign to Kubernetes services:

- **Range**: 192.168.191.200 - 192.168.191.205 (6 addresses)
- **Primary Ingress IP**: 192.168.191.200
- **Knative Ingress IP**: 192.168.191.201

## ZeroTier Configuration

### Installation and Setup

1. Install ZeroTier on all hosts and containers:
   ```bash
   apt install -y zerotier-one
   ```

2. Join the ZeroTier network:
   ```bash
   zerotier-cli join <ZEROTIER_NETWORK_ID>
   ```

3. Configure static IP assignments in ZeroTier Central:
   - Assign IPs according to the IP allocation table above
   - Ensure "Allow Ethernet Bridging" is enabled for the controller node

### ZeroTier Routes

Configure the following routes in ZeroTier Central:

1. Route for MetalLB range:
   - **Destination**: 192.168.191.200/29
   - **Via**: 192.168.191.110 (tkc)

2. Internal container network route (optional):
   - **Destination**: 192.168.100.0/24
   - **Via**: 192.168.191.101 (bcn1) and 192.168.191.102 (bcn2)

### ZeroTier Host Configuration

Each host with ZeroTier should have:

1. Proper interface configuration
2. IP forwarding enabled
3. NAT configured if needed

Example configuration for enabling IP forwarding:
```bash
# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Allow forwarding in firewall
iptables -A FORWARD -i zt+ -j ACCEPT
iptables -A FORWARD -o zt+ -j ACCEPT
```

## DNS Configuration

### DNS Server Setup (dns1)

The DNS server (dns1) will be configured using bind9 to provide name resolution for all Thinkube services.

#### Bind9 Configuration

1. Install bind9:
   ```bash
   apt install -y bind9 bind9utils bind9-doc
   ```

2. Configure named.conf.local:
   ```
   zone "thinkube.com" {
       type master;
       file "/etc/bind/zones/db.thinkube.com";
   };
   
   zone "kn.thinkube.com" {
       type master;
       file "/etc/bind/zones/db.kn.thinkube.com";
   };
   ```

3. Create zone files with wildcard records:

   **db.thinkube.com**:
   ```
   $TTL    604800
   @       IN      SOA     dns.thinkube.com. admin.thinkube.com. (
                           2         ; Serial
                           604800    ; Refresh
                           86400     ; Retry
                           2419200   ; Expire
                           604800 )  ; Negative Cache TTL
   
   ; Name servers
   @       IN      NS      dns.thinkube.com.
   
   ; Base domain records
   @       IN      A       192.168.191.110
   dns     IN      A       192.168.191.1
   
   ; Wildcard record for all services
   *       IN      A       192.168.191.200
   ```

   **db.kn.thinkube.com**:
   ```
   $TTL    604800
   @       IN      SOA     dns.thinkube.com. admin.thinkube.com. (
                           1         ; Serial
                           604800    ; Refresh
                           86400     ; Retry
                           2419200   ; Expire
                           604800 )  ; Negative Cache TTL
   
   ; Name servers
   @       IN      NS      dns.thinkube.com.
   
   ; Wildcard record for all Knative services
   *       IN      A       192.168.191.201
   ```

4. Configure named.conf.options for proper recursion:
   ```
   options {
       directory "/var/cache/bind";
       recursion yes;
       allow-recursion { any; };
       listen-on { 127.0.0.1; 192.168.191.1; 192.168.1.100; 192.168.100.50; };
       forwarders {
           8.8.8.8;
           8.8.4.4;
       };
       dnssec-validation auto;
   };
   ```

### DNS Client Configuration

Configure all hosts and containers to use the dns1 server:

1. Edit /etc/systemd/resolved.conf:
   ```
   [Resolve]
   DNS=192.168.191.1
   Domains=~thinkube.com
   ```

2. Restart systemd-resolved:
   ```bash
   systemctl restart systemd-resolved
   ```

### MicroK8s DNS Integration

Configure CoreDNS in MicroK8s to forward requests for thinkube.com domains to the dns1 server:

1. Edit the CoreDNS ConfigMap:
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
           health
           kubernetes cluster.local in-addr.arpa ip6.arpa {
              pods insecure
              upstream
              fallthrough in-addr.arpa ip6.arpa
           }
           prometheus :9153
           forward . /etc/resolv.conf
           cache 30
           loop
           reload
           loadbalance
       }
       thinkube.com:53 {
           errors
           cache 30
           forward . 192.168.191.1
       }
       kn.thinkube.com:53 {
           errors
           cache 30
           forward . 192.168.191.1
       }
   ```

2. Apply the ConfigMap and restart CoreDNS:
   ```bash
   kubectl apply -f coredns-configmap.yaml
   kubectl -n kube-system rollout restart deployment coredns
   ```

## Service Exposure Strategy

### Ingress Controllers

1. **Main Ingress**:
   - IP: 192.168.191.200
   - Handles all standard services (*.thinkube.com)

2. **Knative Ingress**:
   - IP: 192.168.191.201
   - Handles all Knative services (*.kn.thinkube.com)

### Service Deployment

When deploying new services:

1. Create an Ingress resource with appropriate hostname:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: service-name
     namespace: service-namespace
   spec:
     rules:
     - host: service-name.thinkube.com
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
   nslookup service-name.thinkube.com 192.168.191.1
   ```

2. From inside Kubernetes pod:
   ```bash
   kubectl run -it --rm debug --image=busybox -- nslookup service-name.thinkube.com
   ```

### Connectivity Testing

Test service connectivity:

1. From ZeroTier-connected host:
   ```bash
   curl -v https://service-name.thinkube.com
   ```

2. From inside Kubernetes pod (e.g., JupyterHub):
   ```python
   import requests
   response = requests.get("https://service-name.thinkube.com")
   print(response.status_code)
   ```

## Troubleshooting

### DNS Issues

1. Check if bind9 is running:
   ```bash
   systemctl status bind9
   ```

2. Verify zone files:
   ```bash
   named-checkzone thinkube.com /etc/bind/zones/db.thinkube.com
   ```

3. Test DNS resolution:
   ```bash
   dig @192.168.191.1 service-name.thinkube.com
   ```

### ZeroTier Connectivity

1. Check ZeroTier status:
   ```bash
   zerotier-cli info
   zerotier-cli listnetworks
   ```

2. Verify routing:
   ```bash
   ip route
   ```

3. Test connectivity:
   ```bash
   ping 192.168.191.1
   traceroute 192.168.191.200
   ```

## References

- ZeroTier Documentation: https://docs.zerotier.com/
- Bind9 Documentation: https://bind9.readthedocs.io/
- MicroK8s Documentation: https://microk8s.io/docs