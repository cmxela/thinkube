# Thinkube Installer Workflow Plan

## Current Analysis and Issues

### Problems with Current Flow
1. **Configuration too early**: Asking for cluster details before knowing what servers exist
2. **Role assignment premature**: Trying to assign Kubernetes roles before VMs are created
3. **SSH setup missing**: No proper SSH key exchange between baremetal servers
4. **Hardware detection missing**: Can't plan VMs without knowing server capabilities
5. **Network configuration incomplete**: Missing ZeroTier setup for overlay networking

## Correct Workflow Sequence

### Phase 1: Local Setup
1. **Welcome Screen**
   - Introduction to Thinkube
   - Overview of installation process

2. **Requirements Check**
   - Check OS version (Ubuntu 24.04.x)
   - Verify disk space
   - Check network connectivity
   - List missing tools

3. **Sudo Password Collection**
   - Get local admin password
   - Needed only for installing tools
   - Store in sessionStorage for tool installation

4. **Tool Installation**
   - Install ansible, python3, git, fish, zsh
   - Show real-time progress
   - Continue to next step when complete

### Phase 2: Infrastructure Discovery
5. **Baremetal Server Discovery**
   - Start with current machine (control node)
   - Auto-discover other Ubuntu servers on network
   - Collect ONLY: hostname, IP address
   - Allow manual entry for servers not discovered
   - NO authentication needed yet

6. **SSH Setup**
   - Collect SSH credentials for each discovered server
   - Single username/password for all servers (homogeneous setup)
   - Execute `10_setup_ssh_keys.yaml` to establish passwordless SSH
   - Creates bidirectional SSH access between all baremetal servers

### Phase 3: Cluster Planning
7. **Hardware Detection**
   - With SSH access established, query each server
   - Detect: CPU cores, RAM, disk space, GPU presence
   - Determine which servers can host VMs
   - Store hardware capabilities for planning

8. **VM Planning**
   - Based on hardware capabilities
   - Suggest VM allocation across baremetal servers
   - Allow customization of VM placement
   - Plan VM resources (CPU, RAM, disk)

9. **VM Creation**
   - Execute `30-1_create_base_vms.yaml`
   - Configure VM networking
   - Setup VM users and SSH

### Phase 4: Cluster Configuration
10. **Complete Node List**
    - Show all nodes: baremetal + VMs
    - Display capabilities of each node
    - Ready for role assignment

11. **Role Assignment**
    - Assign Kubernetes roles
    - Control plane nodes (typically VMs)
    - Worker nodes (mix of baremetal and VMs)
    - GPU nodes for AI workloads

12. **Infrastructure Configuration**
    - **Cluster name**: For Kubernetes identification
    - **Domain name**: For DNS and ingress
    - **Cloudflare API Token**: For SSL certificates
    - **ZeroTier Network ID**: For overlay networking
    - **ZeroTier API Token**: For node authorization

### Phase 5: Deployment
13. **Review**
    - Show complete deployment plan
    - List all nodes with roles
    - Display configuration settings
    - Confirm before proceeding

14. **Deploy**
    - Execute ansible playbooks in order
    - Show real-time progress
    - Handle errors gracefully

15. **Complete**
    - Show access information
    - Display service URLs
    - Provide next steps

## Key Principles

1. **Progressive Disclosure**: Only ask for information when needed
2. **Dependency Order**: Each step enables the next
3. **Hardware First**: Can't plan VMs without knowing capabilities
4. **SSH Before Detection**: Need access before querying servers
5. **Complete List Before Roles**: Must have all nodes before assigning roles

## Configuration Timing

- **Early (Phase 1-2)**: Only what's needed for discovery and access
- **Middle (Phase 3)**: Hardware-dependent decisions
- **Late (Phase 4)**: Cluster-wide configuration after all nodes known
- **Never duplicate**: Don't ask for same info twice (e.g., sudo password)

## Next Steps

1. Reorganize Vue components to match this flow
2. Update router to enforce correct sequence
3. Modify Configuration.vue to appear at the right time
4. Split NodeConfiguration into multiple focused components
5. Add missing SSH setup step
6. Add hardware detection step
7. Add VM planning interface

## Environment Variables Needed

From examining the playbooks:
- `ZEROTIER_NETWORK_ID`: ZeroTier network to join
- `ZEROTIER_API_TOKEN`: For authorizing nodes
- `CLOUDFLARE_API_TOKEN`: For cert-manager
- `ADMIN_PASSWORD`: For MicroK8s services (collected later)
- `GITHUB_TOKEN`: For private repos (optional)

## Notes

- SSH credentials should be homogeneous across all baremetal servers
- VMs inherit credentials from their host systems
- Admin username/password for services collected during MicroK8s setup, not initial config
- Domain must be valid for Let's Encrypt certificates