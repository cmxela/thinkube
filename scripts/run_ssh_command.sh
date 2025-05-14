#!/bin/bash
# Script to run SSH commands on remote hosts with proper authentication
# Usage: ./scripts/run_ssh_command.sh <host> <command>

set -e  # Exit on error

# Check for required arguments
if [ $# -lt 2 ]; then
  echo "ERROR: Missing required arguments"
  echo "Usage: $0 <host> <command>"
  echo "Example: $0 bcn1 'lxc cluster list'"
  exit 1
fi

HOST="$1"
shift
COMMAND="$@"  # All remaining arguments

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

# If ANSIBLE_SSH_PASS is not set, use ANSIBLE_SUDO_PASS
if [ -z "$ANSIBLE_SSH_PASS" ]; then
  echo "ANSIBLE_SSH_PASS not set, using ANSIBLE_SUDO_PASS for SSH authentication"
  export ANSIBLE_SSH_PASS="$ANSIBLE_SUDO_PASS"
fi

# Install sshpass if needed
if ! command -v sshpass &> /dev/null; then
  echo "Installing sshpass..."
  sudo apt-get update -qq && sudo apt-get install -qq -y sshpass
fi

# Determine if the command needs sudo (by explicitly checking)
needs_sudo=false
if [[ "$COMMAND" == "sudo "* || "$COMMAND" == *"reboot"* || "$COMMAND" == *"shutdown"* || "$COMMAND" == *"apt"* || "$COMMAND" == *"systemctl"* ]]; then
  needs_sudo=true
  # If command already has sudo, remove it as we'll add it with proper options
  if [[ "$COMMAND" == "sudo "* ]]; then
    COMMAND="${COMMAND#sudo }"
  fi
  echo "Command requires sudo privileges"
fi

# Use sshpass to handle SSH password authentication
echo "Executing command on $HOST..."

if $needs_sudo; then
  # Prepare a command that pipes the sudo password to sudo
  SUDO_COMMAND="echo '$ANSIBLE_SUDO_PASS' | sudo -S $COMMAND"
  
  # Use sshpass to handle the SSH password
  sshpass -p "$ANSIBLE_SSH_PASS" ssh -o StrictHostKeyChecking=no "thinkube@$HOST" "$SUDO_COMMAND"
else
  # Run command without sudo
  sshpass -p "$ANSIBLE_SSH_PASS" ssh -o StrictHostKeyChecking=no "thinkube@$HOST" "$COMMAND"
fi

# Capture the exit code
EXIT_CODE=$?

echo "Command completed with exit code: $EXIT_CODE"

exit $EXIT_CODE