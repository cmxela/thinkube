"""
Server discovery and analysis logic
"""

import asyncio
import logging
from typing import List, Dict, Any
from ..utils.network import (
    ping_sweep, check_ssh_banner, get_hostname_info, 
    get_hostname_via_ssh, get_local_ip_addresses
)

logger = logging.getLogger(__name__)


async def discover_ubuntu_servers(network_cidr: str) -> Dict[str, Any]:
    """Main discovery function that combines multiple methods"""
    start_time = asyncio.get_event_loop().time()
    
    logger.info(f"Starting network discovery for {network_cidr}")
    
    # Step 1: Find active IPs
    logger.info("Finding active IPs...")
    active_ips = await ping_sweep(network_cidr)
    logger.info(f"Found {len(active_ips)} active IPs")
    
    if not active_ips:
        return {
            "servers": [],
            "total_scanned": 0,
            "scan_time": asyncio.get_event_loop().time() - start_time
        }
    
    # Step 2: Check SSH on all active IPs
    logger.info("Checking SSH availability...")
    servers = []
    
    async def analyze_host(ip):
        # Check SSH
        ssh_info = await check_ssh_banner(ip)
        
        # Get hostname if SSH is available
        hostname = None
        if ssh_info['ssh_available']:
            hostname = await get_hostname_via_ssh(ip)
            if not hostname:
                hostname = await get_hostname_info(ip)
        
        # Determine confidence level and OS info
        confidence = "unknown"
        os_info = None
        
        if ssh_info['is_ubuntu']:
            confidence = "confirmed"
            banner = ssh_info['banner']
            if 'Ubuntu' in banner:
                # Try to extract version info from banner
                if 'Ubuntu-' in banner:
                    # Example: SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.5
                    # Extract the Ubuntu package version to guess OS version
                    try:
                        ubuntu_part = banner.split('Ubuntu-')[1]
                        if ubuntu_part.startswith('3ubuntu'):
                            os_info = "Ubuntu 24.04 LTS"
                        elif ubuntu_part.startswith('2ubuntu'):
                            os_info = "Ubuntu 22.04 LTS"
                        elif ubuntu_part.startswith('1ubuntu'):
                            os_info = "Ubuntu 20.04 LTS"
                        else:
                            os_info = "Ubuntu (recent version)"
                    except:
                        os_info = "Ubuntu (version unknown)"
                else:
                    os_info = "Ubuntu (version unknown)"
        elif ssh_info['is_likely_ubuntu']:
            confidence = "possible"
            os_info = "Likely Ubuntu (needs verification)"
        elif ssh_info['ssh_available']:
            # Only mark as "possible" for very specific cases
            banner = ssh_info['banner'] or ""
            
            # Check for strong Ubuntu indicators
            non_ubuntu_indicators = ['Debian', 'CentOS', 'RHEL', 'Alpine', 'raspberrypi', 'Cisco', 'Mikrotik', 'pfSense']
            has_non_ubuntu_indicator = any(indicator.lower() in banner.lower() for indicator in non_ubuntu_indicators)
            
            if not has_non_ubuntu_indicator and 'OpenSSH' in banner:
                confidence = "possible"
                os_info = "Linux SSH server (needs verification)"
            else:
                confidence = "unlikely"
        
        return {
            "ip": ip,
            "hostname": hostname,
            "os_info": os_info,
            "ssh_available": ssh_info['ssh_available'],
            "confidence": confidence,
            "banner": ssh_info['banner']
        }
    
    # Analyze all hosts concurrently
    tasks = [analyze_host(ip) for ip in active_ips]
    servers = await asyncio.gather(*tasks)
    
    # Filter to only return servers with Ubuntu indicators or strong Linux candidates
    ubuntu_servers = [
        server for server in servers 
        if server['confidence'] in ['confirmed', 'possible']
    ]
    
    # Sort by confidence (confirmed first, then possible)
    confidence_order = {'confirmed': 0, 'possible': 1}
    ubuntu_servers.sort(key=lambda x: confidence_order.get(x['confidence'], 2))
    
    scan_time = asyncio.get_event_loop().time() - start_time
    
    logger.info(f"Discovery completed in {scan_time:.2f}s. Found {len(ubuntu_servers)} Ubuntu candidates.")
    
    return {
        "servers": ubuntu_servers,
        "total_scanned": len(active_ips),
        "scan_time": scan_time
    }


async def verify_local_server() -> Dict[str, Any]:
    """Verify local server without SSH"""
    try:
        # Get hostname
        hostname_result = await asyncio.create_subprocess_exec(
            'hostname',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        hostname_stdout, _ = await hostname_result.communicate()
        hostname = hostname_stdout.decode().strip() if hostname_result.returncode == 0 else None
        
        # Get OS info
        os_result = await asyncio.create_subprocess_exec(
            'lsb_release', '-d',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        os_stdout, _ = await os_result.communicate()
        
        os_info = None
        if os_result.returncode == 0:
            os_info = os_stdout.decode().strip().replace('Description:', '').strip()
        else:
            # Fallback to /etc/os-release
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            os_info = line.split('=', 1)[1].strip().strip('"')
                            break
            except:
                pass
        
        return {
            "connected": True,
            "success": True,  # Frontend compatibility
            "message": "Local server (running installer)",
            "os_info": os_info,
            "hostname": hostname
        }
    except Exception as e:
        return {
            "connected": False,
            "success": False,  # Frontend compatibility
            "message": f"Local server verification error: {str(e)}",
            "os_info": None,
            "hostname": None
        }


async def verify_ssh_connectivity(ip_address: str, username: str = "thinkube", password: str = None) -> Dict[str, Any]:
    """Verify SSH connectivity to a server"""
    # Check if this is the local machine using multiple methods
    local_ips = await get_local_ip_addresses()
    logger.info(f"Checking if {ip_address} is in local IPs: {local_ips}")
    
    is_local = ip_address in local_ips
    
    # Alternative method: try to bind to the IP address locally
    if not is_local:
        try:
            import socket
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind((ip_address, 0))  # Bind to any available port
            test_socket.close()
            is_local = True
            logger.info(f"IP {ip_address} confirmed as local via socket binding")
        except Exception as e:
            logger.info(f"IP {ip_address} socket binding failed: {e}")
    
    if is_local:
        logger.info(f"Detected local server {ip_address}, using direct verification")
        return await verify_local_server()
    else:
        logger.info(f"IP {ip_address} is not local, proceeding with SSH verification")
    
    try:
        # Try SSH connection - use password if provided, otherwise try key-based
        if password:
            # Use sshpass for password authentication
            result = await asyncio.create_subprocess_exec(
                'sshpass', '-p', password,
                'ssh', '-o', 'ConnectTimeout=5',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f'{username}@{ip_address}', 'echo "SSH OK"; lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
            # Fall back to key-based auth
            result = await asyncio.create_subprocess_exec(
                'ssh', '-o', 'ConnectTimeout=5',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'BatchMode=yes',  # Don't prompt for password
                f'{username}@{ip_address}', 'echo "SSH OK"; lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        stdout, stderr = await result.communicate()
        
        if result.returncode == 0:
            output = stdout.decode().strip()
            lines = output.split('\n')
            
            # Get hostname
            if password:
                hostname_result = await asyncio.create_subprocess_exec(
                    'sshpass', '-p', password,
                    'ssh', '-o', 'ConnectTimeout=5',
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    f'{username}@{ip_address}', 'hostname',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                hostname_result = await asyncio.create_subprocess_exec(
                    'ssh', '-o', 'ConnectTimeout=5',
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'BatchMode=yes',
                    f'{username}@{ip_address}', 'hostname',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            hostname_stdout, _ = await hostname_result.communicate()
            hostname = hostname_stdout.decode().strip() if hostname_result.returncode == 0 else None
            
            # Extract OS info
            os_info = None
            for line in lines:
                if 'Ubuntu' in line:
                    os_info = line.replace('Description:', '').replace('PRETTY_NAME=', '').strip().strip('"')
                    break
            
            return {
                "connected": True,
                "success": True,  # Frontend compatibility
                "message": "SSH connection successful",
                "os_info": os_info,
                "hostname": hostname
            }
        else:
            error_msg = stderr.decode().strip()
            return {
                "connected": False,
                "success": False,  # Frontend compatibility
                "message": f"SSH connection failed: {error_msg}",
                "os_info": None,
                "hostname": None
            }
    except Exception as e:
        return {
            "connected": False,
            "success": False,  # Frontend compatibility
            "message": f"SSH verification error: {str(e)}",
            "os_info": None,
            "hostname": None
        }