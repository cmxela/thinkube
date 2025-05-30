#!/bin/bash
# Remove secondary IP address from eno1

echo "Removing secondary IP address 192.168.1.48 from eno1..."

# Check current IPs
echo "Current IP addresses on eno1:"
ip addr show eno1 | grep inet

# Remove the secondary IP
sudo ip addr del 192.168.1.48/24 dev eno1

echo ""
echo "IP addresses after removal:"
ip addr show eno1 | grep inet

echo ""
echo "Done. The secondary IP has been removed."
echo "Note: This is temporary. To make it permanent, check your netplan configuration."