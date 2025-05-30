"""
API routes for server discovery
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

from ..core.discovery import discover_ubuntu_servers, verify_ssh_connectivity
from ..utils.network import get_local_ip_addresses
from ..models.server import NetworkDiscoveryRequest, SSHVerificationRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["discovery"])


async def get_real_hardware_info(ip_address: str, username: str = "thinkube"):
    """Get actual hardware information via SSH commands"""
    
    # Check if this is the local machine first
    local_ips = await get_local_ip_addresses()
    is_local = ip_address in local_ips
    
    async def run_command(cmd: str):
        """Run command either locally or via SSH"""
        if is_local:
            # Run locally
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return stdout.decode().strip() if process.returncode == 0 else ""
        else:
            # Run via SSH
            ssh_cmd = [
                'ssh', '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'BatchMode=yes',
                f'{username}@{ip_address}',
                cmd
            ]
            process = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return stdout.decode().strip() if process.returncode == 0 else ""
    
    try:
        # Initialize hardware info
        hardware_info = {
            "cpu_cores": 0,
            "cpu_model": "Unknown",
            "memory_gb": 0.0,
            "disk_gb": 0.0,
            "gpu_detected": False,
            "gpu_model": None,
            "gpu_count": 0,
            "architecture": "unknown"
        }
        
        # Get CPU information
        logger.info(f"Getting CPU info for {ip_address}")
        
        # CPU cores
        cpu_cores_cmd = "nproc"
        cpu_cores_result = await run_command(cpu_cores_cmd)
        if cpu_cores_result.isdigit():
            hardware_info["cpu_cores"] = int(cpu_cores_result)
            
        # CPU model
        cpu_model_cmd = "cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | sed 's/^ *//'"
        cpu_model_result = await run_command(cpu_model_cmd)
        if cpu_model_result:
            hardware_info["cpu_model"] = cpu_model_result.strip()
            
        # Architecture
        arch_cmd = "uname -m"
        arch_result = await run_command(arch_cmd)
        if arch_result:
            hardware_info["architecture"] = arch_result.strip()
        
        # Memory information (in GB)
        logger.info(f"Getting memory info for {ip_address}")
        memory_cmd = "free -b | grep '^Mem:' | awk '{print $2}'"
        memory_result = await run_command(memory_cmd)
        if memory_result.isdigit():
            memory_bytes = int(memory_result)
            hardware_info["memory_gb"] = round(memory_bytes / (1024**3), 1)
        
        # Disk information (total available space in GB)
        logger.info(f"Getting disk info for {ip_address}")
        disk_cmd = "df -B1 / | tail -1 | awk '{print $2}'"
        disk_result = await run_command(disk_cmd)
        if disk_result.isdigit():
            disk_bytes = int(disk_result)
            hardware_info["disk_gb"] = round(disk_bytes / (1024**3), 1)
        
        # GPU information (NVIDIA only for passthrough focus)
        logger.info(f"Getting NVIDIA GPU info for {ip_address}")
        
        # Comprehensive NVIDIA GPU detection including passthrough diagnostics
        
        # 1. Detect all NVIDIA devices (including those bound to VFIO)
        all_nvidia_cmd = "lspci -nn | grep -i nvidia"
        all_nvidia_result = await run_command(all_nvidia_cmd)
        
        # 2. Detect visible NVIDIA GPUs (not bound to VFIO)
        visible_nvidia_cmd = "lspci | grep -i 'vga\\|3d\\|display' | grep -i nvidia"
        visible_nvidia_result = await run_command(visible_nvidia_cmd)
        
        # 3. Check for VFIO-bound devices
        vfio_cmd = "lspci -k | grep -A 3 -i nvidia"
        vfio_result = await run_command(vfio_cmd)
        
        nvidia_gpus = []
        vfio_gpus = []
        total_nvidia_devices = 0
        
        if all_nvidia_result:
            # Count total NVIDIA devices
            all_nvidia_lines = [line.strip() for line in all_nvidia_result.split('\n') if line.strip()]
            total_nvidia_devices = len(all_nvidia_lines)
            logger.info(f"Total NVIDIA devices found: {total_nvidia_devices}")
            
            for line in all_nvidia_lines:
                logger.info(f"NVIDIA device: {line}")
        
        if visible_nvidia_result:
            # Process visible NVIDIA GPUs
            visible_lines = [line.strip() for line in visible_nvidia_result.split('\n') if line.strip()]
            
            for line in visible_lines:
                # Extract NVIDIA GPU model
                if '[' in line and ']' in line:
                    model_start = line.find('[') + 1
                    model_end = line.find(']')
                    gpu_model = line[model_start:model_end].strip()
                else:
                    parts = line.split('NVIDIA Corporation', 1)
                    if len(parts) > 1:
                        gpu_model = parts[1].split('(')[0].strip()
                    else:
                        gpu_model = "NVIDIA GPU"
                nvidia_gpus.append(gpu_model)
        
        if vfio_result:
            # Check for VFIO-bound GPUs
            vfio_lines = vfio_result.split('\n')
            for i, line in enumerate(vfio_lines):
                if 'nvidia' in line.lower() and ('vga' in line.lower() or '3d' in line.lower()):
                    # Check next lines for driver info
                    if i + 1 < len(vfio_lines) and 'vfio-pci' in vfio_lines[i + 1]:
                        if '[' in line and ']' in line:
                            model_start = line.find('[') + 1
                            model_end = line.find(']')
                            gpu_model = line[model_start:model_end].strip()
                        else:
                            gpu_model = "NVIDIA GPU (VFIO-bound)"
                        vfio_gpus.append(gpu_model)
                        logger.info(f"Found VFIO-bound GPU: {gpu_model}")
        
        # Set GPU information
        visible_count = len(nvidia_gpus)
        vfio_count = len(vfio_gpus)
        total_gpu_count = visible_count + vfio_count
        
        if total_gpu_count > 0:
            hardware_info["gpu_detected"] = True
            hardware_info["gpu_count"] = total_gpu_count
            
            # Create descriptive model string
            if visible_count > 0 and vfio_count > 0:
                # Mix of visible and VFIO-bound
                if visible_count == 1 and vfio_count == 1:
                    hardware_info["gpu_model"] = f"{nvidia_gpus[0]} + 1 VFIO-bound"
                else:
                    hardware_info["gpu_model"] = f"{visible_count} visible + {vfio_count} VFIO-bound NVIDIA GPUs"
            elif visible_count > 0:
                # Only visible GPUs
                if visible_count == 1:
                    hardware_info["gpu_model"] = nvidia_gpus[0]
                elif len(set(nvidia_gpus)) == 1:
                    hardware_info["gpu_model"] = f"{visible_count}x {nvidia_gpus[0]}"
                else:
                    hardware_info["gpu_model"] = f"{visible_count} NVIDIA GPUs: {', '.join(nvidia_gpus)}"
            elif vfio_count > 0:
                # Only VFIO-bound GPUs
                if vfio_count == 1:
                    hardware_info["gpu_model"] = f"{vfio_gpus[0]} (VFIO-bound)"
                else:
                    hardware_info["gpu_model"] = f"{vfio_count} NVIDIA GPUs (all VFIO-bound)"
            
            logger.info(f"GPU Summary: {visible_count} visible, {vfio_count} VFIO-bound, {total_gpu_count} total")
            
            # Check IOMMU groups for passthrough eligibility
            logger.info(f"Checking IOMMU groups for {ip_address}")
            
            # First check if IOMMU is enabled
            iommu_check_cmd = "dmesg | grep -i iommu | grep -i enabled | head -n1"
            iommu_enabled_result = await run_command(iommu_check_cmd)
            logger.info(f"IOMMU enabled check: {iommu_enabled_result}")
            
            iommu_cmd = """
            if [ -d /sys/kernel/iommu_groups/ ]; then
                # Check if any IOMMU groups exist
                group_count=$(ls -1 /sys/kernel/iommu_groups/ 2>/dev/null | wc -l)
                if [ "$group_count" -eq 0 ]; then
                    echo "no_iommu_groups"
                else
                    # Look for all NVIDIA GPUs including VFIO-bound ones
                    for gpu in $(lspci -nn | grep -E 'VGA|3D|Display' | grep -i nvidia | cut -d' ' -f1); do
                        echo -n "$gpu|"
                        if [ -e /sys/bus/pci/devices/0000:$gpu/iommu_group ]; then
                            group=$(readlink /sys/bus/pci/devices/0000:$gpu/iommu_group | awk -F/ '{print $NF}')
                            echo -n "$group|"
                            # Check if group has other devices that are NOT NVIDIA audio
                            # NVIDIA audio devices are expected to be in the same group
                            other_count=0
                            for device in /sys/kernel/iommu_groups/$group/devices/*; do
                                dev_id=$(basename $device)
                                if [ "$dev_id" != "0000:$gpu" ]; then
                                    # Check if it's an NVIDIA audio device (class 0403)
                                    if lspci -n -s $dev_id | grep -q " 0403: 10de:"; then
                                        # It's an NVIDIA audio device, don't count it
                                        :
                                    else
                                        # Not an NVIDIA audio device
                                        other_count=$((other_count + 1))
                                    fi
                                fi
                            done
                            if [ "$other_count" -eq 0 ]; then
                                echo "isolated"
                            else
                                echo "shared|$other_count"
                            fi
                        else
                            echo "no_group|unknown"
                        fi
                    done
                fi
            else
                echo "iommu_disabled"
            fi
            """
            iommu_result = await run_command(iommu_cmd)
            logger.info(f"Raw IOMMU result for {ip_address}: {iommu_result}")
            
            # Parse IOMMU information
            gpu_passthrough_info = []
            iommu_enabled = False
            
            if iommu_result:
                if iommu_result == "iommu_disabled":
                    logger.warning("IOMMU support not available - GPU passthrough not possible")
                    iommu_enabled = False
                elif iommu_result == "no_iommu_groups":
                    logger.warning("No IOMMU groups found - check BIOS settings for VT-d/AMD-Vi")
                    iommu_enabled = False
                else:
                    iommu_enabled = True
                    for line in iommu_result.strip().split('\n'):
                        if line and '|' in line and line != "no_iommu_groups":
                            parts = line.split('|')
                            if len(parts) >= 3:
                                pci_addr = parts[0]
                                group = parts[1]
                                status = parts[2]
                                
                                # Determine eligibility
                                is_eligible = status == 'isolated'
                                
                                gpu_passthrough_info.append({
                                    'pci_address': pci_addr,
                                    'iommu_group': group,
                                    'passthrough_eligible': is_eligible,
                                    'status': status
                                })
                                logger.info(f"GPU {pci_addr} in IOMMU group {group}: {status} (eligible: {is_eligible})")
            
            # Also check for VFIO-bound GPUs that might not show in regular lspci
            vfio_check_cmd = "ls -la /sys/bus/pci/drivers/vfio-pci/ | grep 0000: | awk '{print $9}'"
            vfio_devices = await run_command(vfio_check_cmd)
            if vfio_devices:
                logger.info(f"VFIO-bound devices: {vfio_devices}")
            
            # Log summary
            eligible_count = sum(1 for g in gpu_passthrough_info if g['passthrough_eligible'])
            logger.info(f"GPU passthrough summary for {ip_address}: {len(gpu_passthrough_info)} GPUs found, {eligible_count} eligible for passthrough")
            logger.info(f"Detailed GPU info: {gpu_passthrough_info}")
            
            hardware_info["gpu_passthrough_info"] = gpu_passthrough_info
            hardware_info["iommu_enabled"] = iommu_enabled
            hardware_info["gpu_passthrough_eligible_count"] = eligible_count
            
        else:
            logger.info("No NVIDIA GPUs detected")
            
        # Log diagnostic info
        if total_nvidia_devices != total_gpu_count:
            logger.warning(f"Device count mismatch: {total_nvidia_devices} total devices vs {total_gpu_count} GPUs detected")
        
        logger.info(f"Hardware detection completed for {ip_address}: {hardware_info}")
        return hardware_info
        
    except Exception as e:
        logger.error(f"Error in hardware detection for {ip_address}: {e}")
        raise


@router.post("/discover-servers")
async def discover_servers(request: Dict[str, Any]):
    """Discover Ubuntu servers on the network"""
    network_cidr = request.get("network_cidr", "192.168.1.0/24")
    
    # Real network discovery
    try:
        result = await discover_ubuntu_servers(network_cidr)
        return result
    except Exception as e:
        logger.error(f"Network discovery error: {e}")
        return {
            "error": f"Network discovery failed: {str(e)}",
            "servers": [],
            "total_scanned": 0,
            "scan_time": 0
        }


@router.post("/verify-server-ssh")
async def verify_server_ssh(server: Dict[str, Any]):
    """Verify SSH connectivity to a server"""
    ip_address = server.get("ip_address")
    password = server.get("password")
    
    # Get current system username as default
    import pwd
    current_username = pwd.getpwuid(os.getuid()).pw_name
    username = server.get("username", current_username)
    
    if not ip_address:
        return {
            "connected": False,
            "message": "IP address is required",
            "os_info": None,
            "hostname": None
        }
    
    return await verify_ssh_connectivity(ip_address, username, password)


@router.post("/verify-ssh")
async def verify_ssh(request: Dict[str, Any]):
    """Verify SSH connectivity - frontend compatibility endpoint"""
    # Extract parameters from frontend request format
    server_ip = request.get("server")
    password = request.get("password")
    
    # Get current system username as default if not provided
    import pwd
    current_username = pwd.getpwuid(os.getuid()).pw_name
    username = request.get("username", current_username)
    
    if not server_ip:
        return {
            "connected": False,
            "message": "Server IP is required",
            "os_info": None,
            "hostname": None
        }
    
    return await verify_ssh_connectivity(server_ip, username, password)


@router.get("/debug-local-ips")
async def debug_local_ips():
    """Debug endpoint to check local IP detection"""
    local_ips = await get_local_ip_addresses()
    return {
        "local_ips": list(local_ips),
        "count": len(local_ips)
    }


@router.post("/setup-ssh-keys")
async def setup_ssh_keys(request: Dict[str, Any]):
    """Set up SSH keys between servers using Ansible playbook"""
    from ..services.ansible_executor import ansible_executor
    
    servers = request.get("servers", [])
    username = request.get("username", "thinkube")
    password = request.get("password")
    
    # Define playbook path
    playbook_path = "ansible/00_initial_setup/10_setup_ssh_keys.yaml"
    
    # Set up environment variables for Ansible
    environment = {}
    if password:
        environment["ANSIBLE_SUDO_PASS"] = password
    
    # Execute the playbook using the reusable service
    result = await ansible_executor.execute_playbook(
        playbook_path=playbook_path,
        environment=environment,
        timeout=180  # 3 minutes for SSH setup
    )
    
    # Return standardized response
    return ansible_executor.format_result_for_api(result)


@router.post("/debug-ssh-check")
async def debug_ssh_check(request: Dict[str, Any]):
    """Debug endpoint to test SSH verification logic"""
    ip_address = request.get("ip_address")
    local_ips = await get_local_ip_addresses()
    
    return {
        "ip_to_check": ip_address,
        "local_ips": list(local_ips),
        "is_local": ip_address in local_ips,
        "ip_type": type(ip_address).__name__,
        "comparison_details": {
            str(ip): {"matches": ip == ip_address, "type": type(ip).__name__} 
            for ip in local_ips
        }
    }


@router.post("/detect-hardware")
async def detect_hardware(server: Dict[str, Any]):
    """Detect hardware configuration of a server via SSH"""
    # Handle both parameter names for compatibility
    ip_address = server.get("ip_address") or server.get("server")
    username = server.get("username", "thinkube")
    
    if not ip_address:
        return {"error": "IP address is required for hardware detection"}
    
    try:
        logger.info(f"Detecting hardware for {ip_address}")
        
        # Get actual hardware info via SSH
        hardware_info = await get_real_hardware_info(ip_address, username)
        
        return {"hardware": hardware_info}
        
    except Exception as e:
        logger.error(f"Failed to detect hardware for {ip_address}: {e}")
        return {
            "error": f"Hardware detection failed: {str(e)}",
            "hardware": {
                "cpu_cores": 0,
                "cpu_model": "Detection Failed",
                "memory_gb": 0,
                "disk_gb": 0,
                "gpu_detected": False,
                "gpu_model": None,
                "gpu_count": 0,
                "architecture": "unknown"
            }
        }


@router.post("/verify-cloudflare")
async def verify_cloudflare(request: Dict[str, Any]):
    """Verify Cloudflare API token and domain access"""
    try:
        token = request.get('token', '')
        domain = request.get('domain', '')
        
        if not token:
            return {"valid": False, "message": "No API token provided"}
        
        if not domain:
            return {"valid": False, "message": "No domain provided"}
        
        # Call Cloudflare API to list zones
        import aiohttp
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://api.cloudflare.com/client/v4/zones?name={domain}',
                headers=headers
            ) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('success'):
                    zones = data.get('result', [])
                    if zones:
                        # Found the domain
                        zone = zones[0]
                        return {
                            "valid": True, 
                            "message": f"Token has access to {zone['name']}",
                            "zone_id": zone['id']
                        }
                    else:
                        return {"valid": False, "message": f"Domain '{domain}' not found in Cloudflare account"}
                elif response.status == 403:
                    return {"valid": False, "message": "Invalid token or insufficient permissions"}
                elif response.status == 401:
                    return {"valid": False, "message": "Invalid Cloudflare API token"}
                else:
                    return {"valid": False, "message": f"Cloudflare API error: {data.get('errors', [{}])[0].get('message', 'Unknown error')}"}
                    
    except Exception as e:
        logger.error(f"Failed to verify Cloudflare token: {e}")
        return {"valid": False, "message": f"Verification error: {str(e)}"}


@router.post("/save-cluster-config")
async def save_cluster_config(config: Dict[str, Any]):
    """Save the cluster configuration from node configuration UI"""
    try:
        # Validate the configuration
        servers = config.get("servers", [])
        if not servers:
            raise ValueError("No servers configured")
        
        # Check for control plane
        control_planes = []
        workers = []
        
        for server in servers:
            if server["role"] in ["hybrid", "direct"] and server.get("k8s_role") == "control_plane":
                control_planes.append(server)
            elif server["role"] in ["hybrid", "direct"] and server.get("k8s_role") == "worker":
                workers.append(server)
            
            # Check containers
            for container in server.get("containers", []):
                if container.get("k8s_role") == "control_plane":
                    control_planes.append(container)
                elif container.get("k8s_role") == "worker":
                    workers.append(container)
        
        if len(control_planes) != 1:
            raise ValueError(f"Exactly one control plane required, found {len(control_planes)}")
        
        if len(workers) < 1:
            raise ValueError("At least one worker node required")
        
        # Save configuration
        # For now, save to a temporary location since we don't have get_project_root function
        home_dir = Path.home()
        config_dir = home_dir / "thinkube" / "inventory" / "installer_configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = config_dir / f"cluster_config_{timestamp}.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "config_file": str(config_file),
            "summary": {
                "servers": len(servers),
                "control_planes": len(control_planes),
                "workers": len(workers)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to save cluster config: {e}")
        return {
            "success": False,
            "message": str(e)
        }