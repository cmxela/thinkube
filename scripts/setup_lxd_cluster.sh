#!/bin/bash
# setup_lxd_cluster.sh - A script to set up LXD cluster manually

set -e

# Configuration
LXD_TRUST_PASSWORD="thinkube-lxd-cluster"
BCN1_IP=$(ip -4 addr show br0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
BCN2_IP="192.168.1.102"
CLUSTER_PORT=8443

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====== LXD Cluster Setup Script ======${NC}"

# Get server name
SERVER_NAME=$(hostname)
echo -e "${GREEN}Current server: ${SERVER_NAME}${NC}"

# Check if we're on the bootstrap node (bcn1)
if [ "$SERVER_NAME" == "bcn1" ]; then
    echo -e "${GREEN}This is the bootstrap node...${NC}"
    
    # We will do a complete reset of LXD
    
    # Do a thorough cleanup of LXD
    echo -e "${YELLOW}Completely removing LXD...${NC}"
    # First stop LXD
    sudo snap stop lxd || true
    # Remove the snap
    sudo snap remove lxd || true
    # Clean up any left over data directories
    sudo rm -rf /var/snap/lxd || true
    sleep 3
    
    # Reinstall LXD from snap
    echo -e "${YELLOW}Reinstalling LXD...${NC}"
    sudo snap install lxd || true
    sleep 10
    
    # First initialize LXD with basic configuration
    echo -e "${YELLOW}Initializing LXD with basic configuration...${NC}"
    
    # Basic init with auto settings
    lxd init --auto
    
    # Set the https address and trust password
    echo -e "${YELLOW}Setting network and trust password...${NC}"
    lxc config set core.https_address ${BCN1_IP}:${CLUSTER_PORT}
    lxc config set core.trust_password "${LXD_TRUST_PASSWORD}"
    
    # Now explicitly enable clustering
    echo -e "${YELLOW}Enabling clustering...${NC}"
    lxc cluster enable ${SERVER_NAME}
    
    # Wait a moment for the cluster to initialize
    sleep 5
    
    echo -e "${GREEN}Bootstrap node initialization completed${NC}"
    
    # Wait for LXD to stabilize
    sleep 10
    
    # Create profiles
    echo -e "${YELLOW}Creating VM profiles...${NC}"
    
    # Create VM networks profile
    lxc profile create vm-networks || echo "Profile already exists"
    cat <<EOF | lxc profile edit vm-networks
name: vm-networks
description: "Network configuration for VMs"
config:
  security.nesting: "true"
devices:
  eth0:
    name: eth0
    nictype: bridged
    parent: lxdbr0
    type: nic
  eth1:
    name: eth1
    nictype: bridged
    parent: br0
    type: nic
EOF
    
    # Create VM resources profile
    lxc profile create vm-resources || echo "Profile already exists"
    cat <<EOF | lxc profile edit vm-resources
name: vm-resources
description: "Resource limits for VMs"
config:
  limits.cpu: "4"
  limits.memory: "4GB"
  limits.memory.enforce: "hard"
  security.secureboot: "false"
  boot.autostart: "true"
devices: {}
EOF
    
    # Create VM GPU profile
    lxc profile create vm-gpu || echo "Profile already exists"
    cat <<EOF | lxc profile edit vm-gpu
name: vm-gpu
description: "GPU passthrough for VMs"
config:
  nvidia.driver.capabilities: "all"
  nvidia.runtime: "true"
devices: {}
EOF
    
    # Generate a join token for bcn2
    echo -e "${YELLOW}Generating cluster join token for bcn2...${NC}"
    JOIN_TOKEN=$(lxc cluster add bcn2)
    
    # Display the join command to run on bcn2
    echo -e "${YELLOW}To join bcn2 to the cluster, run this command on bcn2:${NC}"
    echo -e "${GREEN}${JOIN_TOKEN}${NC}"
    
    # Also save the token to a file for reference
    echo "${JOIN_TOKEN}" > ${HOME}/bcn2_join_token.txt
    echo -e "${YELLOW}The join token has been saved to ${HOME}/bcn2_join_token.txt${NC}"
    echo -e "${YELLOW}This token is valid for 24 hours or until used once.${NC}"
    
    echo -e "${GREEN}Bootstrap node setup complete.${NC}"
    echo -e "${YELLOW}Make sure to run the cluster join command on bcn2 as shown above.${NC}"
    
else
    # Member node (bcn2)
    echo -e "${GREEN}This is a member node...${NC}"
    
    # Do a thorough cleanup of LXD on the member node
    echo -e "${YELLOW}Completely removing LXD...${NC}"
    # First stop LXD
    sudo snap stop lxd || true
    # Remove the snap
    sudo snap remove lxd || true
    # Clean up any left over data directories
    sudo rm -rf /var/snap/lxd || true
    sleep 3
    
    # Reinstall LXD from snap
    echo -e "${YELLOW}Reinstalling LXD...${NC}"
    sudo snap install lxd || true
    sleep 10
    
    # Prepare for cluster join
    echo -e "${YELLOW}Preparing to join the cluster...${NC}"
    
    # Create a simple preseed for the member node
    cat <<EOF > /tmp/lxd_join_preseed.yaml
config:
  core.https_address: ${BCN2_IP}:${CLUSTER_PORT}
  core.trust_password: ${LXD_TRUST_PASSWORD}
EOF

    # Initialize with basic config first
    cat /tmp/lxd_join_preseed.yaml | lxd init --preseed
    
    # Ask user to paste the join token
    echo -e "${YELLOW}Please paste the join token generated on bcn1:${NC}"
    read -r JOIN_COMMAND
    
    # Join the cluster using the token
    echo -e "${YELLOW}Joining the cluster...${NC}"
    echo -e "${YELLOW}Executing the join command...${NC}"
    eval "${JOIN_COMMAND}"
    
    echo -e "${GREEN}Member node joined the cluster. Wait for sync...${NC}"
    sleep 10
    
    # Verify cluster status
    lxc cluster list
fi

# List profiles
echo -e "${YELLOW}LXD profiles:${NC}"
lxc profile list

# Verify cluster state
echo -e "${YELLOW}Cluster status:${NC}"
lxc cluster list || echo "Not in a cluster"

echo -e "${GREEN}====== LXD Cluster Setup Complete ======${NC}"