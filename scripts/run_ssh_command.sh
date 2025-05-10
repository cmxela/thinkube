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

# Create temporary script to execute on the remote host
TEMP_SCRIPT="/tmp/remote_cmd_$$.sh"
cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
# Temporary script to run command with sudo access
if [[ "$COMMAND" == sudo* ]]; then
    # Command already has sudo, use echo to provide password
    echo "$ANSIBLE_SUDO_PASS" | $COMMAND
else
    # Add sudo -S to the command
    echo "$ANSIBLE_SUDO_PASS" | sudo -S $COMMAND
fi
EOF
chmod +x "$TEMP_SCRIPT"

# Set up SSH authentication
if [ -n "$ANSIBLE_SSH_PASS" ]; then
  echo "Using password authentication for SSH"
  
  # Make sure we have sshpass installed
  if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    sudo apt-get update -qq && sudo apt-get install -qq -y sshpass
  fi
  
  # Copy the script to the remote host
  sshpass -p "$ANSIBLE_SSH_PASS" scp -o StrictHostKeyChecking=no "$TEMP_SCRIPT" "thinkube@$HOST:/tmp/remote_cmd.sh"
  
  # Execute the script
  sshpass -p "$ANSIBLE_SSH_PASS" ssh -o StrictHostKeyChecking=no "thinkube@$HOST" "chmod +x /tmp/remote_cmd.sh && /tmp/remote_cmd.sh; rm -f /tmp/remote_cmd.sh"
else
  echo "Using key-based authentication for SSH"
  # Copy the script to the remote host
  scp -o StrictHostKeyChecking=no "$TEMP_SCRIPT" "$HOST:/tmp/remote_cmd.sh"
  
  # Execute the script
  ssh -o StrictHostKeyChecking=no "$HOST" "chmod +x /tmp/remote_cmd.sh && /tmp/remote_cmd.sh; rm -f /tmp/remote_cmd.sh"
fi

# Clean up local temp file
rm -f "$TEMP_SCRIPT"