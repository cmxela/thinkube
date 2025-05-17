# Kubernetes Networking Architecture

## Overview

The Thinkube platform uses multiple network segments to provide isolation, security, and functionality. Understanding these networks is crucial for proper service configuration.

## Network Segments

### 1. Physical/LAN Network (br0 bridge)
- **CIDR**: 192.168.1.0/24
- **Interface**: br0 (bridge)
- **Purpose**: Primary cluster communication, high-speed local traffic
- **Usage**: 
  - Kubernetes cluster communication
  - VM-to-VM traffic
  - Storage traffic
  - Primary service endpoints

#### Hosts on LAN Network:
```
bcn1: 192.168.1.101 (baremetal, control plane + worker)
bcn2: 192.168.1.102 (baremetal, worker)
tkc:  192.168.1.110 (VM, control plane)
tkw1: 192.168.1.111 (VM, worker)
tkw2: 192.168.1.112 (VM, worker)
```

### 2. ZeroTier Network
- **CIDR**: 192.168.100.0/24
- **Interface**: ztxxxxxxxx
- **Purpose**: Remote access, management traffic
- **Usage**:
  - SSH access from anywhere
  - Management operations
  - Cross-site connectivity (future)
  
#### Hosts on ZeroTier:
```
bcn1: 192.168.100.1
bcn2: 192.168.100.2  
tkc:  192.168.100.10
tkw1: 192.168.100.11
tkw2: 192.168.100.12
```

### 3. LXD Internal Network
- **CIDR**: 10.229.145.0/24
- **Interface**: lxdbr0
- **Purpose**: Container/VM internal communication
- **Usage**:
  - Default network for LXD containers
  - DHCP for containers
  - NAT gateway for containers

#### Network Details:
```
Bridge: lxdbr0
Gateway: 10.229.145.1 (on host)
DHCP Range: 10.229.145.2 - 10.229.145.254
```

## Service Network Selection

### Kubernetes (MicroK8s)
- **Uses**: LAN Network (192.168.1.0/24)
- **Why**: 
  - Low latency requirement
  - High bandwidth for container images
  - etcd consensus protocol sensitive to latency
  - API server needs reliable connectivity

```yaml
# In MicroK8s configuration
node_ip: "{{ lan_ip }}"  # Not zerotier_ip!
```

### DNS Service
- **Primary**: LAN Network
- **Secondary**: Available on all networks
- **Configuration**:
  ```
  listen-on: 192.168.1.0/24, 192.168.100.0/24
  allow-query: any
  ```

### Storage (Future)
- **Recommended**: LAN Network only
- **Why**: Maximum throughput, minimum latency

### Monitoring/Logging
- **Recommended**: LAN Network primary, ZeroTier for remote access
- **Why**: High volume of metrics/logs need bandwidth

## Network Architecture Diagram

```
Internet
    |
    v
[Router] --- 192.168.1.0/24 (Physical LAN)
    |
    +--[br0 Bridge on Hosts]
           |
           +-- bcn1 (192.168.1.101)
           |     +-- lxdbr0 (10.229.145.0/24)
           |     +-- zt* (192.168.100.1)
           |
           +-- bcn2 (192.168.1.102)
           |     +-- lxdbr0 (10.229.145.0/24)
           |     +-- zt* (192.168.100.2)
           |
           +-- VMs via bridge
                 +-- tkc  (192.168.1.110 / 192.168.100.10)
                 +-- tkw1 (192.168.1.111 / 192.168.100.11)
                 +-- tkw2 (192.168.1.112 / 192.168.100.12)
```

## IP Addressing Scheme

### Baremetal Hosts
| Host | LAN IP | ZeroTier IP | LXD Bridge | Role |
|------|--------|-------------|------------|------|
| bcn1 | 192.168.1.101 | 192.168.100.1 | 10.229.145.1/24 | Control+Worker |
| bcn2 | 192.168.1.102 | 192.168.100.2 | 10.229.145.1/24 | Worker |

### Virtual Machines
| VM | LAN IP | ZeroTier IP | Internal IP | Role |
|----|--------|-------------|-------------|------|
| tkc | 192.168.1.110 | 192.168.100.10 | 10.229.145.x | Control Plane |
| tkw1 | 192.168.1.111 | 192.168.100.11 | 10.229.145.x | Worker |
| tkw2 | 192.168.1.112 | 192.168.100.12 | 10.229.145.x | Worker |

## Network Usage Guidelines

### When to Use LAN Network (192.168.1.0/24)
- Kubernetes cluster communication
- Storage traffic
- Database replication
- High-bandwidth applications
- Low-latency requirements

### When to Use ZeroTier (192.168.100.0/24)
- Remote SSH access
- Management interfaces
- Cross-site connectivity
- Non-critical monitoring
- Development access

### When to Use LXD Network (10.229.145.0/24)
- Container internal traffic
- Isolated development environments
- Testing environments
- Services that don't need external access

## Troubleshooting

### Common Issues

1. **Worker Can't Join Cluster**
   - Check: Is MicroK8s using lan_ip not zerotier_ip?
   - Verify: Can worker ping control plane on LAN IP?
   - Test: `microk8s.add-node` shows correct IP?

2. **Service Unreachable**
   - Check: Which network is the service bound to?
   - Verify: Firewall rules for that network
   - Test: Can you ping between nodes on that network?

3. **DNS Resolution Failing**
   - Check: DNS service listening on correct networks
   - Verify: Client using correct DNS server IP
   - Test: `dig @192.168.1.110 service.local`

### Network Testing Commands

```bash
# Test LAN connectivity
ping 192.168.1.110

# Test ZeroTier connectivity  
ping 192.168.100.10

# Test DNS resolution
nslookup tkc.thinkube.com 192.168.1.110

# Check routing table
ip route show

# Check interface configuration
ip addr show

# Test port connectivity
nc -zv 192.168.1.110 16443
```

## Best Practices

1. **Service Placement**
   - Use LAN for cluster services
   - Use ZeroTier for management only
   - Don't mix networks for single service

2. **Security**
   - Firewall between networks
   - Limit ZeroTier access
   - Use LAN for sensitive traffic

3. **Performance**
   - Monitor network utilization
   - Keep storage traffic on LAN
   - Use appropriate network for workload

4. **Future Expansion**
   - Plan IP allocation carefully
   - Document all network changes
   - Consider VLANs for isolation