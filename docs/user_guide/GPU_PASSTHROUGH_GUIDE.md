# GPU Passthrough Configuration Guide

This guide explains how to configure GPU passthrough in Thinkube for virtual machines. It covers the inventory configuration, hardware requirements, IOMMU group compatibility, and troubleshooting tips.

## Table of Contents

- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [IOMMU Group Compatibility](#iommu-group-compatibility)
  - [Identifying IOMMU Groups](#identifying-iommu-groups)
  - [GPUs That Cannot Be Used](#gpus-that-cannot-be-used)
- [Inventory Configuration](#inventory-configuration)
  - [Basic Configuration](#basic-configuration)
  - [Mixed GPU Configuration](#mixed-gpu-configuration)
  - [Multiple VMs Sharing GPUs](#multiple-vms-sharing-gpus)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Advanced Configurations](#advanced-configurations)

## Overview

GPU passthrough allows a virtual machine to directly access a physical GPU, providing near-native performance for graphics-intensive workloads. Thinkube's implementation supports:

- Standard GPU passthrough (dedicating GPUs to VMs)
- Mixed configurations (some GPUs for VMs, some for host)
- Selective binding of specific PCI slots
- NVIDIA and AMD GPUs

## Hardware Requirements

Before configuring GPU passthrough, ensure your hardware meets these requirements:

1. **CPU with IOMMU support**:
   - Intel: VT-d support
   - AMD: AMD-Vi support

2. **Compatible motherboard**:
   - PCIe slots that support proper IOMMU grouping
   - BIOS/UEFI with IOMMU support enabled

3. **GPUs**:
   - Any modern NVIDIA or AMD GPU
   - For mixed setups (like bcn1), you need:
     - Multiple GPUs OR
     - A CPU with integrated graphics

4. **BIOS/UEFI Configuration**:
   - Enable CPU virtualization (VT-x/AMD-V)
   - Enable IOMMU (VT-d/AMD-Vi)
   - Some motherboards have options to improve IOMMU grouping

## IOMMU Group Compatibility

### Identifying IOMMU Groups

IOMMU (Input-Output Memory Management Unit) groups are critical for GPU passthrough. Devices in the same IOMMU group must be passed through together or not at all. This is a hardware-level limitation that cannot be easily changed.

To identify IOMMU groups on your system:

```bash
# List all IOMMU groups
./scripts/run_ssh_command.sh your_host "find /sys/kernel/iommu_groups/ -type l | sort -V | xargs -l basename -a | sort -n"

# View devices in a specific group (e.g., group 14)
./scripts/run_ssh_command.sh your_host "for dev in \$(ls /sys/kernel/iommu_groups/14/devices/); do echo -n \"\$dev \"; lspci -nns \$dev; done"
```

### GPUs That Cannot Be Used

**IMPORTANT**: Not all GPUs can be used for passthrough. A GPU **cannot** be used for passthrough if:

1. **It shares an IOMMU group with critical system devices**, such as:
   - Root ports or PCIe bridges that connect to essential components
   - Host CPU-integrated devices (e.g., SATA controllers, USB controllers)
   - Primary network interfaces
   - Platform controllers

2. **It's the only GPU in a desktop system** without alternative graphics (like integrated GPU)

3. **It's currently used by the host OS** for display output (unless you have a headless setup)

Example of an incompatible scenario:
```
IOMMU Group 1:
00:01.0 PCI bridge: Intel Corporation 6th-10th Gen Core Processor PCIe Controller (x16) [8086:1901]
01:00.0 VGA compatible controller: NVIDIA Corporation TU102 [GeForce RTX 2080 Ti] [10de:1e04]
01:00.1 Audio device: NVIDIA Corporation TU102 High Definition Audio Controller [10de:10f7]
01:00.2 USB controller: NVIDIA Corporation Device [10de:1ad6]
01:00.3 Serial bus controller [0c80]: NVIDIA Corporation Device [10de:1ad7]
```

In this example, the GPU (01:00.0) shares an IOMMU group with a PCI bridge (00:01.0), making it unsuitable for passthrough.

Example of a compatible scenario:
```
IOMMU Group 14:
07:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090] [10de:2204]
07:00.1 Audio device: NVIDIA Corporation GA102 High Definition Audio Controller [10de:1aef]
```

Here, the GPU (07:00.0) is in its own IOMMU group with only its audio device, making it ideal for passthrough.

## Inventory Configuration

### Basic Configuration

To enable GPU passthrough for a VM in your inventory, add these settings to your VM host in `inventory/inventory.yaml`:

```yaml
tkc:  # Example VM host name
  parent_host: bcn1  # The physical host where the VM will run
  memory: 32GB
  cpu_cores: 8
  gpu_passthrough: true  # Enable GPU passthrough
  gpu_type: "RTX 3090"   # Document the GPU model (informational)
  pci_slot: "01:00.0"    # Specify the exact PCI slot of the GPU
```

### Mixed GPU Configuration

For hosts with multiple identical GPUs where you want to keep some for the host OS:

```yaml
# Physical host configuration
bcn1:
  configure_gpu_passthrough: true
  server_type: desktop      # 'desktop' or 'headless'

# VM configuration that will use the GPU
tkc:
  parent_host: bcn1
  gpu_passthrough: true
  gpu_type: "RTX 3090"
  pci_slot: "01:00.0"       # Specific PCI slot to bind to vfio-pci
```

### Multiple VMs Sharing GPUs

To configure multiple VMs to use different GPUs from the same host:

```yaml
# First VM with GPU passthrough
tkc:
  parent_host: bcn1
  gpu_passthrough: true
  gpu_type: "RTX 3090"
  pci_slot: "01:00.0"       # First GPU

# Second VM with GPU passthrough
tkw1:
  parent_host: bcn1
  gpu_passthrough: true
  gpu_type: "RTX 3090"
  pci_slot: "08:00.0"       # Second GPU
```

## Verification

Verify GPU passthrough in two phases:

### 1. Host GPU Binding Verification

```bash
# Run the host test playbook
./scripts/run_ansible.sh ansible/00_initial_setup/38_test_gpu_reservation.yaml

# Check specific host
./scripts/run_ansible.sh ansible/00_initial_setup/38_test_gpu_reservation.yaml -l bcn1

# Manual verification
./scripts/run_ssh_command.sh bcn1 "lspci -nnk | grep -A3 NVIDIA"
./scripts/run_ssh_command.sh bcn1 "systemctl status vfio-bind*"
```

The host test playbook will:
1. Verify IOMMU is enabled
2. Check if the correct GPUs are bound to vfio-pci
3. Verify GPU configuration matches inventory settings
4. Report detailed status for troubleshooting

### 2. VM GPU Functionality Verification

```bash
# Run the VM test playbook 
./scripts/run_ansible.sh ansible/20_lxd_setup/68_test_vm_gpu_passthrough.yaml

# Manual verification
./scripts/run_ssh_command.sh tkw1 "nvidia-smi"  # Check GPU status
./scripts/run_ssh_command.sh tkw1 "nvcc --version" # Check CUDA compiler
```

The VM test playbook will:
1. Check that GPUs are visible in the VM
2. Verify NVIDIA drivers are loaded and functioning
3. Test CUDA functionality
4. Run a basic GPU test

Note that the GPU must be properly bound to vfio-pci on the host AND have working drivers in the VM to function correctly.

## Troubleshooting

### VM Does Not See GPU After Configuration

If the GPU is properly bound to vfio-pci on the host but not visible in the VM:

1. **Check the LXD device configuration**:
   ```bash
   lxc config device show vm-name
   ```
   Look for devices with type "pci" that match your GPU and its audio component.

2. **Verify the correct PCI address format**:
   ```yaml
   # INCORRECT (old format):
   lxc config device add vm-name gpu gpu pci=01:00.0
   
   # CORRECT (new format):
   lxc config device add vm-name gpu pci address=01:00.0
   ```
   The syntax changed in newer LXD versions.

3. **Audio device missing**:
   ```bash
   # Check if both GPU and audio devices are bound to vfio-pci
   lspci -nnk | grep -A3 "NVIDIA"
   ```
   Ensure both the GPU (e.g., 01:00.0) and its audio component (e.g., 01:00.1) show "Kernel driver in use: vfio-pci".
   
4. **Restart the VM**:
   ```bash
   lxc stop vm-name --force
   lxc start vm-name
   ```
   Sometimes a clean restart is needed after configuration changes.

### NVIDIA Drivers Not Working in VM

If the GPU is visible in the VM but nvidia-smi fails:

1. **Clean existing packages**:
   ```bash
   # Inside the VM
   apt purge -y 'nvidia*' 'libnvidia*'
   apt autoremove -y
   apt update
   ```

2. **Install the correct driver version**:
   ```bash
   # Use the exact same version as the host
   apt install -y nvidia-driver-570-server nvidia-utils-570-server
   ```

3. **Check for module loading**:
   ```bash
   lsmod | grep nvidia
   ```
   If no modules are loaded, try `modprobe nvidia`.

4. **Ubuntu 24.04 (Noble) PPA issues**:
   For Ubuntu 24.04 VMs, the graphics-drivers PPA may have configuration conflicts. Try:
   ```bash
   # Remove any conflicting PPA files
   rm -f /etc/apt/sources.list.d/*graphics-drivers*
   
   # Use the standard repositories
   apt update
   apt install -y nvidia-driver-570-server
   ```

### IOMMU Group Issues

The most common and challenging issues with GPU passthrough involve IOMMU groups:

1. **Checking IOMMU Group Isolation**:
   ```bash
   # Display all IOMMU groups with devices
   ./scripts/run_ssh_command.sh your_host "for g in \$(find /sys/kernel/iommu_groups/* -maxdepth 0 -type d | sort -V); do echo \"IOMMU Group \$(basename \$g):\"; for d in \$g/devices/*; do echo -e \"\\t\$(lspci -nns \$(basename \$d))\"; done; done"
   ```

2. **Diagnosing IOMMU Group Problems**:
   - If your GPU shares an IOMMU group with system-critical devices:
     - You cannot use this GPU for passthrough
     - Consider using a different PCIe slot for the GPU
     - Try a different motherboard with better IOMMU support

3. **Solutions for IOMMU Group Limitations**:
   - Move the GPU to a different PCIe slot that has better IOMMU isolation
   - Use a different GPU that has better IOMMU grouping
   - Consider a motherboard designed for virtualization with better IOMMU grouping
   - Hardware limitations cannot be overcome with software workarounds

### IOMMU Not Enabled

If the test playbook shows "IOMMU not enabled":

1. Check BIOS/UEFI settings:
   ```bash
   # Verify kernel command line parameters
   ./scripts/run_ssh_command.sh your_host "cat /proc/cmdline"
   ```

2. Ensure these parameters are present:
   - Intel systems: `intel_iommu=on`
   - AMD systems: `amd_iommu=on`
   - Additional helpful settings: `iommu=pt`

3. Update GRUB configuration if needed:
   ```bash
   # Edit GRUB configuration
   ./scripts/run_ssh_command.sh your_host "sudo nano /etc/default/grub"
   
   # Update GRUB
   ./scripts/run_ssh_command.sh your_host "sudo update-grub"
   
   # Reboot the system
   ./scripts/run_ssh_command.sh your_host "sudo reboot"
   ```

### GPU Not Bound to vfio-pci

If the GPU is not properly bound to vfio-pci:

1. Check current binding:
   ```bash
   ./scripts/run_ssh_command.sh your_host "lspci -nnk | grep -A3 NVIDIA"
   ```

2. Verify vfio-pci module is loaded:
   ```bash
   ./scripts/run_ssh_command.sh your_host "lsmod | grep vfio"
   ```

3. For systems with systemd service binding:
   ```bash
   ./scripts/run_ssh_command.sh your_host "systemctl status vfio-bind*"
   ```

## Advanced Configurations

### Mixed GPU Setup with Identical GPUs

For systems with multiple identical GPUs where one needs to be passed through while keeping others for the host (like bcn1):

1. Use the built-in systemd service approach, which selectively binds specific PCI slots:
   ```yaml
   # In inventory/inventory.yaml
   bcn1:
     configure_gpu_passthrough: true
     server_type: desktop
   
   tkc:
     parent_host: bcn1
     gpu_passthrough: true
     gpu_type: "RTX 3090"
     pci_slot: "01:00.0"  # Specific PCI slot
   ```

2. This creates a systemd service that binds only the specified PCI slot to vfio-pci

### GPU and Audio Device Handling

For NVIDIA GPUs, both the primary GPU device and its audio component must be properly passed through:

1. The audio component of a GPU (for example, PCI 01:00.1) is critical for passthrough
2. Both the GPU and its audio component must be bound to vfio-pci
3. Thinkube uses two approaches for handling this:
   - **Primary GPU Binding**: Using vfio-bind.sh to bind the main GPU device
   - **Audio Device Binding**: Using vfio-bind-audio.sh and udev rules to handle audio components

4. Example of proper PCI device attachment in a VM:
   ```bash
   # Add the GPU device
   lxc config device add vm-name gpu pci address=01:00.0  # Main GPU
   
   # Add the associated audio device from the same IOMMU group
   lxc config device add vm-name gpu-audio pci address=01:00.1  # GPU audio component
   ```

### Creating Custom vfio-bind Scripts

For advanced custom configurations:

1. Create a script at `/usr/local/bin/vfio-bind-custom.sh`:
   ```bash
   #!/bin/bash
   set -x
   
   # Load modules
   modprobe vfio
   modprobe vfio_pci
   modprobe vfio_iommu_type1
   
   # Unbind specific device
   echo "0000:01:00.0" > /sys/bus/pci/devices/0000:01:00.0/driver/unbind
   
   # Set driver override
   echo "vfio-pci" > /sys/bus/pci/devices/0000:01:00.0/driver_override
   
   # Bind to vfio-pci
   echo "0000:01:00.0" > /sys/bus/pci/drivers/vfio-pci/bind
   ```

2. Make it executable:
   ```bash
   chmod +x /usr/local/bin/vfio-bind-custom.sh
   ```

3. Create a systemd service to run it at boot.

---

By following this guide, you should be able to successfully identify compatible GPUs and configure GPU passthrough for your VMs in Thinkube. Remember that hardware limitations with IOMMU groups cannot be overcome with software workarounds - you need compatible hardware for GPU passthrough to work properly.

For further assistance, refer to the implementation details in the Ansible playbooks or consult the project maintainers.