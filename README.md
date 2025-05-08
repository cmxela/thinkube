# Thinkube

## Deployment Process Overview

Setting up Thinkube involves these key steps:

1. **Initial Setup**: Install tools and clone the repository
2. **Network Configuration**: Set up fixed IP addresses on servers
3. **SSH Configuration**: Establish passwordless SSH access between servers
4. **Deployment**: Run the Ansible playbooks to deploy services

Follow the instructions in this README to complete these steps in order.

## Deployment Prerequisites

Before starting the deployment process, you need:

1. Two Ubuntu 24.04.2 systems (bcn1 and bcn2) with:
   - sudo access on both machines
   - Internet access for package installation
   - GitHub Personal Access Token with proper permissions

Note: All scripts will automatically install necessary packages if they are not already present.

## Initial Setup

### GitHub Setup and Tools Installation

Generate a GitHub Personal Access Token with these permissions:
- `repo` (Full control of private repositories)
- `admin:ssh_signing_key` (Manage SSH signing keys)
- `admin:public_key` (Manage public keys)

Then copy and paste this script into your terminal to set up your Thinkube environment:

```bash
cat > setup_thinkube.sh << 'EOFSCRIPT'
#!/bin/bash
# Thinkube Setup Script

# Prompt for GitHub credentials
echo "Please enter your GitHub information:"
read -p "GitHub Username: " GITHUB_USER
read -p "GitHub Email: " GITHUB_EMAIL
read -sp "GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GitHub token is required"
  exit 1
fi

# Save credentials to .env file
mkdir -p "$HOME/.config/thinkube"
cat > ~/.env << EOF
# Thinkube Environment Variables
# Generated on $(date)

# GitHub Configuration
GITHUB_TOKEN="${GITHUB_TOKEN}"
GITHUB_USER="${GITHUB_USER}"
GITHUB_EMAIL="${GITHUB_EMAIL}"
EOF

chmod 600 ~/.env
echo "Credentials saved to ~/.env"

# Install required packages
echo "Installing required packages..."
sudo apt update

# Install git if needed
if ! command -v git &> /dev/null; then
  echo "Git not found. Installing git..."
  sudo apt install -y git
fi

# Install curl if needed
if ! command -v curl &> /dev/null; then
  echo "Curl not found. Installing curl..."
  sudo apt install -y curl
fi

# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Define a specific key name for Thinkube deployment
KEY_FILE=~/.ssh/thinkube_deploy_key
HOSTNAME=$(hostname)

# Generate SSH key if it doesn't exist
if [ ! -f "$KEY_FILE" ]; then
  ssh-keygen -t ed25519 -C "${GITHUB_EMAIL}" -f "$KEY_FILE" -N ""
  echo "SSH key generated at $KEY_FILE"
else
  echo "SSH key already exists at $KEY_FILE"
fi

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add "$KEY_FILE"

# Add SSH key to GitHub
KEY_TITLE="Thinkube-Deployment-Key-${HOSTNAME}"
KEY_CONTENT=$(cat "${KEY_FILE}.pub")

echo "Adding SSH key to GitHub with title: $KEY_TITLE"
RESPONSE=$(curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user/keys \
     -d "{\"title\":\"$KEY_TITLE\",\"key\":\"$KEY_CONTENT\"}")

if echo "$RESPONSE" | grep -q "message"; then
  # Check if the key is already in use
  if echo "$RESPONSE" | grep -q "key is already in use"; then
    echo "SSH key is already registered with GitHub. Continuing..."
  else
    # For any other GitHub API error
    echo "Error adding key to GitHub:"
    echo "$RESPONSE" | grep "message"
    echo "Continuing anyway, but you may need to add the key manually later."
  fi
else
  echo "Key successfully added to GitHub"
fi

# Configure SSH to use specific key for GitHub
if ! grep -q "Host github.com" ~/.ssh/config 2>/dev/null; then
  cat >> ~/.ssh/config << EOF
Host github.com
  User git
  IdentityFile $KEY_FILE
  IdentitiesOnly yes
EOF
  echo "SSH config updated for GitHub"
fi

# Setup Git configuration
git config --global user.name "${GITHUB_USER}"
git config --global user.email "${GITHUB_EMAIL}"

# Clone the repository
echo "Cloning the Thinkube repository..."
REPO_DIR="$HOME/thinkube"
REPO_URL="github.com:cmxela/thinkube"

if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning from git@${REPO_URL}.git to $REPO_DIR"
  git clone git@${REPO_URL}.git "$REPO_DIR"
  
  # Check if the clone was successful
  if [ $? -eq 0 ]; then
    echo "Repository cloned to $REPO_DIR"
    
    # Run the tools installation script if it exists
    if [ -f "$REPO_DIR/scripts/10_install-tools.sh" ]; then
      echo "Installing Ansible and other required tools..."
      cd "$REPO_DIR"
      bash ./scripts/10_install-tools.sh
      
      # Activate the Python virtual environment if it exists
      if [ -f "$HOME/.venv/bin/activate" ]; then
        source "$HOME/.venv/bin/activate"
        echo "Python virtual environment activated with Ansible $(ansible --version | head -n1)"
      else
        echo "Python virtual environment not found at $HOME/.venv/bin/activate"
      fi
    else
      echo "Tools installation script not found at $REPO_DIR/scripts/10_install-tools.sh"
    fi
  else
    echo "Failed to clone repository. Please check your access rights."
    echo "You can try to manually clone it later with: git clone git@${REPO_URL}.git $REPO_DIR"
  fi
else
  echo "Repository directory already exists at $REPO_DIR"
fi

# Make sure environment variables are available
if ! grep -q "Load Thinkube environment" ~/.bashrc; then
  cat >> ~/.bashrc << EOF

# Load Thinkube environment
if [ -f "$HOME/.env" ]; then
  export \$(grep -v '^#' $HOME/.env | xargs)
fi
EOF
  echo "Environment variables added to .bashrc"
  source ~/.bashrc
else
  echo "Thinkube environment already configured in .bashrc"
fi

echo "Initial setup complete!"
echo "Next, configure network settings on all servers."
EOFSCRIPT

chmod +x setup_thinkube.sh
./setup_thinkube.sh
```

## Network Configuration for Baremetal Servers

After completing the initial setup, configure fixed IP addresses on your Ubuntu 24.04 baremetal servers:

1. Export the fixed IP address you want to configure:

```bash
export FIX_IP=192.168.1.101  # For bcn1 (Desktop)
# OR
export FIX_IP=192.168.1.102  # For bcn2 (Headless Server)
```

2. Run this script to configure the network (same for any server):

```bash
cat > setup_network.sh << 'EOFSCRIPT'
#!/bin/bash
# Thinkube Network Configuration Script

# Prompt for IP address if not provided
if [ -z "$FIX_IP" ]; then
  read -p "Enter fixed IP address (e.g., 192.168.1.101): " FIX_IP
  
  if [ -z "$FIX_IP" ]; then
    echo "Error: Fixed IP address is required"
    exit 1
  fi
fi

echo "Setting up fixed IP: $FIX_IP"

# Detect primary interface
ROUTE_INFO=$(ip route get 8.8.8.8 2>/dev/null)
if [ $? -ne 0 ]; then
  echo "Error: Cannot determine network route. Make sure you have internet connectivity."
  exit 1
fi

IFACE=$(echo "$ROUTE_INFO" | grep -oP 'dev \K\S+')
GATEWAY=$(echo "$ROUTE_INFO" | grep -oP 'via \K\S+')

if [ -z "$IFACE" ]; then
  echo "Error: Could not detect network interface."
  exit 1
fi

echo "Detected interface: $IFACE"
echo "Detected gateway: $GATEWAY"
echo "Setting fixed IP: $FIX_IP"

# Backup current IP information
ip addr show > /tmp/ip_addr_backup.txt
echo "IP configuration backed up to /tmp/ip_addr_backup.txt"

# Create netplan configuration with proper permissions
NETPLAN_CONFIG="/etc/netplan/01-thinkube-config.yaml"

# Create the file content in a temporary file
TMP_NETPLAN_CONFIG=$(mktemp)
cat > $TMP_NETPLAN_CONFIG << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $IFACE:
      dhcp4: no
      addresses:
        - $FIX_IP/24
      routes:
        - to: default
          via: $GATEWAY
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
EOF

# Use sudo to copy the file with correct permissions from the start
sudo cp $TMP_NETPLAN_CONFIG $NETPLAN_CONFIG
sudo chmod 600 $NETPLAN_CONFIG
sudo chown root:root $NETPLAN_CONFIG
rm $TMP_NETPLAN_CONFIG

# Also check and fix permissions on any other netplan config files
for config in /etc/netplan/*.yaml; do
  echo "Setting secure permissions on $config"
  sudo chmod 600 "$config"
  sudo chown root:root "$config"
done

# Apply configuration
echo "Applying netplan configuration..."
sudo netplan apply

# Verify IP configuration
echo "IP configuration applied. Current status:"
ip addr show dev $IFACE | grep "inet "

echo "Fixed IP configuration complete!"
EOFSCRIPT

chmod +x setup_network.sh
```

## SSH Configuration

After configuring fixed IP addresses and installing Ansible, set up passwordless SSH access between servers:

```bash
# Run this from your management node (bcn1)
cd ~/thinkube
# Option 1: Using interactive prompts for passwords
ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/10_setup_ssh_keys.yaml --ask-pass --ask-become-pass

# Option 2: Using environment variables (more convenient for automation)
export ANSIBLE_SUDO_PASS='your_sudo_password'
ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/10_setup_ssh_keys.yaml --ask-pass
```

This playbook will:
1. Generate SSH keys on all servers
2. Distribute public keys between all hosts
3. Create proper SSH config files
4. Test the connections

You'll be prompted once for the SSH password of the remote servers.

After configuring SSH, extract environment variables from your inventory:

```bash
ansible-playbook -i inventory/inventory.yaml ansible/00_initial_setup/20_setup_env.yaml
```

## Continuing the Deployment

After completing the initial setup, the deployment process continues with:

1. Setting up LXD containers
2. Configuring network bridges and ZeroTier
3. Installing MicroK8s and Hashicorp Vault
4. Deploying platform services like Keycloak, Harbor, and PostgreSQL
5. Installing application services

For a complete deployment guide, see the [DEPLOYMENT.md](DEPLOYMENT.md) file.
