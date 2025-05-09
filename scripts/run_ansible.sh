#!/bin/bash
# Script to run Ansible playbooks with proper environment variables
# Usage: ./scripts/run_ansible.sh ansible/path/to/playbook.yaml [additional ansible options]

set -e  # Exit on error

# Source environment variables
if [ -f "$HOME/.env" ]; then
  echo "Loading environment variables from $HOME/.env"
  source "$HOME/.env"
else
  echo "ERROR: $HOME/.env file not found!"
  exit 1
fi

# Check for required environment variables
if [ -z "$ANSIBLE_SUDO_PASS" ]; then
  echo "ERROR: ANSIBLE_SUDO_PASS environment variable not set!"
  exit 1
fi

# Export environment variables for Ansible
export ANSIBLE_BECOME_PASSWORD="$ANSIBLE_SUDO_PASS"
export ANSIBLE_SUDO_PASS

# Set up authentication - this is critical for remote access
if [ -n "$ANSIBLE_SSH_PASS" ]; then
  echo "Using ANSIBLE_SSH_PASS for SSH authentication"
  
  # Make sure we have sshpass installed
  if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    sudo apt-get update -qq && sudo apt-get install -qq -y sshpass
  fi
  
  # Use direct approach with Ansible variables
  export ANSIBLE_HOST_KEY_CHECKING=False
  
  # Will add SSH variables to the vars file later, after it's created
  SSH_AUTH_CONFIGURED=true
  
  echo "SSH password authentication will be configured via ansible_ssh_pass variable"
else
  echo "WARNING: ANSIBLE_SSH_PASS not set, using SSH keys for authentication"
  if [ -z "$SSH_AUTH_SOCK" ] || ! ssh-add -l &>/dev/null; then
    echo "WARNING: No SSH keys loaded in agent, authentication may fail"
  fi
  SSH_AUTH_CONFIGURED=false
fi

# Check if playbook argument is provided
if [ -z "$1" ]; then
  echo "ERROR: No playbook specified"
  echo "Usage: $0 ansible/path/to/playbook.yaml [additional options]"
  exit 1
fi

PLAYBOOK="$1"
shift  # Remove first argument

# Create a temporary vars file for authentication
TEMP_VARS="/tmp/ansible-vars-$$.yml"
cat > "$TEMP_VARS" << EOF
---
ansible_become_pass: "$ANSIBLE_SUDO_PASS"
EOF

# Add SSH authentication if configured
if [ "$SSH_AUTH_CONFIGURED" = true ]; then
  cat >> "$TEMP_VARS" << EOF
ansible_ssh_pass: "$ANSIBLE_SSH_PASS"
ansible_user: "thinkube"
EOF
fi

# Display execution info
echo "Running playbook: $PLAYBOOK"
echo "With environment: ANSIBLE_SUDO_PASS=*** ANSIBLE_SSH_PASS=***"
echo "Additional options: $@"
echo

# Execute playbook with extra vars
ansible-playbook -i inventory/inventory.yaml "$PLAYBOOK" -e "@$TEMP_VARS" "$@"
RESULT=$?

# Clean up temporary files
rm -f "$TEMP_VARS"

# Report status
if [ $RESULT -eq 0 ]; then
  echo "Playbook execution completed successfully"
else
  echo "Playbook execution failed with error code $RESULT"
  exit $RESULT
fi