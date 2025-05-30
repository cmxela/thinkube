#!/bin/bash
# Add local servers to /etc/hosts

echo "Adding local servers to /etc/hosts..."

# Check if entries already exist
if ! grep -q "192.168.1.101.*bcn1" /etc/hosts; then
    echo "192.168.1.101   bcn1" | sudo tee -a /etc/hosts
fi

if ! grep -q "192.168.1.102.*bcn2" /etc/hosts; then
    echo "192.168.1.102   bcn2" | sudo tee -a /etc/hosts
fi

echo ""
echo "Current /etc/hosts entries:"
grep -E "bcn1|bcn2" /etc/hosts

echo ""
echo "Testing name resolution:"
ping -c 1 bcn1
ping -c 1 bcn2