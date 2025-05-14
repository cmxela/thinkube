# Phase 3: LXD VM Setup Lessons

## Overview

This document captures lessons learned during the implementation of Phase 3 (LXD VM Setup), which focused on creating and configuring LXD virtual machines in a standardized, modular way.

## Challenges and Solutions

### Challenge 1: Long-Running Operations Timing Out
- Root cause: Time-intensive operations (VM creation, package installation) exceeded Ansible's default timeout
- Impact: Playbooks failed mid-execution, leaving systems in undefined states
- Solution: Added async/poll parameters to long-running tasks and retry mechanisms
- Prevention: Break down operations into smaller steps with appropriate timeouts

### Challenge 2: Interactive Package Installation
- Root cause: Some packages (e.g., iptables-persistent) prompt for user input during installation
- Impact: Playbook execution hung indefinitely, waiting for user input
- Solution: Use DEBIAN_FRONTEND=noninteractive for package installations
- Prevention: Test package installations manually first to identify interactive prompts

### Challenge 3: VM SSH Service Configuration
- Root cause: SSH service in VMs failed to start due to missing host keys
- Impact: Unable to connect to VMs via SSH, causing failures in subsequent steps
- Solution: Explicitly generate SSH host keys and verify services start correctly
- Prevention: Add proper verification steps after each critical configuration

### Challenge 4: Monolithic vs. Modular Approach
- Root cause: Initial VM setup playbook tried to do too many things in one execution
- Impact: Difficult to troubleshoot failures and impossible to run steps selectively
- Solution: Split VM setup into modular playbooks (create, network, users, packages)
- Prevention: Design playbooks to follow single responsibility principle from the start

## Methodology Improvements

Based on these challenges, we've refined our methodology:

1. **Modular Playbook Design**: 
   - Each playbook focuses on one specific aspect of VM configuration
   - Playbooks can be run independently in sequence
   - Each build playbook (30-x) has a corresponding test playbook (38-x)

2. **Sequential VM Processing**:
   - Process VMs one at a time using include_tasks
   - Prevents one slow/failing VM from blocking others
   - Provides clearer error reporting per VM

3. **Robust Error Handling**:
   - Add proper retry mechanisms for network-dependent operations
   - Implement appropriate timeouts for long-running tasks
   - Validate prerequisites before proceeding with critical operations

4. **Non-Interactive Installation**:
   - Use DEBIAN_FRONTEND=noninteractive for package installations
   - Split package installations into smaller batches to reduce failure impact
   - Verify package installations explicitly

## Best Practices

New best practices identified during this phase:

1. **Single Responsibility Playbooks**: Each playbook should do one thing well
2. **Build and Test Pattern**: Pair each functional playbook with a dedicated test playbook
3. **Sequential Processing**: Process VMs one at a time to isolate issues
4. **Explicit Error Handling**: Define clear failure conditions and retry mechanisms
5. **Non-Interactive Installations**: Prevent prompts that would block automation
6. **VM-Specific Variables**: Allow per-VM customization through inventory variables
7. **Supporting Task Files**: Extract reusable logic into dedicated task files
8. **Consistent Naming Conventions**: Follow project numbering conventions consistently

## Implementation Notes

The VM setup implementation now follows this structure:

1. VM Creation and Setup (aligned with project numbering convention):
   - 30-1_create_base_vms.yaml - Creates the base VM instances
   - 30-2_configure_vm_networking.yaml - Configures VM networking
   - 30-3_configure_vm_users.yaml - Sets up users and SSH in VMs
   - 30-4_install_vm_packages.yaml - Installs packages on VMs

2. VM Testing:
   - 38-1_test_base_vms.yaml - Tests base VM creation
   - 38-2_test_vm_networking.yaml - Tests VM networking
   - 38-3_test_vm_users.yaml - Tests VM user configuration and SSH
   - 38-4_test_vm_packages.yaml - Tests VM package installation

3. Rollback Operations:
   - 39_rollback_vm_creation.yaml - Rollback for VM creation

4. Supporting Task Files:
   - configure_vm_ssh.yaml - Tasks for SSH installation
   - configure_vm_user.yaml - Tasks for user configuration
   - configure_vm_packages.yaml - Tasks for package installation

This structure ensures:
- Clear separation of responsibilities
- Independent testing of each component
- Ability to retry or rerun specific steps
- Simplified troubleshooting

## Task File Patterns

We identified effective patterns for task files:

1. **VM Configuration Task Files**:
   - Each receives a `current_vm` variable defining which VM to configure
   - Contains all steps needed for one aspect of VM configuration
   - Handles its own error conditions and retries
   - Provides clear status reporting

2. **Retry Mechanisms**:
   - Use retries with increasing delays between attempts
   - Implement different strategies for each retry attempt
   - Add appropriate timeouts to prevent hanging

3. **Verification Steps**:
   - Always verify successful completion of critical operations
   - Test functionality, not just installation status
   - Provide clear status messages

## DNS and Network Considerations

Special attention to networking issues:

1. **DNS Resolution**:
   - Check and fix DNS resolution before package operations
   - Add static /etc/hosts entries when needed
   - Test connectivity to package repositories explicitly

2. **SSH Configuration**:
   - Generate host keys explicitly
   - Verify service status after configuration
   - Test connectivity with appropriate timeouts

3. **Package Installation**:
   - Use non-interactive installation mode
   - Split installations into logical groups
   - Handle package prompts appropriately

## Variable Handling Strategy

Following project guidelines for variable management:

1. **Inventory Variables**:
   - Installation-specific variables defined in inventory
   - VM-specific package lists
   - System username for VMs

2. **Default Variables**:
   - Technical variables defined with defaults in playbooks
   - SSH key types and names
   - Timeout values for operations

3. **Dynamic Variables**:
   - VMs to configure generated from inventory groups
   - Loop variables passed to included tasks

## Conclusion

The modular approach to VM setup has significantly improved maintainability, reliability, and flexibility. By breaking down the process into discrete steps and adding robust error handling, we've created a system that can handle network issues, package installation problems, and VM-specific configurations without sacrificing reliability.

This approach will serve as a model for future infrastructure component implementations, demonstrating how complex operations can be effectively managed through modularity, proper error handling, and clear responsibility separation.