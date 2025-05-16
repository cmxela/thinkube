# GPU Passthrough for LXD VMs: Lessons Learned

This document captures the key lessons learned during the implementation of GPU passthrough for LXD VMs in the Thinkube project. It serves as both a reference for future maintenance and a knowledge base for similar implementations.

## 1. Overview

GPU passthrough enables virtual machines to directly access physical GPUs on the host, providing near-native performance for graphics-intensive applications. In the Thinkube project, we implemented GPU passthrough from baremetal hosts to LXD VMs, with a focus on NVIDIA GPUs.

**Current Implementation Status**:

- **Host GPU Binding**: Working correctly on all systems
  - bcn1: Mixed RTX 3090 setup with selective PCI binding
  - bcn2: GTX 1080Ti bound to vfio-pci

- **VM GPU Passthrough**: Working correctly for all target VMs
  - tkw1: Running on bcn1 with RTX 3090 GPU
  - tkc: Running on bcn2 with GTX 1080Ti GPU

- **GPU Driver Installation**: Successfully implemented
  - Both VMs have NVIDIA drivers and CUDA support
  - Confirmed working with `nvidia-smi` and `nvcc --version`

## 2. Prerequisites

Successful GPU passthrough requires several prerequisites at the host level:

1. **IOMMU Support**:
   - CPU must support IOMMU (Intel VT-d or AMD-Vi)
   - IOMMU must be enabled in BIOS/UEFI
   - Kernel parameters must include `intel_iommu=on` or `amd_iommu=on` and `iommu=pt`

2. **GPU Reservation**:
   - GPUs must be bound to the VFIO-PCI driver using `00_initial_setup/30_reserve_gpus.yaml`
   - System must be rebooted after GPU reservation
   - VFIO-PCI modules must be loaded at boot

3. **Multiple GPU Configurations**:
   - For desktop systems, at least one GPU must remain available for the host OS
   - For headless servers, a single GPU can be fully passed through
   - Specific PCI slots must be identified for systems with identical GPUs

## 3. Modular Design Pattern

We applied a modular design pattern to GPU passthrough, which improved maintainability and reliability:

1. **Setup Playbook (60_configure_vm_gpu_passthrough.yaml)**:
   - Validates prerequisites (VFIO binding, etc.)
   - Sets up NVIDIA drivers on the host
   - Processes VMs sequentially using include_tasks pattern
   - Configures GPU devices in LXD VMs
   - Installs matching NVIDIA drivers in VMs

2. **Task File (configure_vm_gpu.yaml)**:
   - Contains all tasks for configuring a single VM
   - Validates VM-specific prerequisites
   - Handles PCI slot assignment and IOMMU group devices
   - Configures GPU devices in LXD
   - Installs NVIDIA packages in the VM

3. **Test Playbook (68_test_vm_gpu_passthrough.yaml)**:
   - Tests GPU visibility inside VMs
   - Verifies NVIDIA driver and CUDA functionality
   - Runs basic GPU stress tests
   - Provides detailed diagnostic information

4. **Rollback Playbook (69_rollback_vm_gpu_passthrough.yaml)**:
   - Removes GPU devices from VMs
   - Uninstalls NVIDIA drivers from VMs
   - Restores VMs to their pre-GPU-passthrough state

## 4. Key Implementation Challenges

### 4.1 IOMMU Group Handling

**Challenge**: All devices in the same IOMMU group must be passed through together.

**Solution**:
```yaml
- name: Find devices in the same IOMMU group
  ansible.builtin.shell: |
    gpu_slot="{{ hostvars[current_vm]['pci_slot'] }}"
    for group_dir in /sys/kernel/iommu_groups/*/devices/0000:$gpu_slot; do
      if [ -e "$group_dir" ]; then
        group=$(echo $group_dir | cut -d/ -f5)
        for dev in /sys/kernel/iommu_groups/$group/devices/*; do
          dev_addr=$(basename $dev | sed 's/^0000://')
          if [ "$dev_addr" != "$gpu_slot" ]; then
            echo "$dev_addr"
          fi
        done
      fi
    done
```

**Implementation**: We detect all devices in the same IOMMU group as the GPU and add them all to the VM configuration.

### 4.2 Audio Device Handling

**Challenge**: GPU audio components often rebind to snd_hda_intel, preventing VM from accessing the entire GPU.

**Solution**:

1. Created a dedicated script for binding audio devices:
```bash
#!/bin/bash
# {{ ansible_managed }}
# Script to bind a specific GPU audio device to vfio-pci

AUDIO_DEVICE=$1

if [ -z "$AUDIO_DEVICE" ]; then
  echo "Error: No audio device specified"
  exit 1
fi

# Ensure vfio modules are loaded
modprobe vfio-pci

# Check if device exists
if [ ! -e "/sys/bus/pci/devices/0000:$AUDIO_DEVICE" ]; then
  echo "Error: Device 0000:$AUDIO_DEVICE does not exist"
  exit 1
fi

# Unbind from current driver if bound
if [ -e "/sys/bus/pci/devices/0000:$AUDIO_DEVICE/driver" ]; then
  echo "Unbinding 0000:$AUDIO_DEVICE from current driver"
  echo "0000:$AUDIO_DEVICE" > /sys/bus/pci/devices/0000:$AUDIO_DEVICE/driver/unbind
fi

# Set driver override to vfio-pci
echo "Setting driver_override to vfio-pci"
echo "vfio-pci" > /sys/bus/pci/devices/0000:$AUDIO_DEVICE/driver_override

# Bind to vfio-pci
echo "Binding 0000:$AUDIO_DEVICE to vfio-pci"
echo "0000:$AUDIO_DEVICE" > /sys/bus/pci/drivers/vfio-pci/bind

echo "Successfully bound 0000:$AUDIO_DEVICE to vfio-pci"
exit 0
```

2. Created a udev rule to trigger audio binding when device is detected:
```bash
# VFIO PCI audio device rule - prevent certain audio devices from binding to snd_hda_intel
# {{ ansible_managed }}

# For RTX 3090 audio controller at 01:00.1
SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{device}=="0x1aef", ACTION=="add", RUN+="/usr/local/bin/vfio-bind-audio.sh 01:00.1"
```

**Implementation**: This two-part approach ensures that audio devices are properly bound to vfio-pci at system boot and prevents the snd_hda_intel driver from claiming them.

### 4.2 IOMMU Driver Activation Timeouts

**Challenge**: VMs fail to start with error: "Failed to override IOMMU group driver: Device took too long to activate"

**Solution**:
```yaml
- name: Start VM with IOMMU activation retry logic
  ansible.builtin.shell: |
    for attempt in {1..5}; do
      # Try to start VM 
      lxc start {{ current_vm }} 2>&1 || true
      
      # Check if VM started successfully
      if lxc info {{ current_vm }} | grep -q "Status: RUNNING"; then
        echo "VM started successfully on attempt $attempt"
        exit 0
      else
        # Check for specific IOMMU error
        if lxc info --show-log {{ current_vm }} | grep -q "Failed to override IOMMU group driver"; then
          echo "IOMMU driver activation issue detected, waiting before retry..."
          # Remove and re-add the device to reset the binding
          lxc config device remove {{ current_vm }} gpu 2>/dev/null || true
          sleep 5
          lxc config device add {{ current_vm }} gpu gpu [pci options] 2>/dev/null || true
          sleep 10
        else
          sleep 10
        fi
      fi
    done
    
    # Final attempt
    lxc start {{ current_vm }}
```

**Implementation**: We use a retry mechanism that removes and re-adds GPU devices when IOMMU activation issues are detected, allowing the driver binding process to be reset between attempts.

### 4.3 PCI Slot Assignment

**Challenge**: Systems with multiple identical GPUs require specific PCI slot assignment.

**Solution**:
- Define PCI slots explicitly in inventory:
  ```yaml
  tkw1:
    parent_host: bcn1
    gpu_passthrough: true
    gpu_type: "RTX 3090"
    pci_slot: "01:00.0"
  ```
- Use PCI slot in LXD configuration with correct syntax:
  ```yaml
  - name: Add GPU device by PCI slot
    ansible.builtin.command: "lxc config device add {{ vm_name }} gpu pci address={{ pci_slot }}"
  ```

**Implementation**: We allow specific PCI slot assignment via inventory, with fallback to dynamic assignment. Note the syntax `pci address=X:X.X` instead of the older `gpu pci=X:X.X` format.

### 4.3 VM Start/Stop Sequence

**Challenge**: GPU device configuration requires VMs to be stopped and restarted.

**Solution**:
```yaml
# Stop VM
- name: Stop VM before GPU configuration
  ansible.builtin.command: lxc stop {{ current_vm }} --force

# Add GPU device
- name: Add GPU device
  ansible.builtin.command: lxc config device add {{ current_vm }} gpu gpu

# Start VM
- name: Start VM to apply changes
  ansible.builtin.command: lxc start {{ current_vm }}
```

**Implementation**: Our playbook follows the stop→configure→start sequence consistently.

### 4.4 Driver Version Consistency

**Challenge**: Host and VM NVIDIA driver versions must match.

**Solution**:
```yaml
# Define driver version once in vars
vars:
  nvidia_driver_version: "570-server"

# Install same version in VM
- name: Install NVIDIA packages in VM
  ansible.builtin.shell: |
    lxc exec {{ current_vm }} -- apt-get install -y \
      nvidia-driver-{{ nvidia_driver_version }} \
      nvidia-utils-{{ nvidia_driver_version }} \
      nvidia-cuda-toolkit
```

**Implementation**: We use a single variable for driver version across host and VM installations to ensure compatibility. CUDA toolkit is also installed for development support.

### 4.5 Non-Interactive Package Installation

**Challenge**: NVIDIA package installation can prompt for user input, blocking automation.

**Solution**:
```yaml
- name: Install NVIDIA packages non-interactively
  ansible.builtin.shell: |
    lxc exec {{ current_vm }} -- bash -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-utils-...'
```

**Implementation**: We use DEBIAN_FRONTEND=noninteractive for all package installations.

### 4.6 Timeouts and Retry Logic

**Challenge**: GPU operations can be time-consuming and occasionally fail.

**Solution**:
```yaml
- name: Long-running task with retry
  ansible.builtin.command: ...
  register: result
  failed_when: result.rc != 0
  retries: 3
  delay: 10
  until: result.rc == 0
  async: 600  # 10 minutes timeout
  poll: 15    # Check every 15 seconds
```

**Implementation**: We use async/poll for long-running tasks and retry logic for operations that might fail.

## 5. Inventory Variables

GPU passthrough configuration is controlled via inventory variables:

1. **VM-Level Variables**:
   - `gpu_passthrough: true|false` - Enable/disable GPU passthrough for this VM
   - `gpu_type: "RTX 3090"` - Type of GPU (documentation only)
   - `pci_slot: "01:00.0"` - Specific PCI slot for direct passthrough (optional)

2. **Host-Level Variables**:
   - `server_type: "desktop|headless"` - Whether this is a desktop or headless server
   - `configure_gpu_passthrough: true|false` - Master switch for GPU passthrough

## 6. Testing and Verification

Our test playbook (68_test_vm_gpu_passthrough.yaml) performs comprehensive verification:

1. **GPU Visibility**:
   ```
   lspci | grep -i vga && lspci | grep -i nvidia
   ```

2. **Driver Functionality**:
   ```
   nvidia-smi
   ```

3. **CUDA Availability**:
   ```
   nvidia-smi -q -d COMPUTE
   ```

4. **Basic Stress Test**:
   ```
   nvidia-smi dmon -s u
   ```

This multi-level testing ensures that the GPU is not only visible but fully functional within the VM.

## 7. Detected Issues and Solutions

### 7.1 VM Fails to Start After GPU Configuration

**Issue**: VM fails to start with error: `Failed to override IOMMU group driver: Device took too long to activate`.

**Solution**:
- Implement an advanced retry mechanism with device re-binding:
  ```bash
  for attempt in {1..5}; do
    echo "Attempt $attempt to start VM..."
    
    # Try to start the VM
    lxc start vm_name 2>&1 || true
    
    # Check if VM started successfully
    if lxc info vm_name | grep -q "Status: RUNNING"; then
      echo "VM started successfully on attempt $attempt"
      exit 0
    else
      # Check for specific IOMMU error
      if lxc info --show-log vm_name | grep -q "Failed to override IOMMU group driver"; then
        echo "IOMMU driver activation issue detected, waiting before retry..."
        # Try to ensure any bound devices are properly released
        lxc config device remove vm_name gpu 2>/dev/null || true
        sleep 5
        # Add the device back with correct syntax
        lxc config device add vm_name gpu pci address=01:00.0 2>/dev/null || true
        sleep 10
      else
        echo "Start failed with unknown error, waiting before retry..."
        sleep 10
      fi
    fi
  done
  ```
- Add a longer pause (30+ seconds) after VM restart
- After adding GPU device, verify all devices in the same IOMMU group are also added
- Make sure to use the correct LXD syntax for device addition (`pci address=X:X.X`)

**Diagnosis**:
```bash
# Check IOMMU group for specific PCI slot
find /sys/kernel/iommu_groups/*/devices/0000:01:00.0 -type l | head -1 | xargs dirname | xargs basename | xargs echo "IOMMU Group: "

# List all devices in the IOMMU group
find /sys/kernel/iommu_groups/XX/devices/ -type l | xargs basename | sed 's/^0000://'

# Check driver binding for each device in the IOMMU group
for dev in $(find /sys/kernel/iommu_groups/XX/devices/ -type l | xargs basename); do
  if [ -e "/sys/bus/pci/devices/$dev/driver" ]; then
    driver=$(basename $(readlink -f /sys/bus/pci/devices/$dev/driver))
    echo "$dev -> $driver"
  else
    echo "$dev -> (no driver)"
  fi
done
```

**Root Cause Analysis**:
The "Device took too long to activate" error occurs because:
1. LXD attempts to bind the device to vfio-pci driver for passthrough
2. The driver binding takes longer than LXD's timeout period
3. This often happens when the IOMMU subsystem needs time to properly set up
4. Removing and re-adding the device can help reset the binding process

### 7.2 VM Hangs After GPU Passthrough

**Issue**: Some VMs would hang or become unresponsive after GPU passthrough.

**Solution**: 
- Ensure all devices in the IOMMU group are passed through
- Add a longer pause (30+ seconds) after VM restart
- Install appropriate NVIDIA drivers in the VM before testing
- Verify VM is running with `lxc info` before attempting to access GPU

### 7.2 GPU Not Visible in VM

**Issue**: The GPU was not visible in the VM even after configuration.

**Solution**:
- Verify VFIO binding on the host (`lspci -nnk | grep -A3 "NVIDIA" | grep -B1 "vfio-pci"`)
- Check LXD device configuration (`lxc config device show <vm-name>`)
- Ensure the VM was fully restarted after configuration

### 7.3 nvidia-smi Command Fails

**Issue**: The `nvidia-smi` command failed in the VM even with visible GPU.

**Solution**:
- Install exact matching driver version
- On Ubuntu 24.04 (Noble) VMs, handle PPA conflicts properly:
  ```bash
  # Remove any conflicting PPA files
  rm -f /etc/apt/sources.list.d/*graphics-drivers*
  
  # Use mainline repositories
  echo "deb http://archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list.d/main.list
  echo "deb http://archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list.d/main.list
  echo "deb http://security.ubuntu.com/ubuntu noble-security main restricted universe multiverse" >> /etc/apt/sources.list.d/main.list
  
  # Install NVIDIA packages
  apt-get update -y
  apt-get install -y nvidia-driver-570-server nvidia-utils-570-server
  ```
- Install CUDA toolkit for additional functionality
- Use noninteractive installation to prevent prompts
- Reload NVIDIA modules if they don't load automatically:
  ```bash
  rmmod nvidia_drm nvidia_modeset nvidia_uvm nvidia 2>/dev/null || true
  modprobe nvidia
  ```

## A. Example PCI Slot Discovery

To identify the correct PCI slot for your GPU:

```bash
# List all GPUs with PCI slots
lspci -nnk | grep -A3 "VGA\|3D\|Display"

# Example output:
# 01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA102 [GeForce RTX 3090] [10de:2204] (rev a1)
#        Subsystem: ASUSTeK Computer Inc. Device [1043:8708]
#        Kernel driver in use: vfio-pci
#        Kernel modules: nvidia
```

Use the PCI slot (01:00.0 in this example) in your inventory:

```yaml
tkw1:
  parent_host: bcn1
  gpu_passthrough: true
  gpu_type: "RTX 3090"
  pci_slot: "01:00.0"  # From lspci output
```

## B. VFIO-PCI Binding Verification

To verify that GPUs are properly bound to VFIO-PCI:

```bash
# Check all NVIDIA GPUs
lspci -nnk | grep -A3 "NVIDIA" | grep -B1 "vfio-pci"

# Example output:
# 01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA102 [GeForce RTX 3090] [10de:2204] (rev a1)
#        Kernel driver in use: vfio-pci
```

The "Kernel driver in use: vfio-pci" line confirms proper binding.

## C. Sequential VM Processing Pattern

Our recommended pattern for VM processing:

```yaml
# Main playbook
- name: Process VMs sequentially
  include_tasks: configure_vm_gpu.yaml
  loop: "{{ host_gpu_vms }}"
  loop_control:
    loop_var: current_vm
    pause: 2  # Small pause between VMs

# Task file (configure_vm_gpu.yaml)
- name: Process this VM
  block:
    - name: VM-specific tasks...
  when: should_continue | bool  # Control flag for conditional execution
```

This pattern allows for clear per-VM processing with proper error handling.

---

## 8. Ubuntu 24.04 (Noble) Specific Challenges

We encountered specific challenges with Ubuntu 24.04 (Noble) VMs:

### 8.1 PPA Management Issues

**Issue**: In Ubuntu 24.04, the graphics-drivers PPA had configuration conflicts causing apt errors.

**Solution**:
- Instead of using the PPA, we relied on mainline repository packages:
```yaml
- name: Create direct package source instead of PPA
  ansible.builtin.shell: |
    echo "deb http://archive.ubuntu.com/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list.d/main.list
    echo "deb http://archive.ubuntu.com/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list.d/main.list
    echo "deb http://security.ubuntu.com/ubuntu noble-security main restricted universe multiverse" >> /etc/apt/sources.list.d/main.list
```
- This approach avoids PPA conflicts while still providing access to the required packages

### 8.2 Driver Installation Process

**Issue**: The driver installation process in Noble required special handling.

**Solution**:
- We created a more resilient installation process:
  1. First clean up any existing NVIDIA packages
  2. Reset the apt sources to use mainstream repositories
  3. Install the exact same driver version as on the host
  4. Manually load the nvidia module if it doesn't load automatically
  
```yaml
- name: Install NVIDIA driver with retry mechanism
  ansible.builtin.shell: |
    apt-get purge -y 'nvidia*' 'libnvidia*' || true
    apt-get autoremove -y
    apt-get update
    apt-get install -y --no-install-recommends \
      nvidia-driver-{{ nvidia_driver_version }} \
      nvidia-utils-{{ nvidia_driver_version }} \
      nvidia-cuda-toolkit
    modprobe nvidia || true
```

## 9. Conclusion

GPU passthrough in LXD VMs is a complex but powerful capability that requires careful configuration at multiple levels. By following the lessons and patterns documented here, you can successfully implement GPU passthrough for your VMs while avoiding common pitfalls.

The most critical lessons learned include:

1. **Proper audio device handling**: Both the GPU and its audio component must be bound to vfio-pci
2. **Correct LXD syntax**: LXD configuration requires precise syntax for PCI device passthrough
3. **Driver version matching**: Host and VM should use the same driver version
4. **OS-specific handling**: Ubuntu 24.04 (Noble) requires special handling for driver installation

With our current implementation, all target VMs have fully functional GPU access with working drivers and CUDA support.