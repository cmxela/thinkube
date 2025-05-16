# 20 LXD Setup

## Overview

The LXD Setup component configures LXD on the baremetal servers, creates VM profiles, and deploys VMs for MicroK8s. This component is responsible for preparing the virtualization environment that will host the Kubernetes cluster.

## Playbooks

### 00_cleanup.yaml
- **Purpose**: Cleans up existing LXD VMs and configurations for a fresh deployment
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - LXD installed on all servers
- **Required Variables**:
  - None (uses inventory host definitions)
- **Outputs**: 
  - Old VMs removed
  - Old profiles removed
  - System ready for fresh deployment
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/00_cleanup.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 10_setup_lxd_cluster.yaml
- **Purpose**: Initializes LXD and configures clustering between nodes
- **Target Hosts**: `baremetal` (all physical servers)
- **Prerequisites**: 
  - Network bridge configured
  - System dependencies installed
- **Required Variables**:
  - `lxd_storage_pool`: Storage pool name from inventory
  - `lxd_storage_size`: Size of storage pool from inventory
- **Optional Variables**:
  - `lxd_network_name`: Name of LXD network bridge (default: "lxdbr0")
  - `lxd_network_cidr`: CIDR for LXD network (default: "192.168.100.0/24")
- **Outputs**: 
  - LXD initialized on all servers
  - Storage pools configured
  - Network bridges created
  - Clustering configured (if multiple servers)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/10_setup_lxd_cluster.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 20_setup_lxd_profiles.yaml
- **Purpose**: Creates VM profiles for MicroK8s nodes
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - LXD cluster set up by 10_setup_lxd_cluster.yaml
- **Required Variables**:
  - None (uses inventory to determine profiles to create)
- **Optional Variables**:
  - None (all configuration taken from inventory)
- **Outputs**: 
  - VM profiles created based on inventory definitions
  - Profiles properly configured for VM creation
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/20_setup_lxd_profiles.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 30_create_vms.yaml
- **Purpose**: Creates VMs for MicroK8s deployment
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - LXD profiles created by 20_setup_lxd_profiles.yaml
- **Required Variables**:
  - VM definitions in inventory (memory, cpu_cores, disk_size, parent_host, etc.)
  - `domain_name`: Domain name for VM FQDNs
  - `system_username`: System user to create on VMs
- **Optional Variables**:
  - `lxd_image`: VM image to use (default: "ubuntu:24.04")
  - `dns_servers`: List of DNS servers for VMs (default: "8.8.8.8, 8.8.4.4")
- **Outputs**: 
  - VMs created with names and resources as defined in inventory
  - Network interfaces configured according to inventory
  - VMs running and ready for further configuration
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/30_create_vms.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 40_configure_vm_ssh.yaml
- **Purpose**: Configures SSH key-based access to VMs from management node
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**: 
  - VMs created by 30_create_vms.yaml
  - System user created on VMs with sudo access
  - VMs accessible via IP
- **Required Variables**:
  - `system_username`: System user on VMs (from inventory)
  - VM definitions in inventory (hostnames and IP addresses)
- **Optional Variables**:
  - `ssh_key_name`: SSH key to use (default: "thinkube_cluster_key")
  - `ssh_key_type`: Type of key to generate (default: "rsa")
  - `ssh_key_bits`: Key size in bits (default: 4096)
- **Outputs**: 
  - SSH keys generated if not already present
  - SSH keys copied to VMs for password-less access
  - SSH config updated for direct VM access
  - SSH agent configured for forwarding
- **Implementation Details**:
  - Generates SSH keypair on management node if not present
  - Sets proper permissions on key files
  - Distributes public key to all VMs
  - Updates SSH config for easy VM access
  - Tests SSH connectivity to confirm setup
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/40_configure_vm_ssh.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 50_configure_gpu_passthrough.yaml
- **Purpose**: Configures GPU passthrough for AI workloads
- **Target Hosts**: `baremetal` with GPU devices and `management`
- **Prerequisites**: 
  - VMs created by 30_create_vms.yaml
  - NVIDIA GPU drivers installed on host
  - IOMMU enabled in BIOS and kernel
- **Required Variables**:
  - `gpu_passthrough_containers`: Group in inventory listing VMs requiring GPU access
  - `gpu_device_ids`: PCI IDs of GPU devices to pass through
- **Optional Variables**:
  - `nvidia_driver_version`: Version of NVIDIA driver to install in VMs
- **Outputs**: 
  - Host configured for GPU passthrough
  - VM profiles updated with GPU device assignment
  - NVIDIA drivers installed in VMs
  - VMs ready for GPU workloads
- **Implementation Details**:
  - Configures host kernel parameters for PCI passthrough
  - Updates LXD profiles to include GPU device
  - Installs NVIDIA drivers in target VMs
  - Tests GPU detection and functionality
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/50_configure_gpu_passthrough.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 60_configure_dns_server.yaml
- **Purpose**: Configures the DNS VM (dns1) with proper DNS server setup
- **Target Hosts**: `management`
- **Prerequisites**: 
  - VMs created by 30_create_vms.yaml
  - SSH access configured by 40_configure_vm_ssh.yaml
  - DNS VM (dns1) running and accessible
- **Required Variables**:
  - `domain_name`: Primary domain for the cluster
  - `dns1_ip`: IP address of the DNS server VM
  - `dns_forwarders`: List of upstream DNS servers
- **Optional Variables**:
  - `dns_allow_query`: Networks allowed to query (default: any)
  - `dns_allow_recursion`: Networks allowed recursion (default: local networks)
- **Outputs**: 
  - Bind9 DNS server installed and configured in the DNS VM
  - Forward and reverse zones set up for the domain
  - DNS records created for cluster nodes and services
  - DNS functioning for both internal and external names
- **Implementation Details**:
  - Installs Bind9 DNS server on the DNS VM
  - Configures zones for primary domain
  - Sets up reverse lookup zones
  - Creates DNS records for all cluster nodes
  - Sets up forwarding for external domains
  - Configures security and performance settings
  - Tests DNS resolution
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/60_configure_dns_server.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 38_test_vm_creation.yaml
- **Purpose**: Tests VM creation and configuration
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**:
  - VMs created by 30_create_vms.yaml
- **Required Variables**:
  - VM definitions in inventory (for validation)
  - `system_username`: System user on VMs
- **What it Tests**:
  - VM existence and running state
  - Resource allocation matches inventory
  - Network interfaces are correctly configured
  - User configuration is correct
  - Network connectivity works
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/38_test_vm_creation.yaml
  ```

### 39_rollback_vm_creation.yaml
- **Purpose**: Removes VMs if needed
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **When to Use**:
  - When troubleshooting VM issues
  - When needing to reconfigure VMs
- **Required Variables**:
  - VM definitions in inventory (used to determine which VMs to remove)
- **What it Removes**:
  - VMs specified in inventory
  - SSH configuration for VMs
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/39_rollback_vm_creation.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

### 28_test_lxd_profiles.yaml
- **Purpose**: Tests LXD profile creation and configuration
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **Prerequisites**:
  - LXD profiles created by 20_setup_lxd_profiles.yaml
- **Required Variables**:
  - None (uses inventory to determine profiles to check)
- **What it Tests**:
  - Profile existence
  - Profile settings match requirements
  - Resource limits correctly configured
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/28_test_lxd_profiles.yaml
  ```

### 29_rollback_lxd_profiles.yaml
- **Purpose**: Removes LXD profiles if needed
- **Target Hosts**: `management` (Ansible controller node defined in inventory)
- **When to Use**:
  - When troubleshooting profile issues
  - When needing to reconfigure profiles
- **Required Variables**:
  - None (uses predefined list of profiles)
- **What it Removes**:
  - LXD profiles (container, vm-base, vm-networks, gpu-passthrough)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/29_rollback_lxd_profiles.yaml -e "ansible_become_pass=$ANSIBLE_SUDO_PASS"
  ```

## Implementation Specifications

### SSH Key-Based Access Configuration (40_configure_vm_ssh.yaml)

SSH key-based access is critical for secure and automated access to VMs. The playbook should implement the following:

1. **SSH Key Generation**:
   ```yaml
   - name: Generate SSH key if not present
     ansible.builtin.user:
       name: "{{ ansible_user }}"
       generate_ssh_key: yes
       ssh_key_bits: 4096
       ssh_key_type: rsa
     register: ssh_key_generation
   ```

2. **Public Key Copy**:
   ```yaml
   - name: Copy SSH public key to VMs
     ansible.builtin.shell: |
       cat ~/.ssh/id_rsa.pub | lxc exec {{ vm_name }} -- bash -c "
       mkdir -p /home/{{ system_username }}/.ssh
       cat >> /home/{{ system_username }}/.ssh/authorized_keys
       chown -R {{ system_username }}:{{ system_username }} /home/{{ system_username }}/.ssh
       chmod 700 /home/{{ system_username }}/.ssh
       chmod 600 /home/{{ system_username }}/.ssh/authorized_keys"
     loop: "{{ groups['lxd_containers'] }}"
     loop_control:
       loop_var: vm_name
   ```

3. **SSH Config Setup**:
   ```yaml
   - name: Create SSH config for VMs
     ansible.builtin.template:
       src: ssh_config.j2
       dest: "~/.ssh/config"
       backup: yes
       mode: '0600'
   ```

4. **Template Content** (ssh_config.j2):
   ```
   # Thinkube VM SSH Configuration
   # Managed by Ansible - DO NOT EDIT MANUALLY

   {% for vm in groups['lxd_containers'] %}
   Host {{ vm }}
     HostName {{ hostvars[vm]['lan_ip'] }}
     User {{ system_username }}
     StrictHostKeyChecking no
     UserKnownHostsFile /dev/null
     IdentityFile ~/.ssh/id_rsa
     ForwardAgent yes
   {% endfor %}
   ```

5. **SSH Connectivity Test**:
   ```yaml
   - name: Test SSH connectivity to VMs
     ansible.builtin.command: ssh -o BatchMode=yes -o ConnectTimeout=5 {{ vm_name }} echo "SSH connection successful"
     register: ssh_test
     changed_when: false
     failed_when: ssh_test.rc != 0
     loop: "{{ groups['lxd_containers'] }}"
     loop_control:
       loop_var: vm_name
   ```

### GPU Passthrough Configuration (50_configure_gpu_passthrough.yaml)

GPU passthrough is essential for AI workloads. The playbook should implement:

1. **Host-Side Configuration**:
   ```yaml
   - name: Enable IOMMU in kernel parameters
     ansible.builtin.lineinfile:
       path: /etc/default/grub
       regexp: '^GRUB_CMDLINE_LINUX_DEFAULT="(.*)"'
       line: 'GRUB_CMDLINE_LINUX_DEFAULT="\1 intel_iommu=on iommu=pt"'
       backrefs: yes
     register: grub_updated
     become: true
     
   - name: Update GRUB if configuration changed
     ansible.builtin.command: update-grub
     become: true
     when: grub_updated.changed
   ```

2. **LXD Profile Configuration**:
   ```yaml
   - name: Configure GPU passthrough profile
     ansible.builtin.command: >
       lxc profile device add gpu-passthrough gpu gpu
       vendorid={{ gpu_vendor_id }}
     become: true
   ```

3. **VM-Side Installation**:
   ```yaml
   - name: Install NVIDIA drivers in GPU VMs
     ansible.builtin.shell: |
       lxc exec {{ vm_name }} -- bash -c "
       apt-get update && 
       apt-get install -y nvidia-driver-{{ nvidia_driver_version }} nvidia-utils-{{ nvidia_driver_version }} cuda-drivers"
     loop: "{{ groups['gpu_passthrough_containers'] | default([]) }}"
     loop_control:
       loop_var: vm_name
     when: groups['gpu_passthrough_containers'] is defined and groups['gpu_passthrough_containers'] | length > 0
   ```

4. **GPU Testing**:
   ```yaml
   - name: Test GPU detection in VMs
     ansible.builtin.command: lxc exec {{ vm_name }} -- nvidia-smi
     register: gpu_test
     changed_when: false
     loop: "{{ groups['gpu_passthrough_containers'] | default([]) }}"
     loop_control:
       loop_var: vm_name
     when: groups['gpu_passthrough_containers'] is defined and groups['gpu_passthrough_containers'] | length > 0
   ```

### DNS Server Configuration (60_configure_dns_server.yaml)

A properly configured DNS server is critical for the cluster. The playbook should:

1. **Install DNS Server**:
   ```yaml
   - name: Install Bind9 DNS server
     ansible.builtin.apt:
       name:
         - bind9
         - bind9-utils
         - dnsutils
       state: present
       update_cache: yes
     become: true
     delegate_to: dns1
   ```

2. **Configure Named Options**:
   ```yaml
   - name: Configure named.conf.options
     ansible.builtin.template:
       src: templates/named.conf.options.j2
       dest: /etc/bind/named.conf.options
       mode: '0644'
       owner: bind
       group: bind
     become: true
     delegate_to: dns1
   ```

3. **Configure Zones**:
   ```yaml
   - name: Configure named.conf.local
     ansible.builtin.template:
       src: templates/named.conf.local.j2
       dest: /etc/bind/named.conf.local
       mode: '0644'
       owner: bind
       group: bind
     become: true
     delegate_to: dns1
   ```

4. **Create Zone Files**:
   ```yaml
   - name: Create forward zone file
     ansible.builtin.template:
       src: templates/db.domain.j2
       dest: "/etc/bind/db.{{ domain_name }}"
       mode: '0644'
       owner: bind
       group: bind
     become: true
     delegate_to: dns1
   ```

5. **Configure Reverse Zone**:
   ```yaml
   - name: Create reverse zone file
     ansible.builtin.template:
       src: templates/db.reverse.j2
       dest: "/etc/bind/db.{{ reverse_zone }}"
       mode: '0644'
       owner: bind
       group: bind
     become: true
     delegate_to: dns1
   ```

6. **Restart DNS Service**:
   ```yaml
   - name: Restart Bind9 service
     ansible.builtin.systemd:
       name: bind9
       state: restarted
       enabled: yes
     become: true
     delegate_to: dns1
   ```

7. **Test DNS Resolution**:
   ```yaml
   - name: Test DNS resolution
     ansible.builtin.command: "dig @{{ dns1_ip }} {{ item }}.{{ domain_name }}"
     register: dns_test
     changed_when: false
     failed_when: dns_test.rc != 0
     loop: "{{ groups['lxd_containers'] }}"
     delegate_to: dns1
   ```

## Playbook Execution Sequence

For complete LXD setup, execute playbooks in this order:

1. **Reset/Cleanup** (if needed):
   ```bash
   ./scripts/run_ansible.sh ansible/20_lxd_setup/29_rollback_lxd_profiles.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/39_rollback_vm_creation.yaml
   ```

2. **LXD Cluster Setup**:
   ```bash
   ./scripts/run_ansible.sh ansible/20_lxd_setup/10_setup_lxd_cluster.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/18_test_lxd_cluster.yaml
   ```

3. **LXD Profiles**:
   ```bash
   ./scripts/run_ansible.sh ansible/20_lxd_setup/20_setup_lxd_profiles.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/28_test_lxd_profiles.yaml
   ```

4. **VM Creation**:
   ```bash
   ./scripts/run_ansible.sh ansible/20_lxd_setup/30_create_vms.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/38_test_vm_creation.yaml
   ```

5. **VM Configuration**:
   ```bash
   ./scripts/run_ansible.sh ansible/20_lxd_setup/40_configure_vm_ssh.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/50_configure_gpu_passthrough.yaml
   ./scripts/run_ansible.sh ansible/20_lxd_setup/60_configure_dns_server.yaml
   ```

## Dependencies

- Initial setup completed (00_initial_setup)
- Baremetal infrastructure configured (10_baremetal_infra)
- LXD installed on all servers
- Network bridges configured

## Common Issues and Troubleshooting

- **LXD Initialization Failures**:
  - Check storage space with `df -h`
  - Verify LXD version with `lxd --version`
  - Check LXD service status with `systemctl status lxd`

- **VM Creation Issues**:
  - Verify profile existence with `lxc profile list`
  - Check VM logs with `lxc console <vm_name>`
  - Verify network settings with `lxc network list`

- **SSH Access Problems**:
  - Check VM IP address with `lxc list`
  - Verify SSH key permissions
  - Check SSH configuration in `~/.ssh/config`
  - Verify user exists in VM with `lxc exec <vm_name> -- getent passwd <username>`

- **GPU Passthrough Issues**:
  - Verify IOMMU is enabled in BIOS and kernel
  - Check GPU device is properly passed through with `lxc config device show <vm_name>`
  - Ensure NVIDIA drivers are compatible with host kernel version
  - Check GPU visibility in VM with `lxc exec <vm_name> -- nvidia-smi`

- **DNS Server Issues**:
  - Check Bind9 service status with `lxc exec dns1 -- systemctl status bind9`
  - Verify zone files with `lxc exec dns1 -- named-checkzone example.com /etc/bind/db.example.com`
  - Test resolution with `lxc exec dns1 -- dig @localhost hostname.example.com`
  - Check logs with `lxc exec dns1 -- journalctl -u bind9`

## Component-Specific Guidelines

- **No Hardcoded Values**: All VM names, IP addresses, resource allocations, and host configurations MUST come from the inventory file
- The inventory file is the single source of truth for all VM configurations
- Playbooks must dynamically use host variables from inventory
- Use inventory groups to determine VM roles (controllers, workers)
- User-defined hostnames in inventory must be respected (no assumptions about naming conventions)
- IP addresses must be taken from inventory variables, never hardcoded
- Parent-child relationships between baremetal servers and VMs are defined in inventory
- All VM resource allocations (CPU, memory, disk) must be taken from inventory