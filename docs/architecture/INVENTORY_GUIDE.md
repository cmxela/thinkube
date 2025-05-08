# Thinkube Inventory Guide

This document explains the structure of the Thinkube inventory system and provides instructions for adding new nodes to your deployment.

## Inventory Structure

The inventory is organized around both physical and logical groupings of hosts:

### Physical Infrastructure

- **Baremetal Servers**: Physical machines that host LXD containers
  - **Headless**: Servers without displays (e.g., `bcn2`)
  - **Desktops**: Servers with displays and desktop environments (e.g., `bcn1`)
  - **DGX**: Special group for NVIDIA DGX servers (ARM architecture)

- **LXD Containers**: Virtual machines running on the baremetal hosts
  - **DNS Containers**: Containers serving DNS (e.g., `dns1`)
  - **MicroK8s Containers**:
    - **Controllers**: K8s control plane nodes (e.g., `tkc`)
    - **Workers**: K8s worker nodes (e.g., `tkw1`, `tkw2`)

### Logical Groupings

- **Architecture Groups**: Hosts grouped by CPU architecture
  - **x86_64**: Intel/AMD architecture hosts
  - **arm64**: ARM architecture hosts (like DGX Spark)

- **Network Groups**:
  - **ZeroTier Nodes**: Hosts accessible via ZeroTier network

- **Role-Based Groups**:
  - **MicroK8s**: All Kubernetes-related hosts
    - **Control Plane**: Kubernetes controllers
    - **Workers**: Kubernetes workers
  - **Management**: Ansible controller hosts
  - **DNS**: DNS servers

## Networking Configuration

Each container in the inventory has multiple IP addresses for different network interfaces:

1. **LAN IP (`lan_ip`)**: External IP on the `br0` bridge (192.168.1.x)
2. **Internal IP (`internal_ip`)**: Internal container network on `lxdbr0` (192.168.100.x)
3. **ZeroTier IP (`zerotier_ip`)**: Remote access network (192.168.191.x)

## IP Allocation Scheme

| Host Type        | LAN (192.168.1.x) | Internal (192.168.100.x) | ZeroTier (192.168.191.x) |
|------------------|-------------------|--------------------------|--------------------------|
| Physical Servers | 10x (101, 102)    | N/A                      | 10x (101, 102, 103)      |
| DNS              | 100               | 50                       | 1                        |
| K8s Controller   | 11x (110)         | 1x (10)                  | 11x (110)                |
| K8s Workers      | 11x (111, 112)    | 1x (11, 12)              | 11x (113 for ARM)        |

## Adding New Nodes

### Adding a New Physical Server

To add a new x86_64 physical server:

1. Add the host to the appropriate baremetal group and architecture group:

```yaml
baremetal:
  children:
    headless:
      hosts:
        new-server:  # New server name
          ansible_host: 192.168.1.xxx  # LAN IP
          zerotier_ip: 192.168.191.xxx  # ZeroTier IP
          server_type: headless  # or desktop
          arch: x86_64
          gpu_type: nvidia  # or amd
          gpu_model: "RTX xxxx"  # GPU model
          zerotier_enabled: true
```

2. Add the server to the ZeroTier nodes group if needed:

```yaml
zerotier_nodes:
  hosts:
    new-server:
```

3. Add the server to the arch group:

```yaml
arch:
  children:
    x86_64:
      hosts:
        new-server:
```

### Adding a New DGX Server (ARM64)

For a DGX server with ARM architecture:

```yaml
baremetal:
  children:
    dgx:
      hosts:
        dgx1:
          ansible_host: 192.168.1.xxx
          zerotier_ip: 192.168.191.103
          server_type: headless
          arch: arm64
          gpu_type: nvidia
          gpu_model: "A100"  # or other GPU type
          zerotier_enabled: true
```

Add to the arm64 architecture group:

```yaml
arch:
  children:
    arm64:
      hosts:
        dgx1:
```

### Adding a New LXD Container

To add a new container (example for a MicroK8s worker):

1. Identify the parent host where the container will run:

```yaml
lxd_containers:
  children:
    microk8s_containers:
      children:
        workers:
          hosts:
            new-worker:
              parent_host: bcn2  # Server hosting the container
              memory: "48GB"
              cpu_cores: 12
              arch: x86_64  # or arm64
              lan_ip: 192.168.1.xxx  # External IP (br0)
              internal_ip: 192.168.100.xxx  # Internal IP (lxdbr0)
              gpu_passthrough: true
              gpu_type: "RTX xxxx"
              pci_slot: "xx:xx.x"  # PCI slot for GPU (for RTX cards)
```

2. Add the container to appropriate logical groups:

```yaml
microk8s:
  children:
    microk8s_workers:
      hosts:
        new-worker:
```

3. For containers that need ZeroTier access, add a ZeroTier IP and to the ZeroTier nodes group:

```yaml
zerotier_nodes:
  hosts:
    new-worker:
```

### Adding a New GPU to a Server or Container

When adding a new GPU to an existing server:

1. Update the `gpu_ids` or `pci_slot` for the server:

```yaml
bcn1:
  gpu_model: "RTX 3090, RTX 4090"  # Update with new GPU models
  gpu_ids: ["0", "1", "2"]  # Add new GPU ID
```

2. For RTX cards using PCI slots, specify the PCI slot instead:

```yaml
pci_slot: "08:00.0"  # Use lspci | grep -i nvidia to find the correct slot
```

## Container Configs for GPU Passthrough

When adding GPUs, also update the container_configs section:

```yaml
container_configs:
  vars:
    bcn1:
      - name: new-worker
        gpu_type: "RTX 4090"
        pci_slot: "09:00.0"
```

## IP Address Planning

When assigning new IP addresses, follow these conventions:

1. **LAN IPs**:
   - Physical servers: 192.168.1.10x
   - DNS server: 192.168.1.100
   - K8s controllers: 192.168.1.11x
   - K8s workers: 192.168.1.11x-12x

2. **Internal IPs**:
   - DNS server: 192.168.100.50
   - K8s controllers: 192.168.100.1x
   - K8s workers: 192.168.100.1x-2x

3. **ZeroTier IPs**:
   - DNS server: 192.168.191.1 (primary network service)
   - Physical servers: 192.168.191.10x
   - K8s controllers: 192.168.191.11x
   - ARM workers: 192.168.191.11x

## Network Configuration

After adding new entries to the inventory, you'll need to:

1. Ensure ZeroTier is properly set up if the node needs remote access
2. Configure the container with proper networking:

```bash
# For a new container, the playbook will set up:
# - eth0: Connected to lxdbr0 (internal)
# - eth1: Connected to br0 (external)
```

## Architecture-Specific Considerations

For ARM64 nodes (like DGX servers):

1. Use ARM64-compatible images for containers
2. Ensure Kubernetes components are ARM64-compatible
3. Consider tagging workloads with node selectors for architecture

## Example: Adding a DGX Spark Server with Worker Container

Here's a complete example for adding a DGX Spark server with one worker container:

```yaml
# Add to arch groups
arch:
  children:
    arm64:
      hosts:
        dgx1:
        tkw3:

# Add to baremetal
baremetal:
  children:
    dgx:
      hosts:
        dgx1:
          ansible_host: 192.168.1.120
          zerotier_ip: 192.168.191.103
          server_type: headless
          arch: arm64
          gpu_type: nvidia
          gpu_model: "A100"
          zerotier_enabled: true

# Add to ZeroTier nodes
zerotier_nodes:
  hosts:
    dgx1:
    tkw3:

# Add container
lxd_containers:
  children:
    microk8s_containers:
      children:
        workers:
          hosts:
            tkw3:
              parent_host: dgx1
              memory: "48GB"
              cpu_cores: 12
              arch: arm64
              lan_ip: 192.168.1.113
              internal_ip: 192.168.100.13
              zerotier_ip: 192.168.191.113
              gpu_passthrough: true
              gpu_type: "A100"
              pci_slot: "01:00.0"

# Add to MicroK8s workers
microk8s:
  children:
    microk8s_workers:
      hosts:
        tkw3:

# Add GPU config
container_configs:
  vars:
    dgx1:
      - name: tkw3
        gpu_type: "A100"
        pci_slot: "01:00.0"
```