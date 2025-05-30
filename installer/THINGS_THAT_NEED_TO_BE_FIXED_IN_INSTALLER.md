# Things That Need to Be Fixed in Installer

This document tracks issues discovered during manual installation that need to be fixed in the installer.

## 1. ZeroTier API Token Management

**Issue**: The ZeroTier playbook expects the API token to be passed as an environment variable, but the installer collects it and stores it in the inventory.

**Current Behavior**:
- Installer collects `zerotier_api_token` and stores it in inventory
- Playbook expects `ZEROTIER_API_TOKEN` environment variable
- Manual execution requires: `export ZEROTIER_API_TOKEN='<token>'`

**Fix Required**:
- Modify `PlaybookExecutorStream.vue` to pass ZeroTier variables as environment variables
- Add to the playbook execution:
  ```javascript
  if (playbook.name.includes('zerotier')) {
    envVars.ZEROTIER_API_TOKEN = sessionStorage.getItem('zerotier_api_token')
    envVars.ZEROTIER_NETWORK_ID = sessionStorage.getItem('zerotier_network_id')
  }
  ```

## 2. VM Host Resolution (/etc/hosts)

**Issue**: After VMs are created, their hostnames are not added to `/etc/hosts`, causing playbooks to fail with "Could not resolve hostname" errors.

**Current Behavior**:
- VMs are created with IPs but hostnames aren't registered
- Subsequent playbooks fail when trying to connect to VMs by hostname
- Manual fix required: adding entries to `/etc/hosts`

**Fix Required**:
- Add a task after VM creation to update `/etc/hosts` on the management host
- Should add entries like:
  ```
  192.168.1.111   dns1 dns
  192.168.1.112   vm-2
  ```
- Could be added to `30-2_configure_vm_networking.yaml` or as a separate utility playbook

## 3. SSH Config for VMs

**Issue**: The SSH config for VMs is only updated in `30-3_configure_vm_users.yaml`, but some playbooks may need to connect to VMs before this runs.

**Current Behavior**:
- SSH config is updated late in the process
- May cause connection issues for intermediate playbooks

**Fix Required**:
- Consider moving SSH config generation earlier in the process
- Or ensure all VM-related playbooks use IP addresses until SSH config is set up

## 4. GPU Passthrough PCI Slot Format

**Issue**: GPU passthrough requires PCI addresses with "0000:" prefix, but the inventory generator wasn't adding this prefix.

**Status**: Fixed in `inventoryGenerator.js`
- Now correctly adds `pci_slot: "0000:XX:XX.X"` format

## 5. Playbook Execution Order

**Issue**: GPU driver installation was attempted before networking was configured, causing failures due to no internet access.

**Status**: Fixed in `Deploy.vue`
- Moved GPU driver installation to after DNS/networking setup

## 6. Missing Sudo Permissions for ZeroTier CLI

**Issue**: The ZeroTier playbook was missing `become: true` for zerotier-cli commands.

**Status**: Fixed in `10_setup_zerotier.yaml`
- Added `become: true` to all zerotier-cli command tasks

## 7. Inventory Generation Validation

**Issue**: The installer should validate that all required fields are present in the generated inventory.

**Fix Required**:
- Add validation to ensure GPU-enabled VMs have `pci_slot` field
- Validate all required network configuration is present
- Show warnings if configuration seems incomplete

## 8. Environment Variable Standardization

**Issue**: Inconsistent use of environment variables vs inventory variables across playbooks.

**Fix Required**:
- Document which values should be in environment variables vs inventory
- Standardize approach across all playbooks
- Update installer to handle both patterns correctly

## 9. OpenSSH Server Requirement for Packaged App

**Issue**: The installer requires openssh-server to be installed on the machine running the installer to enable Ansible to connect to localhost.

**Current Behavior**:
- If openssh-server is not installed, Ansible cannot connect to localhost
- This affects initial setup playbooks that configure the management host
- Not obvious to users why the installer fails

**Fix Required**:
- Add pre-flight check in the installer to verify openssh-server is installed
- If not installed, either:
  - Show clear error message with installation instructions
  - Offer to install it automatically (requires sudo)
  - Or package openssh-server with the Electron app (complex)
- Add to installer requirements documentation
- Consider adding a setup script that ensures all prerequisites are met

## 10. Dual IP Address Configuration Issue

**Issue**: Following the instructions in README.md results in servers having two IP addresses - one static and one from DHCP.

**Current Behavior**:
- README instructions lead to network configuration with both static and DHCP addresses
- This can cause routing issues and confusion
- Network services may bind to the wrong IP
- SSH may connect to different IPs unpredictably

**Fix Required**:
- Update README.md instructions to ensure only static IP configuration
- Add network configuration validation in the installer
- Provide utility scripts to fix existing dual-IP configurations (already have some in scripts/utilities/)
- Consider adding a network configuration step in the installer that:
  - Detects current network configuration
  - Warns if multiple IPs detected
  - Offers to fix the configuration automatically

**Related Scripts**:
- `scripts/utilities/fix_dual_ip_generic.sh` - Already exists to fix this issue
- `scripts/utilities/remove_secondary_ip.sh` - Removes DHCP addresses
- `scripts/utilities/fix_network_permanently.sh` - Makes network fixes persistent

## 11. Python venv Not Available on Remote Servers

**Issue**: When SSH configuration playbooks run, other servers don't have Python installed in the venv directory, causing playbooks to skip or fail on those hosts.

**Current Behavior**:
- Initial setup assumes Python venv at `/home/thinkube/.venv/bin/python3`
- This venv only exists on the management host where installer runs
- Other servers (bcn2, VMs) don't have this venv
- Playbooks fail or skip tasks on remote hosts due to missing Python interpreter

**Fix Required**:
Create the same Python venv on ALL hosts during initial setup:
- Add a new early-stage playbook (e.g., `05_setup_python_venv.yaml`) that:
  - Runs after SSH keys are configured
  - Creates `/home/thinkube/.venv` on all hosts
  - Installs Python 3.12 in the venv (same version as management host)
  - Installs required Python packages
  - Ensures all hosts have identical Python environment
- This ensures consistency across all nodes
- Prevents version mismatch issues
- Makes debugging easier

**Implementation**:
```yaml
# New playbook: 05_setup_python_venv.yaml
- name: Setup Python venv on all hosts
  hosts: all
  tasks:
    - name: Install python3-venv package
      apt:
        name: python3-venv
        state: present
      become: true
    
    - name: Create venv directory
      file:
        path: /home/thinkube/.venv
        state: directory
        owner: thinkube
        group: thinkube
    
    - name: Create Python venv
      command: python3 -m venv /home/thinkube/.venv
      args:
        creates: /home/thinkube/.venv/bin/python
```

## 12. DNS VM Name Mismatch

**Issue**: The DNS VM is created with name `dns` but the inventory generator references it as `dns1`, causing playbooks to fail.

**Current Behavior**:
- VMPlanning.vue creates VM with name: `dns`
- inventoryGenerator.js puts it in inventory as: `dns1`
- This causes "dns" to appear as both a group and a host
- ZeroTier playbook fails with: `'ansible.vars.hostvars.HostVarsVars object' has no attribute 'zerotier_ip'`

**Fix Required**:
Choose one consistent naming approach:
- Option A: Change VMPlanning.vue line 484 from `name: 'dns'` to `name: 'dns1'`
- Option B: Change inventoryGenerator.js line 309 from `dns1` to `dns`
- Also update all references to match the chosen name

**Recommendation**: Use `dns1` everywhere since it follows the pattern of other VMs (vm-1, vm-2, etc.)

## 13. DNS Zone Template and CoreDNS Use Old Host Names

**Issue**: Multiple DNS-related playbooks reference old host names (tkc, tkw1, dns1) that don't match current inventory.

**Current Behavior**:
- DNS zone template expects: tkc, tkw1, tkw2, dns1
- CoreDNS playbook expects: dns1
- Actual hosts are: vm-2 (control plane), dns, bcn1, bcn2
- CoreDNS setup fails with: `"hostvars['dns1'].zerotier_ip is undefined"`
- DNS setup fails with: `"hostvars['tkc']" is undefined`

**Fix Required**:
- Update the DNS zone template to use dynamic host discovery from inventory groups
- Update CoreDNS playbook to use 'dns' instead of 'dns1'
- Instead of hardcoding hostnames, iterate through microk8s_control_plane and microk8s_workers groups
- Use the actual hostnames from the inventory
- Add missing variables to installer's inventory generator:
  - `zerotier_subnet_prefix`: Extract from zerotier_cidr (e.g., "192.168.191.")
  - `primary_ingress_ip_octet`: Default to "200" (reserved by ZeroTier setup)
  - `secondary_ingress_ip_octet`: Default to "201" (reserved by ZeroTier setup)

**Files to Update**:
- `ansible/40_thinkube/core/infrastructure/coredns/10_deploy.yaml` - Change dns1 to dns
- `ansible/30_networking/templates/db.domain.j2` - Use dynamic host discovery
- `installer/frontend/src/utils/inventoryGenerator.js` - Add missing variables

## 14. DNS VM Name Hardcoded in Infrastructure Playbooks

**Issue**: The VM creation playbook (`30-1_create_base_vms.yaml`) has `dns1` hardcoded, causing mismatch with inventory that expects `dns`.

**Current Behavior**:
- The playbook creates VM with name `dns1` (hardcoded)
- Inventory and other playbooks expect `dns`
- This causes connectivity and reference issues

**Fix Required**:
- Update `30-1_create_base_vms.yaml` to use the hostname from inventory instead of hardcoded `dns1`
- Ensure VM names are always taken from inventory, not hardcoded

## 15. DNS Group Name Conflicts with Host Name

**Issue**: Having a group named `dns` and a host named `dns` causes Ansible warnings and potential variable resolution issues.

**Current Behavior**:
- Ansible shows warning: `[WARNING]: Found both group and host with same name: dns`
- This can cause confusion in variable precedence
- Makes debugging harder when issues arise

**Fix Applied (Manual)**:
- Renamed `dns` group to `dns_servers` in inventory
- Renamed `dns_containers` group to `dns_vms` for clarity

**Fix Required (Installer)**:
- Update inventory generator to use `dns_servers` instead of `dns` for the group
- Update `dns_containers` to `dns_vms` in inventory generator
- Update all playbooks that reference the dns group to use dns_servers
- Any templates that use group membership checks need updating
- This follows better Ansible practices and avoids naming conflicts

## 16. Shell Configuration Must Run Before MicroK8s

**Issue**: The shell configuration playbook (`ansible/misc/00_setup_shells.yml`) must be executed before MicroK8s installation as it sets up the alias system that MicroK8s integrates with.

**Current Behavior**:
- MicroK8s installation creates kubectl and helm aliases that integrate with the Thinkube alias system
- If shells aren't configured first, the alias system doesn't exist
- This causes MicroK8s setup to fail or skip alias configuration
- Users don't get kubectl/helm shortcuts (k, kgp, h, etc.)

**Fix Required**:
- Add `misc/00_setup_shells.yml` to the deployment sequence in the installer
- Run it early in the process, after SSH setup but before any component installation
- Ensure it runs on all nodes (baremetal and VMs)
- Update deployment order in `Deploy.vue` to include shell setup
- Consider making this part of the initial infrastructure setup phase

## 17. Fish Shell Fork Bomb Due to Missing Starship

**Issue**: The shell setup playbook uses `ignore_errors: yes` when Starship installation fails, then configures Fish to use Starship anyway, causing a fork bomb.

**Current Behavior**:
- Starship installation fails (needs sudo) but is ignored due to `ignore_errors: yes`
- Fish configuration is set up to run `starship init fish`
- When Fish starts, it fails to find starship, potentially causing shell crashes and restarts
- This creates thousands of fish processes, consuming all memory
- VMs become unresponsive with 35,000+ fish processes

**Fix Applied**:
- Removed `ignore_errors: yes` from Starship installation
- Added `become: true` to install with proper permissions
- Added verification step to check if Starship actually installed
- Modified Fish config to double-check starship works before using it
- Set `starship_available` fact to control conditional configuration

**Lessons Learned**:
- NEVER use `ignore_errors: yes` without proper error handling
- Always verify external tools exist before configuring shells to use them
- Shell initialization errors can cause catastrophic fork bombs

## 18. Ingress IP Octet Configuration and Validation

**Issue**: The primary and secondary ingress IP octets are hardcoded to 200 and 201, but these should be configurable and validated to ensure they're not already in use.

**Current Behavior**:
- Hardcoded values: primary=200, secondary=201
- No validation that these IPs are free on the ZeroTier network
- ZeroTier setup reserves these IPs but doesn't check if they're already assigned
- Could cause IP conflicts if another device is using these addresses

**Fix Required**:
- Add configuration fields in NetworkConfiguration.vue for:
  - Primary ingress IP octet (default 200)
  - Secondary ingress IP octet (default 201)
- Integrate with the ZeroTier member checking (from issue #13)
- Validate that these IPs are not already assigned in the ZeroTier network
- Show warning if the IPs are in use, similar to the node IP validation
- Update inventory generator to use the configured values instead of hardcoded defaults
- Consider reserving a range (e.g., 200-210) for MetalLB pool configuration

**Benefits**:
- Prevents IP conflicts in the ZeroTier network
- Allows flexibility for different network configurations
- Makes the installer more robust for various deployment scenarios

## 19. Component Deployment Order and Dependencies

**Issue**: The deployment order for all components is critical due to dependencies between services.

**Current Behavior**:
- Ingress deployment tries to create Certificate resources without cert-manager
- PostgreSQL tries to pull images from Harbor before Harbor is deployed
- Harbor requires Keycloak for OIDC authentication
- No clear dependency chain documented

**Dependencies Discovered**:
- Cert-manager must be installed before Ingress (for Certificate resources)
- Keycloak must be installed before Harbor (for OIDC authentication)
- Harbor must be deployed and images mirrored before PostgreSQL (for container images)
- Keycloak uses embedded H2 database in dev mode (no PostgreSQL dependency)

**Fix Applied**:
- Updated documentation with correct order:
  - Infrastructure: MicroK8s → CoreDNS → Cert-manager → Ingress
  - Core Services: Keycloak → Harbor → Mirror Images → PostgreSQL → Others
- Updated DEPLOYMENT_STRUCTURE.md with full dependency chain

**Fix Required (Installer)**:
- Update Deploy.vue to enforce correct deployment order
- Add dependency checking in deployment sequence
- Show clear error if dependencies aren't met
- Consider adding a dependency graph visualization

## 20. GRUB IOMMU Configuration Not Idempotent and Wrong CPU Type

**Issue**: The GRUB configuration playbook has two critical issues:
1. Adding IOMMU parameters multiple times (not idempotent)
2. Using Intel IOMMU parameters on AMD systems

**Current Behavior**:
- Kernel command line shows: `intel_iommu=on iommu=pt` repeated 8 times
- This is WRONG for AMD systems - should be `amd_iommu=on`
- The playbook appends without checking if parameters already exist
- The playbook doesn't detect CPU vendor (AMD vs Intel)

**Fix Required**:
- Update the GPU reservation playbook (`30_reserve_gpus.yaml`) to:
  - Detect CPU vendor using `lscpu` or `/proc/cpuinfo`
  - Use `amd_iommu=on` for AMD CPUs
  - Use `intel_iommu=on` for Intel CPUs
  - Check if IOMMU parameters already exist before adding
  - Use proper regex replacement instead of appending
  - Ensure the playbook is truly idempotent

**Example of the issue on AMD system**:
```
/proc/cmdline: ... intel_iommu=on iommu=pt intel_iommu=on iommu=pt ...  # WRONG!
Should be: ... amd_iommu=on iommu=pt ...  # CORRECT for AMD
```

**Critical**: Using wrong IOMMU parameters can prevent GPU passthrough from working!

## 21. VFIO PCI IDs Configuration Syntax Error

**Issue**: The GPU passthrough configuration generates invalid VFIO PCI IDs with a syntax error that prevents GPU binding.

**Current Behavior**:
- The file `/etc/modprobe.d/vfio-pci-ids.conf` contains:
  ```
  options vfio-pci ids=10de:2204,10de 1aef,10de:1aef
  ```
- Notice the missing colon in `10de 1aef` (should be `10de:1aef`)
- This syntax error prevents vfio-pci from binding to the GPUs
- The GPUs remain bound to nvidia driver instead

**Fix Required**:
- Fix the playbook that generates this configuration (likely in `30_reserve_gpus.yaml`)
- Ensure proper formatting of PCI IDs with colons
- The correct format should be:
  ```
  options vfio-pci ids=10de:2204,10de:1aef
  ```
- Remove duplicate IDs if any

**Impact**: This prevents GPU passthrough from working even when all other configuration is correct.

## Implementation Priority

1. **High Priority**: ZeroTier API token, VM hosts resolution, OpenSSH server check, Dual IP fix, Python venv issue, DNS name mismatch, DNS hardcoded names, DNS group conflict, Shell setup must run before MicroK8s, Fish fork bomb, Ingress IP configuration, Component deployment order, GRUB IOMMU wrong CPU type, VFIO PCI IDs syntax error - These block installation
2. **Medium Priority**: SSH config timing, inventory validation
3. **Low Priority**: Environment variable standardization (works but could be cleaner)