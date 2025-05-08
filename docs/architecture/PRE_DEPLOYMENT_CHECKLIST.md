# Pre-deployment Checklist

This document provides a minimal checklist of requirements before deploying Thinkube. The setup scripts and deployment playbooks will handle most of the software installation and configuration automatically.

## Essential Hardware Requirements

- [ ] At least 2 Ubuntu 24.04 machines:
  - [ ] **Control Server/Desktop**: 16GB+ RAM, 8+ CPU cores, 500GB+ storage
  - [ ] **Worker Server/Desktop**: 16GB+ RAM, 8+ CPU cores, 500GB+ storage
  - [ ] For AI workloads: NVIDIA GPUs installed (optional but recommended)

## Network Configuration

- [ ] Fixed/static IP addresses configured on all machines
- [ ] All machines connected to the same local network
- [ ] Internet access available on all machines for package installation

That's it! The setup script and deployment playbooks will handle everything else, including:

- Installing SSH server if needed (not installed by default on Ubuntu Desktop)
- Setting up SSH keys between machines
- Installing required packages and dependencies
- Configuring environment variables
- Setting up LXD and virtual machines
- Configuring overlay networking
- Installing and configuring Kubernetes
- Deploying all necessary applications

To start the deployment after meeting these minimal requirements, simply follow the instructions in the README.md file. The setup script will check for and install any missing prerequisites automatically.

## Next Steps

After ensuring your hardware and network meet the requirements:

1. Clone the repository on your control machine
2. Follow the setup instructions in README.md
3. The deployment will guide you through the rest of the process