# Thinkube Project Definition

## Overview

Thinkube is a home-based development platform built on Kubernetes, designed specifically for AI applications and agents. This platform enables developers, researchers, and enthusiasts to deploy, test, and run AI workloads in their own environment with minimal setup complexity.

## What We're Building

We are developing the automated deployment system for Thinkube - a sequence of Ansible playbooks that create a complete, functional Kubernetes-based AI development environment with the following characteristics:

## Core Principles

1. **Fully Automated Deployment**: 
   - Complete deployment through a sequence of Ansible playbooks
   - Minimal human intervention required
   - Clear, guided process for the few required manual steps

2. **Reliability**:
   - If the deployment process completes, all subprocesses have completed successfully
   - No silent failures or incomplete configurations
   - Comprehensive checking and validation at each step

3. **Configurability**:
   - Adaptable to different home environments and hardware
   - Clear separation of configuration from implementation
   - Sensible defaults with ability to customize

4. **Completeness**:
   - Deployment results in a fully functional platform
   - No manual fixes or adjustments required post-deployment
   - All services properly integrated and communicating

5. **Resilience**:
   - Handles common failure cases gracefully
   - Provides clear error messages and recovery guidance
   - Designed for home environments with potential network/power disruptions

## Technical Implementation Guidelines

### Playbook Development

1. **Idempotency**:
   - Playbooks must be idempotent (can be run multiple times safely)
   - Running a playbook twice should not break the system
   - Status checks should prevent unnecessary operations

2. **Validation**:
   - Each playbook must validate its actions before completing
   - Include tests to verify services are functioning correctly
   - Use wait_for conditions to ensure services are truly ready

3. **Error Handling**:
   - Provide meaningful error messages
   - Fail early when critical issues are detected
   - Include troubleshooting guidance in error messages

4. **Logical Progression**:
   - Organize playbooks in a logical, numerical sequence
   - Clearly document dependencies between playbooks
   - Design for minimal manual intervention between steps

5. **Documentation**:
   - Document purpose, prerequisites, and expected outcomes
   - Include examples and usage notes
   - Provide troubleshooting guidance for common issues

6. **Performance**:
   - Optimize for typical home environments
   - Balance between speed and reliability
   - Parallelize operations where appropriate

### Repository Structure

The repository should maintain a clean, logical structure that reflects the deployment sequence:

```
/ansible
├── 00_initial_setup      # Host configuration and SSH setup
├── 10_baremetal_infra    # Physical server configuration
├── 20_lxd_setup          # LXD cluster/VM creation and setup
├── 30_networking         # Network configuration (ZeroTier, DNS)
└── 40_thinkube           # All Kubernetes and platform services
    ├── core/             # Essential services (Keycloak, PostgreSQL, etc.)
    └── optional/         # AWX-deployed services (JupyterHub, Prometheus, etc.)
```

Within each directory, playbooks should be numbered to indicate execution order, with increments of 10 to allow for future additions.

## Target Environment

Thinkube is designed to run on home-based hardware with the following minimum specifications:

- Two or more Ubuntu servers (bare metal or proxmox VMs)
- One or more NVIDIA GPUs for AI workloads
- Stable local network with fixed IP addresses
- Internet connectivity for package installation

## Deployment Flow

The complete deployment follows this general flow:

1. Initial setup of servers (SSH keys, environment)
2. Configuration of physical infrastructure (network bridges, GPU passthrough)
3. Creation of LXD VMs for Kubernetes nodes
4. Network configuration (ZeroTier overlay, DNS)
5. Kubernetes (MicroK8s) installation and configuration
6. Core infrastructure deployment (cert-manager, ingress, etc.)
7. Core services deployment (Keycloak, PostgreSQL, Harbor, etc.)
8. Optional services deployment via AWX (JupyterHub, Prometheus, etc.)

Each step is implemented as one or more Ansible playbooks, with clear documentation and error handling.

## Success Criteria

The Thinkube deployment is considered successful when:

1. All services are deployed and properly configured
2. The platform can be accessed through the expected URLs
3. AI workloads can be deployed and executed
4. GPU resources are properly utilized
5. Authentication and authorization are functioning
6. Data persistence is working as expected
7. All validation tests pass

The goal is a completely functional AI development platform that "just works" after following the deployment steps, enabling users to focus on AI development rather than infrastructure.