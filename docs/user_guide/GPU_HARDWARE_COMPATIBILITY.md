# GPU Hardware Compatibility Guide for Passthrough

This document provides detailed information about hardware compatibility for GPU passthrough in the Thinkube platform.

## Table of Contents

- [Introduction](#introduction)
- [Motherboard Compatibility](#motherboard-compatibility)
- [CPU Compatibility](#cpu-compatibility)
- [GPU Compatibility](#gpu-compatibility)
- [IOMMU Group Verification](#iommu-group-verification)
- [Tested Hardware Configurations](#tested-hardware-configurations)
- [Hardware Recommendations](#hardware-recommendations)

## Introduction

GPU passthrough allows a virtual machine to directly access a physical GPU for near-native performance. However, not all hardware supports this feature adequately. The primary limitation is IOMMU grouping, which is determined by your motherboard's chipset and BIOS implementation.

## Motherboard Compatibility

### Key Motherboard Features for GPU Passthrough

1. **IOMMU Support**: The motherboard must support IOMMU/VT-d/AMD-Vi
2. **Proper IOMMU Grouping**: GPUs should be in their own IOMMU group or grouped only with their related devices
3. **PCIe Layout**: Motherboards with more PCIe slots directly connected to the CPU (rather than through chipset) generally have better IOMMU grouping

### Motherboard Types by Compatibility

1. **Ideal**: High-end workstation/server motherboards (ASUS WS, Supermicro, etc.)
2. **Good**: Higher-end consumer motherboards with good PCIe layout
3. **Problematic**: Budget motherboards and laptops

### Motherboard BIOS Settings

Required BIOS settings for GPU passthrough:
- Enable Intel VT-d or AMD IOMMU/AMD-Vi
- Enable Virtualization Technology (VT-x/AMD-V)
- In some cases, disable CSM support
- On some boards: Adjust PCIe settings to Gen3 instead of Auto

## CPU Compatibility

### Intel CPUs

- All modern Intel CPUs (6th gen/Skylake and newer) support VT-d
- Higher-end CPUs (especially Xeon) often have better IOMMU implementation
- CPUs with integrated graphics (iGPU) are recommended for desktop systems to allow the host OS to use the iGPU while passing through discrete GPUs

### AMD CPUs

- All modern AMD Ryzen CPUs support AMD-Vi
- Ryzen CPUs with integrated graphics (e.g., 5600G, 5700G) are recommended for desktop systems
- EPYC and Threadripper typically have superior IOMMU grouping

## GPU Compatibility

### NVIDIA GPUs

All modern NVIDIA GPUs are compatible with passthrough, but there are important considerations:

1. **Consumer GPUs (GeForce)**:
   - Work with passthrough but NVIDIA drivers may detect virtualization
   - For optimal performance, use the following parameters in the VM configuration:
     ```
     <hidden state='on'/>
     ```
   
2. **Professional GPUs (Quadro, Tesla)**:
   - Officially support virtualization
   - Don't require hiding the virtualization state

### AMD GPUs

- All modern AMD GPUs work well with passthrough
- Don't have virtualization detection limitations
- Radeon PRO series has better virtualization support

### GPU Physical Installation

The physical PCIe slot where you install the GPU affects passthrough compatibility:

1. **Primary PCIe slots** (directly connected to CPU):
   - Usually have better IOMMU grouping
   - Often labeled as CPU_PCIE1, PCIEX16_1, etc.

2. **Secondary PCIe slots** (connected through chipset):
   - May have problematic IOMMU grouping
   - Often share groups with other devices

## IOMMU Group Verification

### Checking IOMMU Groups

To verify IOMMU groups on your system, run:

```bash
# Enable IOMMU if not already enabled
./scripts/run_ssh_command.sh your_host "sudo bash -c 'echo \"options vfio_iommu_type1 allow_unsafe_interrupts=1\" > /etc/modprobe.d/vfio.conf'"
./scripts/run_ssh_command.sh your_host "sudo modprobe vfio_iommu_type1"

# Show all IOMMU groups and their devices
./scripts/run_ssh_command.sh your_host "for d in /sys/kernel/iommu_groups/*/devices/*; do n=\$(basename \$d); echo \"\$n \"; lspci -nns \$n; done | sort -V"
```

### Interpreting Results

A good IOMMU group for a GPU looks like this:
```
IOMMU Group 14:
07:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3090] [10de:2204]
07:00.1 Audio device: NVIDIA Corporation GA102 High Definition Audio Controller [10de:1aef]
```

Problematic IOMMU grouping looks like this:
```
IOMMU Group 1:
00:01.0 PCI bridge: Intel Corporation PCI Express Root Port [8086:1901]
01:00.0 VGA compatible controller: NVIDIA Corporation GeForce RTX 2080 [10de:1e82]
01:00.1 Audio device: NVIDIA Corporation TU104 HD Audio Controller [10de:10f7]
01:00.2 USB controller: NVIDIA Corporation TU104 USB 3.1 Host Controller [10de:1ad6]
01:00.3 Serial bus controller: NVIDIA Corporation TU104 USB Type-C UCSI Controller [10de:1ad7]
```

The GPU in the problematic example cannot be used for passthrough without also passing through the PCI bridge, which would create conflicts.

## Tested Hardware Configurations

### Confirmed Working Setups

1. **bcn1** - Desktop System:
   - CPU: AMD Ryzen with integrated graphics
   - GPUs: 2× NVIDIA RTX 3090
   - Configuration: Mixed setup with one GPU passed through, one kept for host
   - IOMMU Status: Good isolation, specific PCI slots can be individually bound

2. **bcn2** - Headless Server:
   - GPU: NVIDIA GTX 1080Ti
   - Configuration: Full GPU passthrough
   - IOMMU Status: Good isolation

### Recommended Hardware Combinations

For new Thinkube deployments, we recommend:

1. **Desktop Systems**:
   - CPU: AMD Ryzen with integrated graphics (e.g., 5700G) or Intel with iGPU
   - Motherboard: High-end X570/X670 (AMD) or Z590/Z690 (Intel)
   - GPU: Any NVIDIA RTX or AMD Radeon, preferably in primary PCIe slots

2. **Server/Headless Systems**:
   - CPU: AMD EPYC, Threadripper, or Intel Xeon
   - Motherboard: Server-grade with good IOMMU support
   - GPU: Any NVIDIA or AMD GPU in well-isolated IOMMU groups

## Hardware Recommendations

### Best Motherboards for GPU Passthrough

1. **AMD Platform**:
   - ASUS ProArt X570/X670 Creator
   - ASUS ROG Crosshair VIII Hero
   - ASRock X570 Taichi
   - Gigabyte X570 Aorus Master

2. **Intel Platform**:
   - ASUS ProArt Z690/Z790 Creator
   - ASUS WS series
   - Gigabyte Z690 Aorus Master
   - ASRock Z690 Taichi

### Best CPUs for GPU Passthrough

1. **AMD**:
   - Ryzen 7 5700G/5800X3D (desktop with iGPU)
   - Ryzen 9 5950X (high performance)
   - Threadripper (workstation/server)
   - EPYC (server)

2. **Intel**:
   - Core i7/i9 12th/13th Gen (desktop with iGPU)
   - Xeon W-3300 series (workstation/server)
   - Xeon Scalable (server)

---

Remember that hardware compatibility is the foundation of successful GPU passthrough. Even the best software configuration cannot overcome physical hardware limitations with IOMMU groups.