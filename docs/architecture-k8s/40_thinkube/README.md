# 40 Thinkube

## Overview

The Thinkube component deploys and configures MicroK8s Kubernetes cluster and essential services like CoreDNS, Ingress controllers, MetalLB, and cert-manager. This forms the foundation of the Thinkube platform on which all applications will run.

## Playbooks

### 10_setup_microk8s.yaml
- **Purpose**: Installs and configures MicroK8s on control plane node
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - VM created and accessible
  - ZeroTier configured
  - SSH access configured
- **Required Variables**:
  - Control plane node definition in inventory
  - `microk8s_channel`: MicroK8s channel to install (from inventory)
- **Optional Variables**:
  - `microk8s_addons`: List of addons to enable (default set defined in playbook)
- **Outputs**: 
  - MicroK8s installed on control plane
  - Addons enabled
  - Cluster initialized
  - Kubernetes configuration available
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/10_setup_microk8s.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 11_configure_microk8s_addons.yaml
- **Purpose**: Configures additional MicroK8s addons
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s installed by 10_setup_microk8s.yaml
- **Required Variables**:
  - None
- **Optional Variables**:
  - `microk8s_extra_addons`: Additional addons to enable
- **Outputs**: 
  - Additional addons configured
  - Addon settings customized
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/11_configure_microk8s_addons.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 20_join_workers.yaml
- **Purpose**: Joins worker nodes to the MicroK8s cluster
- **Target Hosts**: `microk8s_workers` (worker nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s control plane set up
  - Worker VMs created and accessible
- **Required Variables**:
  - Worker node definitions in inventory
  - Control plane node defined in inventory
- **Optional Variables**:
  - None
- **Outputs**: 
  - Worker nodes joined to cluster
  - Node labels applied based on inventory
  - Cluster status updated
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/20_join_workers.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 21_configure_worker_roles.yaml
- **Purpose**: Configures specific roles and taints for worker nodes
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - Workers joined to cluster
- **Required Variables**:
  - Worker node definitions in inventory (with roles, taints, etc.)
- **Optional Variables**:
  - None
- **Outputs**: 
  - Node roles configured
  - Taints applied as specified
  - Labels applied for workload targeting
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/21_configure_worker_roles.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 30_setup_coredns.yaml
- **Purpose**: Configures CoreDNS for service discovery
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s cluster running
  - DNS server configured
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
  - DNS server IPs from inventory
- **Optional Variables**:
  - Additional forwarding zones
- **Outputs**: 
  - CoreDNS ConfigMap updated
  - Domain forwarding configured
  - Internal service discovery working
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/30_setup_coredns.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 40_setup_ingress.yaml
- **Purpose**: Deploys ingress controllers for external access
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s cluster running
  - MetalLB configured (if using LoadBalancer services)
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
  - Ingress controller configuration from inventory
- **Optional Variables**:
  - TLS settings
  - Custom annotations
- **Outputs**: 
  - Primary ingress controller deployed
  - Secondary ingress controller for Knative (if needed)
  - Default backend configured
  - Ingress classes defined
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/40_setup_ingress.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 50_setup_metallb.yaml
- **Purpose**: Configures MetalLB load balancer for service exposure
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s cluster running
  - Network properly configured
- **Required Variables**:
  - IP address ranges for MetalLB from inventory
- **Optional Variables**:
  - Advanced MetalLB configuration
- **Outputs**: 
  - MetalLB installed and configured
  - IP address pools defined
  - BGP configuration (if applicable)
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/50_setup_metallb.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 60_setup_cert_manager.yaml
- **Purpose**: Deploys cert-manager for SSL certificate management
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**: 
  - MicroK8s cluster running
  - Ingress controller configured
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
  - Email address for Let's Encrypt notifications
- **Optional Variables**:
  - Alternative certificate issuers
  - Custom certificate settings
- **Outputs**: 
  - cert-manager installed
  - ClusterIssuers configured
  - Default certificate challenges set up
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/60_setup_cert_manager.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 18_test_microk8s.yaml
- **Purpose**: Tests MicroK8s functionality
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**:
  - MicroK8s installed
- **Required Variables**:
  - None
- **What it Tests**:
  - Basic cluster functionality
  - Addon status
  - API server accessibility
  - Node status
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/18_test_microk8s.yaml
  ```

### 19_reset_microk8s.yaml
- **Purpose**: Resets MicroK8s installation if needed
- **Target Hosts**: `microk8s` (all MicroK8s nodes defined in inventory)
- **When to Use**:
  - When troubleshooting cluster issues
  - When needing to reinstall MicroK8s
- **Required Variables**:
  - None
- **What it Removes**:
  - MicroK8s installation
  - Cluster configuration
  - Addon settings
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/19_reset_microk8s.yaml -e "ansible_become_pass=$ANSIBLE_BECOME_PASSWORD"
  ```

### 28_test_workers.yaml
- **Purpose**: Tests worker node functionality
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**:
  - Worker nodes joined to cluster
- **Required Variables**:
  - Worker node definitions in inventory (for validation)
- **What it Tests**:
  - Worker node status
  - Pod scheduling on workers
  - Resource availability
  - Node labels and taints
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/28_test_workers.yaml
  ```

### 38_test_coredns.yaml
- **Purpose**: Tests CoreDNS functionality
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**:
  - CoreDNS configured
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
- **What it Tests**:
  - Service discovery within cluster
  - External domain resolution
  - Custom domain forwarding
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/38_test_coredns.yaml
  ```

### 48_test_ingress.yaml
- **Purpose**: Tests ingress controller functionality
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**:
  - Ingress controllers deployed
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
- **What it Tests**:
  - Ingress controller availability
  - Ingress resource processing
  - External access to services
  - TLS termination
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/48_test_ingress.yaml
  ```

### 68_test_certificates.yaml
- **Purpose**: Tests certificate issuance and renewal
- **Target Hosts**: `microk8s_control_plane` (control plane nodes defined in inventory)
- **Prerequisites**:
  - cert-manager deployed
- **Required Variables**:
  - `domain_name`: Primary domain name from inventory
- **What it Tests**:
  - Certificate issuance
  - ClusterIssuer functionality
  - Challenge resolution
  - Certificate validity
- **Run Command**:
  ```bash
  ansible-playbook -i inventory/inventory.yaml ansible/40_thinkube/68_test_certificates.yaml
  ```

## Dependencies

- Initial setup completed (00_initial_setup)
- Baremetal infrastructure configured (10_baremetal_infra)
- LXD setup completed with VMs created (20_lxd_setup)
- Networking configured (30_networking)

## Common Issues and Troubleshooting

- **MicroK8s Installation Issues**:
  - Check snap service with `systemctl status snapd`
  - Verify MicroK8s status with `microk8s status`
  - Check logs with `journalctl -u snap.microk8s.daemon-apiserver`
  - Ensure available disk space with `df -h`

- **Worker Join Problems**:
  - Verify token validity
  - Check network connectivity between nodes
  - Ensure proper DNS resolution
  - Check logs with `journalctl -u snap.microk8s.daemon-kubelet`

- **CoreDNS Issues**:
  - Check CoreDNS pods with `kubectl -n kube-system get pods`
  - Verify ConfigMap with `kubectl -n kube-system get configmap coredns -o yaml`
  - Test resolution from pods with debugging pod
  - Check logs with `kubectl -n kube-system logs -l k8s-app=kube-dns`

- **Ingress Controller Issues**:
  - Verify pods running with `kubectl -n ingress get pods`
  - Check service configuration with `kubectl -n ingress get svc`
  - Verify load balancer IP assignment
  - Test with simple ingress resource

- **Certificate Issues**:
  - Check cert-manager pods with `kubectl get pods -n cert-manager`
  - Verify certificate status with `kubectl get certificates,certificaterequests,challenges`
  - Check issuer configuration with `kubectl get clusterissuers`
  - Review logs with `kubectl logs -n cert-manager -l app=cert-manager`

## Component-Specific Guidelines

- **No Hardcoded Values**: All configuration must come from inventory
- MicroK8s version and channel must be specified in inventory
- Worker nodes are defined in inventory under the microk8s_workers group
- IP addresses for services must be derived from inventory variables
- Domain names must come from inventory, never hardcoded
- Node labels and taints should be defined in inventory
- User-specific email for Let's Encrypt must be defined in inventory
- Rollback procedures must be tested before production use
- Always verify cluster health after making changes