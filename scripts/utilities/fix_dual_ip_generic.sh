#!/bin/bash
# Generic script to fix dual IP issues on any Ubuntu server

echo "=== Generic Dual IP Fix Script ==="
echo ""

# Detect primary network interface
PRIMARY_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -z "$PRIMARY_IFACE" ]; then
    echo "Error: Could not detect primary network interface"
    exit 1
fi

echo "Detected primary network interface: $PRIMARY_IFACE"

# Get all IPs on the interface
echo ""
echo "Current IP addresses on $PRIMARY_IFACE:"
ip addr show $PRIMARY_IFACE | grep "inet " | awk '{print $2}'

# Get the static IP (the one without dynamic flag)
STATIC_IP=$(ip addr show $PRIMARY_IFACE | grep "inet " | grep -v "dynamic" | head -1 | awk '{print $2}')
STATIC_IP_ADDR=$(echo $STATIC_IP | cut -d'/' -f1)
STATIC_IP_CIDR=$(echo $STATIC_IP | cut -d'/' -f2)

# Get the dynamic IPs
DYNAMIC_IPS=$(ip addr show $PRIMARY_IFACE | grep "inet " | grep "dynamic" | awk '{print $2}')

if [ -z "$DYNAMIC_IPS" ]; then
    echo "No dynamic IPs found. Network configuration appears correct."
    exit 0
fi

echo ""
echo "Static IP detected: $STATIC_IP"
echo "Dynamic IPs to remove:"
echo "$DYNAMIC_IPS"

# Get gateway
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
echo "Gateway detected: $GATEWAY"

# Get current DNS servers
DNS_SERVERS=$(resolvectl status | grep "DNS Servers" | head -1 | cut -d':' -f2 | xargs)
if [ -z "$DNS_SERVERS" ]; then
    DNS_SERVERS="8.8.8.8 8.8.4.4"
fi
echo "DNS servers: $DNS_SERVERS"

# Remove dynamic IPs
echo ""
echo "Removing dynamic IP addresses..."
for DIP in $DYNAMIC_IPS; do
    echo "Removing $DIP from $PRIMARY_IFACE..."
    sudo ip addr del $DIP dev $PRIMARY_IFACE 2>/dev/null || echo "Already removed or error"
done

# Backup netplan configs
echo ""
echo "Backing up netplan configuration..."
sudo cp -r /etc/netplan /etc/netplan.backup.$(date +%Y%m%d_%H%M%S)

# Find the main netplan config file
NETPLAN_FILE=""
for f in /etc/netplan/*.yaml; do
    if sudo grep -q "$PRIMARY_IFACE" "$f" 2>/dev/null; then
        NETPLAN_FILE="$f"
        break
    fi
done

# If no specific file found, use the most likely one
if [ -z "$NETPLAN_FILE" ]; then
    if [ -f "/etc/netplan/01-thinkube-config.yaml" ]; then
        NETPLAN_FILE="/etc/netplan/01-thinkube-config.yaml"
    elif [ -f "/etc/netplan/00-installer-config.yaml" ]; then
        NETPLAN_FILE="/etc/netplan/00-installer-config.yaml"
    elif [ -f "/etc/netplan/01-netcfg.yaml" ]; then
        NETPLAN_FILE="/etc/netplan/01-netcfg.yaml"
    else
        NETPLAN_FILE="/etc/netplan/01-network-config.yaml"
    fi
fi

echo ""
echo "Creating fixed netplan configuration in $NETPLAN_FILE..."

# Convert space-separated DNS to yaml array format
DNS_YAML=""
for dns in $DNS_SERVERS; do
    DNS_YAML="$DNS_YAML          - $dns\n"
done

# Create the fixed configuration
cat << EOF | sudo tee $NETPLAN_FILE
network:
  version: 2
  renderer: networkd
  ethernets:
    $PRIMARY_IFACE:
      addresses:
        - $STATIC_IP
      routes:
        - to: default
          via: $GATEWAY
      nameservers:
        addresses:
$(echo -e "$DNS_YAML" | sed '$ s/\\n$//')
      dhcp4: false
      dhcp6: false
EOF

# Disable other potentially conflicting configs
echo ""
echo "Disabling potentially conflicting configurations..."

# Disable cloud-init network config
if [ -f "/etc/netplan/50-cloud-init.yaml" ] && [ "$NETPLAN_FILE" != "/etc/netplan/50-cloud-init.yaml" ]; then
    sudo mv /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.disabled 2>/dev/null || true
fi

# If NetworkManager config exists and we're not using it, adjust it
if [ -f "/etc/netplan/01-network-manager-all.yaml" ] && [ "$NETPLAN_FILE" != "/etc/netplan/01-network-manager-all.yaml" ]; then
    # Keep NetworkManager only for wifi
    cat << EOF | sudo tee /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
  wifis: {}
EOF
fi

# Apply the configuration
echo ""
echo "Applying network configuration..."
sudo netplan apply

echo ""
echo "Waiting for network to settle..."
sleep 3

# Show final configuration
echo ""
echo "=== Final Configuration ==="
echo "IP addresses on $PRIMARY_IFACE:"
ip addr show $PRIMARY_IFACE | grep "inet "

echo ""
echo "Routing table:"
ip route | grep -E "default|$PRIMARY_IFACE"

echo ""
echo "Network configuration has been fixed!"
echo "The system now has only the static IP $STATIC_IP on $PRIMARY_IFACE"
echo ""
echo "You can copy this script to other servers with the same issue."