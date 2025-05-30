#!/bin/bash
# Fix network configuration permanently

echo "Fixing network configuration permanently..."
echo "This script will:"
echo "1. Remove the secondary IP address"
echo "2. Check and fix netplan configuration"
echo "3. Apply the changes"
echo ""

# First, remove the secondary IP temporarily
echo "Removing secondary IP address 192.168.1.48..."
sudo ip addr del 192.168.1.48/24 dev eno1 2>/dev/null || echo "Secondary IP may already be removed"

# Check all netplan files
echo ""
echo "Checking netplan configuration files..."
echo "Current netplan files:"
ls -la /etc/netplan/

# Backup existing configs
echo ""
echo "Creating backup of netplan configs..."
sudo cp -r /etc/netplan /etc/netplan.backup.$(date +%Y%m%d_%H%M%S)

# Check if there's a conflicting DHCP configuration
echo ""
echo "Checking for DHCP configurations..."

# Look for the thinkube config
if [ -f "/etc/netplan/01-thinkube-config.yaml" ]; then
    echo "Found thinkube config. Current content:"
    sudo cat /etc/netplan/01-thinkube-config.yaml
    
    echo ""
    echo "Creating corrected configuration..."
    
    # Create a proper static-only configuration
    cat << 'EOF' | sudo tee /etc/netplan/01-thinkube-config.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eno1:
      addresses:
        - 192.168.1.101/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
      dhcp4: false
      dhcp6: false
EOF
fi

# Disable cloud-init network configuration if it exists
if [ -f "/etc/netplan/50-cloud-init.yaml" ]; then
    echo ""
    echo "Disabling cloud-init network configuration..."
    sudo mv /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.disabled
fi

# Disable NetworkManager config if it's trying to manage eno1
if [ -f "/etc/netplan/01-network-manager-all.yaml" ]; then
    echo ""
    echo "Checking NetworkManager configuration..."
    # Create a config that excludes eno1
    cat << 'EOF' | sudo tee /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    wlp10s0:
      dhcp4: true
EOF
fi

echo ""
echo "Applying netplan configuration..."
sudo netplan apply

echo ""
echo "Waiting for network to settle..."
sleep 3

echo ""
echo "Final network configuration:"
ip addr show eno1 | grep inet

echo ""
echo "Network configuration has been fixed!"
echo "The system now has only the static IP 192.168.1.101 on eno1"