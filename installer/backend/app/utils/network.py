"""
Network utilities for server discovery and validation
"""

import asyncio
import logging
import ipaddress
import socket
import re
from typing import Set, Dict, Any, List

logger = logging.getLogger(__name__)


async def get_local_ip_addresses() -> Set[str]:
    """Get all local IP addresses"""
    try:
        local_ips = set()
        
        # Method 1: Parse ip addr output 
        result = await asyncio.create_subprocess_exec(
            'ip', 'addr', 'show',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        
        if result.returncode == 0:
            # Extract all IP addresses from ip addr output, excluding CIDR
            ip_pattern = r'inet (\d+\.\d+\.\d+\.\d+)/\d+'
            for match in re.finditer(ip_pattern, stdout.decode()):
                ip = match.group(1)
                if ip != '127.0.0.1':  # Exclude localhost
                    local_ips.add(ip)
                    logger.info(f"Found local IP: {ip}")
        
        # Method 2: Use hostname resolution as fallback
        try:
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
            if host_ip != '127.0.0.1':
                local_ips.add(host_ip)
                logger.info(f"Found hostname IP: {host_ip}")
        except:
            pass
        
        # Method 3: Check default route interface
        try:
            route_result = await asyncio.create_subprocess_exec(
                'ip', 'route', 'get', '8.8.8.8',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            route_stdout, _ = await route_result.communicate()
            if route_result.returncode == 0:
                # Extract source IP from route output
                src_match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', route_stdout.decode())
                if src_match:
                    src_ip = src_match.group(1)
                    local_ips.add(src_ip)
                    logger.info(f"Found route source IP: {src_ip}")
        except:
            pass
        
        logger.info(f"Total local IPs found: {local_ips}")
        return local_ips
    except Exception as e:
        logger.error(f"Error getting local IPs: {e}")
        return set()


def is_local_ip(ip_address: str, local_ips: Set[str] = None) -> bool:
    """Check if an IP address is local to this machine"""
    if local_ips is None:
        # Synchronous fallback - not recommended for async code
        return False
    
    if ip_address in local_ips:
        return True
    
    # Alternative method: try to bind to the IP address locally
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind((ip_address, 0))  # Bind to any available port
        test_socket.close()
        logger.info(f"IP {ip_address} confirmed as local via socket binding")
        return True
    except Exception as e:
        logger.debug(f"IP {ip_address} socket binding failed: {e}")
        return False


async def ping_sweep(network_cidr: str) -> List[str]:
    """Perform a ping sweep to find active IPs"""
    try:
        network = ipaddress.IPv4Network(network_cidr, strict=False)
        active_ips = []
        
        # Create tasks for concurrent pinging
        async def ping_ip(ip_str):
            try:
                result = await asyncio.create_subprocess_exec(
                    'ping', '-c', '1', '-W', '1', ip_str,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await result.communicate()
                if result.returncode == 0:
                    return ip_str
            except:
                pass
            return None
        
        # Limit to reasonable subnet size (max 254 hosts)
        host_count = min(254, network.num_addresses - 2)
        tasks = []
        
        for i, ip in enumerate(network.hosts()):
            if i >= host_count:
                break
            tasks.append(ping_ip(str(ip)))
        
        # Execute pings concurrently in batches to avoid overwhelming
        batch_size = 50
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results = await asyncio.gather(*batch)
            active_ips.extend([ip for ip in results if ip])
        
        return active_ips
    except Exception as e:
        logger.error(f"Ping sweep error: {e}")
        return []


async def check_ssh_banner(ip: str, port: int = 22, timeout: int = 3) -> Dict[str, Any]:
    """Check if SSH is running and get banner info"""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout
        )
        
        # SSH servers send banner immediately
        banner = await asyncio.wait_for(
            reader.readline(),
            timeout=timeout
        )
        
        writer.close()
        await writer.wait_closed()
        
        banner_str = banner.decode('utf-8', errors='ignore').strip()
        
        # Analyze banner for Ubuntu indicators
        is_ubuntu = 'Ubuntu' in banner_str
        
        # Be more specific about Ubuntu detection
        is_likely_ubuntu = False
        if is_ubuntu:
            is_likely_ubuntu = True
        elif 'OpenSSH' in banner_str:
            # Check for Ubuntu-specific OpenSSH patterns
            # Ubuntu typically has version patterns like "OpenSSH_8.9p1" or "OpenSSH_9.6p1"
            if any(version in banner_str for version in ['OpenSSH_8.9', 'OpenSSH_9.0', 'OpenSSH_9.3', 'OpenSSH_9.6']):
                is_likely_ubuntu = True
        
        ssh_version = banner_str if banner_str.startswith('SSH-') else None
        
        return {
            'ssh_available': True,
            'banner': banner_str,
            'is_ubuntu': is_ubuntu,
            'is_likely_ubuntu': is_likely_ubuntu,
            'ssh_version': ssh_version
        }
        
    except Exception as e:
        return {
            'ssh_available': False,
            'banner': None,
            'is_ubuntu': False,
            'is_likely_ubuntu': False,
            'ssh_version': None,
            'error': str(e)
        }


async def get_hostname_info(ip: str) -> str:
    """Try to get hostname via multiple methods"""
    # Method 1: Try mDNS/Avahi discovery (works on Ubuntu desktop)
    try:
        result = await asyncio.create_subprocess_exec(
            'avahi-resolve', '-a', ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        
        if stdout:
            output = stdout.decode().strip()
            # Format: "192.168.1.101    hostname.local"
            parts = output.split()
            if len(parts) >= 2:
                hostname = parts[1].rstrip('.local')
                return hostname
    except:
        pass
    
    # Method 2: NetBIOS name resolution (for mixed networks)
    try:
        result = await asyncio.create_subprocess_exec(
            'nmblookup', '-A', ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        
        if stdout:
            output = stdout.decode()
            for line in output.split('\n'):
                if '<00>' in line and 'GROUP' not in line:
                    hostname = line.split()[0].strip()
                    if hostname and hostname != ip:
                        return hostname
    except:
        pass
    
    # Method 3: Simple reverse DNS (may not work on clean systems)
    try:
        result = await asyncio.create_subprocess_exec(
            'dig', '+short', '-x', ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        
        if stdout:
            hostname = stdout.decode().strip().rstrip('.')
            if hostname and not hostname.startswith(';') and hostname != ip and '.' in hostname:
                # Only accept FQDN results, not just IP addresses
                return hostname.split('.')[0]  # Return just the hostname part
    except:
        pass
    
    return None


async def get_hostname_via_ssh(ip: str, timeout: int = 5) -> str:
    """Try to get hostname by connecting via SSH and reading it directly"""
    try:
        # Try to get hostname via SSH (if SSH key auth is available)
        # This is the most reliable method for clean systems
        result = await asyncio.create_subprocess_exec(
            'ssh', '-o', 'ConnectTimeout=3', 
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'BatchMode=yes',  # Don't prompt for password
            f'thinkube@{ip}', 'hostname',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=timeout)
        
        if result.returncode == 0 and stdout:
            hostname = stdout.decode().strip()
            if hostname and hostname != ip:
                return hostname
    except:
        pass
    
    return None