#!/bin/bash
# Test script for direct SSH with Ansible
set -e

# Test direct SSH first
echo "Testing direct SSH connection to bcn2..."
ssh -o StrictHostKeyChecking=no bcn2 "echo SSH connection successful"

# Test Ansible ping
echo
echo "Testing Ansible ping to bcn2..."
ansible bcn2 -m ping -i inventory/inventory.yaml

echo
echo "If both tests passed, SSH works but Ansible configuration may have issues."
echo "Try setting 'ansible_ssh_extra_args' in inventory.yaml for bcn2."