#!/bin/bash

# Script to check SSH configuration on bcn1 via ZeroTier

echo "=== Checking SSH and ZeroTier configuration on bcn1 ==="
echo

# First connect to bcn1 via LAN
echo "1. Connecting to bcn1 via LAN (192.168.1.101)..."
ssh -o ConnectTimeout=5 thinkube@192.168.1.101 "
echo 'Connected to bcn1 via LAN'
echo
echo '2. Checking SSH daemon configuration...'
sudo grep -E '^ListenAddress|^Port|^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config || echo 'No specific SSH restrictions found'
echo
echo '3. Checking if SSH is listening on all interfaces...'
sudo ss -tlnp | grep :22
echo
echo '4. Checking ZeroTier interface...'
ip addr show | grep -A 3 zt
echo
echo '5. Checking firewall rules for SSH...'
sudo iptables -L INPUT -n -v | grep -E '22|ssh' || echo 'No specific SSH firewall rules'
echo
echo '6. Checking UFW status...'
sudo ufw status | grep -E '22|SSH' || echo 'UFW not active or no SSH rules'
echo
echo '7. Checking if ZeroTier service is running...'
sudo systemctl status zerotier-one | grep Active
echo
echo '8. Checking ZeroTier network status...'
sudo zerotier-cli listnetworks
echo
echo '9. Checking routing table for ZeroTier...'
ip route | grep zt
"

echo
echo "=== Now attempting direct ZeroTier connection ==="
echo "10. Testing SSH to bcn1 via ZeroTier (192.168.191.10)..."
ssh -v -o ConnectTimeout=5 thinkube@192.168.191.10 "echo 'Successfully connected via ZeroTier!'" 2>&1 | grep -E "debug1:|Connection|connected|refused|timeout"