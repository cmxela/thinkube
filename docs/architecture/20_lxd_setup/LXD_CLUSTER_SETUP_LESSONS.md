# LXD Cluster Setup: Lessons Learned

This document captures the challenges, solutions, and approaches tested for setting up LXD clusters in the Thinkube project. It serves as a knowledge base for future implementations and troubleshooting.

## Background

The goal is to create an idempotent Ansible playbook that can reliably set up an LXD cluster across multiple baremetal hosts (specifically bcn1 and bcn2), using bcn2 as the primary node and bcn1 as the secondary node. The playbook must be fully automated without requiring manual intervention.

## 1. Manual Approach (Works)

The following manual steps were successful:

### Primary Node (bcn2):

1. **Reset LXD**:
   ```bash
   sudo snap stop lxd
   sudo rm -rf /var/snap/lxd/common/lxd/*
   sudo snap start lxd
   ```

2. **Initialize Primary Node with preseed**:
   ```bash
   cat > /tmp/lxd_init.yaml << EOF
   config:
     core.https_address: 192.168.1.102:8443
     core.trust_password: thinkube-lxd-cluster
   cluster:
     enabled: true
     server_name: bcn2
   storage_pools:
   - name: default
     driver: dir
   networks:
   - name: lxdbr0
     type: bridge
     config:
       ipv4.address: 192.168.100.1/24
       ipv4.nat: "true"
       ipv6.address: fd42:d2f8:c3f:9338::1/64
       ipv6.nat: "true"
   profiles:
   - name: default
     devices:
       eth0:
         name: eth0
         network: lxdbr0
         type: nic
       root:
         path: /
         pool: default
         type: disk
   EOF
   
   sudo cat /tmp/lxd_init.yaml | sudo lxd init --preseed
   ```

3. **Generate Join Token**:
   ```bash
   sudo lxc cluster add bcn1
   ```
   This command outputs a token that includes a complete join command.

### Secondary Node (bcn1):

1. **Reset LXD**:
   ```bash
   sudo snap stop lxd
   sudo rm -rf /var/snap/lxd/common/lxd/*
   sudo snap start lxd
   ```

2. **Join Cluster Using Interactive Mode**:
   ```bash
   lxd init
   ```
   
   **Interactive Answers:**
   ```
   Would you like to use LXD clustering? (yes/no) [default=no]: yes
   What IP address or DNS name should be used to reach this node? [default=192.168.1.101]: 
   Are you joining an existing cluster? (yes/no) [default=no]: yes
   Do you have a join token? (yes/no/[token]) [default=no]: eyJzZXJ2...
   All existing data is lost when joining a cluster, continue? (yes/no) [default=no]: yes
   ```

## 2. Certificate-Based Approach (Issues)

### Issues Encountered:

1. **Certificate Validation Failures**:
   - Error: `Invalid remote certificate`
   - Attempting to pass the certificate in the preseed file often fails due to formatting issues
   - Escaping newlines and indentation makes this approach fragile
   
2. **Join Token Format Issues**:
   - The token format from `lxc cluster add` can be difficult to parse programmatically
   - It's not easily extractable from the output in a way that works reliably

## 3. Network Configuration Issues

### Issues Encountered:

1. **Missing Network Bridge**:
   - Error: `Failed to update local member network "lxdbr0" in project "default": Failed loading network: Network not found`
   - This occurs when trying to join a cluster without proper network configuration

2. **Interface in DOWN State**:
   - Error: `Network lxdbr0 unavailable on this server`
   - This occurs when VMs try to start but the lxdbr0 interface exists in a DOWN state with NO-CARRIER flag
   - Interface state will show `<NO-CARRIER,BROADCAST,MULTICAST,UP>` with `state DOWN` instead of `<BROADCAST,MULTICAST,UP,LOWER_UP>` with `state UP`

3. **DNS/DHCP Service Failures**:
   - Error: `Failed initializing network: Failed starting: The DNS and DHCP service exited prematurely: exit status 2 (\"dnsmasq: failed to create listening socket for 192.168.100.1: Address already in use\")`
   - This indicates that another process may be binding to the lxdbr0 IP address

4. **Storage Pool Issues**:
   - Error: `Config key "source" is cluster member specific`
   - When joining, specific storage configuration may be required

## 4. Preseed vs. Interactive Mode

### Preseed Issues:
- YAML formatting is sensitive and error-prone
- Certificate and token extraction/formatting is challenging
- Requires careful handling of network and storage configuration

### Interactive Mode Advantages:
- Handles complex configuration automatically
- Accepts the token directly without parsing
- Manages network and storage setup internally

## 5. Command Line Approach

The most reliable approach for automation appears to be:

1. **Primary Node**:
   - Use preseed to set up primary node
   - Generate join token with `lxc cluster add <node>`

2. **Secondary Node**:
   - Use LXD's interactive mode via an expect script or echo piping:
   ```bash
   echo -e "yes\n192.168.1.101\nyes\neyJzZXJ2...\nyes\n" | lxd init
   ```

## 6. Ansible Implementation Best Practices

1. **State Detection**:
   - Always check if nodes are already in cluster before attempting operations
   - Use `lxc cluster list` to verify current state

2. **Reset Procedure**:
   - Always fully stop LXD before resetting
   - Remove all data from `/var/snap/lxd/common/lxd/*`
   - Reset cluster address configuration

3. **Order of Operations**:
   - Primary node must be set up first and fully initialized
   - Wait sufficient time between operations (10-20 seconds) 
   - Secondary nodes must join in sequence

4. **Verification**:
   - Verify successful joins using `lxc cluster list` from primary node
   - Check that all expected nodes are present and show ONLINE status

## 7. Token Approach

The most reliable method found for joining secondary nodes is:

1. Generate a token on the primary node
2. Use interactive mode with predefined answers on the secondary node
3. Verify the join succeeded from the primary node

## 8. Preseed Format for Joining

For joining secondary nodes with preseed mode, the correct format must include:

```yaml
cluster:
  enabled: true
  server_name: bcn1
  server_address: 192.168.1.101:8443  # This node's address and port
  cluster_address: 192.168.1.102:8443  # Primary node's address and port
  cluster_token: "eyJzZXJ2..."
  member_config:
  - entity: storage-pool
    name: default
    key: source
    value: /var/snap/lxd/common/lxd/storage-pools/default  # Absolute path on this node
config:
  core.https_address: 192.168.1.101:8443
  core.trust_password: thinkube-lxd-cluster
# Do NOT include storage_pools section here
```

Critical elements:
- `server_address` must specify this node's address and port
- `cluster_address` must point to the primary node (including port)
- `cluster_token` must contain the full token string
- `member_config` must specify storage pool configuration with the correct path
- `core.https_address` must specify this node's address

### Storage Pool Source Directory

The most critical fix for the "Config key 'source' is cluster member specific" error:

1. **Create Directory Before Joining**: You must create the storage pool directory on the secondary node before running the join operation.
   ```bash
   sudo mkdir -p /var/snap/lxd/common/lxd/storage-pools/default
   ```

2. **Correct Path in member_config**: The `value` for the `source` key must point to the directory you created.
   ```yaml
   member_config:
   - entity: storage-pool
     name: default
     key: source
     value: /var/snap/lxd/common/lxd/storage-pools/default
   ```

3. **Remove storage_pools Section**: Do not include a `storage_pools` section in the preseed file when joining a cluster.

4. **Include server_address Field**: Always include the `server_address` field with this node's address and port.

## 9. Implementation Progress

Our current Ansible implementation:

1. Successfully sets up the primary node with clustering enabled
2. Sets up required profiles (vm-networks, vm-resources, vm-gpu)
3. Generates join tokens for secondary nodes
4. Attempts to join secondary nodes using either:
   - Interactive mode with piped input
   - Preseed with proper token and cluster_address

We're currently addressing the following challenges:
- Reliable token extraction and usage
- Proper handling of network configuration
- Storage pool configuration for secondary nodes

## Recommendations

1. **Prefer Interactive Mode**: Use echo piping to simulate interactive mode for the most reliable joining
2. **Simple Token Handling**: Don't try to parse the token, pass it directly
3. **Complete Reset**: Always perform a complete reset before attempting join operations
4. **Wait Times**: Include sufficient wait times between operations (15+ seconds)
5. **Verification**: Always verify the operation succeeded from both nodes
6. **Cluster Address**: Always explicitly specify the cluster_address parameter
7. **Member Config**: Always include member_config for storage pools

---

This document will be updated as we discover more reliable approaches to LXD cluster setup.

## 10. Network Interface State Discoveries

During our implementation of 10_setup_lxd_cluster.yaml and VM creation, we discovered important facts about LXD network interfaces:

1. **Normal Interface State Behavior**:
   - We initially misinterpreted the lxdbr0 bridge being in DOWN state as a problem
   - According to Ubuntu forums (https://discourse.ubuntu.com/t/lxdbr0-interface-is-down/45442):
     > The state DOWN is normal if no containers/VMs are using the bridge. It will change to state UP once VMs are running on it.
   - This is expected behavior and not an error condition
   - The interface showing `<NO-CARRIER,BROADCAST,MULTICAST,UP>` with `state DOWN` is normal when unused
   - This finding saved significant troubleshooting time

2. **Testing Implications**:
   - Tests for interface state should not fail when interface is DOWN
   - Bridge state should only be checked after VMs are running and using the bridge
   - Test playbooks should document this behavior for future users

3. **Avoiding Unnecessary Fixes**:
   - Scripts like `fix_lxdbr0.sh` are unnecessary in most cases
   - Restarting the LXD service or resetting the bridge is typically not required
   - We removed these "fix" scripts as they were addressing a non-issue

4. **Updated Interface Monitoring Approach**:
   ```bash
   # Check if any VMs are active on the bridge
   num_vms=$(lxc list --format csv | wc -l)

   # Only expect UP state if VMs are present
   if [ $num_vms -gt 0 ]; then
     ip link show lxdbr0 | grep "state UP" || echo "Warning: lxdbr0 interface is DOWN with active VMs"
   else
     echo "No active VMs - lxdbr0 being in DOWN state is normal"
   fi
   ```

## 11. VM Creation and User Setup Lessons

During the implementation of 30_create_vms.yaml, we discovered several important lessons:

1. **Resource Configuration Workflow**:
   - VM resources (CPU, memory, disk) must be configured while VMs are stopped
   - The most reliable sequence is:
     1. Create VM with basic configuration
     2. Stop VM
     3. Apply resource constraints
     4. Start VM with new configuration
   - Trying to change resources while VM is running causes errors

2. **User Creation Shell Script Approach**:
   - We learned that complex user creation commands have quoting issues when used directly
   - The most reliable approach is to:
     1. Create a temporary script file on the host
     2. Copy the script to the VM
     3. Execute it with proper permissions
     4. Remove the temporary script
   - This avoids shell escaping issues and improves reliability

3. **Script Example**:
   ```bash
   # Create user setup script locally
   cat > /tmp/vm_user_setup.sh << 'EOF'
   #!/bin/bash
   USERNAME="thinkube"

   # Create user if not exists
   if ! id -u $USERNAME &>/dev/null; then
     useradd -m -s /bin/bash $USERNAME
   fi

   # Set password and sudo access
   echo "$USERNAME:$USERNAME" | chpasswd
   usermod -aG sudo $USERNAME
   echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME
   chmod 440 /etc/sudoers.d/$USERNAME
   EOF

   # Copy and execute in VM
   lxc file push /tmp/vm_user_setup.sh vm_name/tmp/
   lxc exec vm_name -- bash /tmp/vm_user_setup.sh
   ```

4. **Network Configuration Strategy**:
   - Using netplan for network configuration provides consistency
   - Template-based approach ensures all VMs have identical configuration
   - Static IP addressing prevents DHCP issues
   - Example implementation:
     1. Create temporary netplan files locally
     2. Push to VM configuration directory
     3. Apply using `netplan apply`
     4. Test network configuration

5. **Package Installation Reliability**:
   - Package installation in newly created VMs can be unreliable
   - Implementing retry logic is essential:
   ```bash
   for i in $(seq 1 3); do
     if apt-get update && apt-get install -y package; then
       echo "Success on attempt $i"
       break
     else
       echo "Failed on attempt $i, retrying..."
       sleep 2
     fi
   done
   ```
   - Failure handling should fail the playbook only when all retry attempts are exhausted

6. **VM Creation Verification**:
   - The VM creation process should include a verification step
   - Basic connectivity and user existence verification should be part of the creation playbook
   - More detailed verification should be in the separate test playbook (38_test_vm_creation.yaml)
   - This ensures VMs are ready for subsequent configuration steps

7. **Wait Times**:
   - Adding appropriate wait times after VM creation and restart is critical
   - VM initialization can vary based on host resources and configuration
   - Example implementation with wait_for:
   ```yaml
   - name: Wait for VM to be ready
     ansible.builtin.command: lxc exec {{ vm_name }} -- uname -a
     register: vm_ready
     until: vm_ready.rc == 0
     retries: 30
     delay: 2
   ```

## 12. Modular Playbook Design

Our experience highlighted the importance of proper playbook separation and modular design:

1. **Separation of Concerns**:
   - Break down complex operations into smaller, focused playbooks
   - Each playbook should do one thing well
   - Follow a logical sequence for VM setup: create → network → users → packages

2. **Modular VM Setup Structure**:
   - 30-1_create_base_vms.yaml - Creates the base VM instances
   - 30-2_configure_vm_networking.yaml - Configures VM networking
   - 30-3_configure_vm_users.yaml - Sets up users and SSH in VMs
   - 30-4_install_vm_packages.yaml - Installs packages on VMs

3. **Dedicated Test Playbooks**:
   - 38-1_test_base_vms.yaml - Tests base VM creation
   - 38-2_test_vm_networking.yaml - Tests VM networking
   - 38-3_test_vm_users.yaml - Tests VM user configuration and SSH
   - 38-4_test_vm_packages.yaml - Tests VM package installation

4. **Task File Reusability**:
   - Extract common operations into dedicated task files
   - configure_vm_ssh.yaml - Tasks for SSH installation
   - configure_vm_user.yaml - Tasks for user configuration
   - configure_vm_packages.yaml - Tasks for package installation

5. **Sequential VM Processing**:
   - Process VMs one at a time using include_tasks
   - Prevents one slow/failing VM from blocking others
   - Provides clearer error reporting per VM

6. **Idempotency Design**:
   - Setup playbooks must be idempotent (safe to run multiple times)
   - They should check if resources already exist before creating them
   - This allows for recovery from partially completed runs

7. **Proper Test Isolation**:
   - Tests should be independent and not modify the environment
   - Test playbooks should document expected state, not make changes
   - Failed tests should provide clear information on what's wrong and how to fix it

8. **Numerical Playbook Ordering**:
   - Following the x0-y, x8-y convention for setup and testing is effective
   - This ensures proper workflow between playbooks
   - Example: 30-1_setup → 38-1_test, 30-2_setup → 38-2_test, etc.

9. **Non-Interactive Operations**:
   - Use DEBIAN_FRONTEND=noninteractive for package installations
   - Prevent interactive prompts that would block automation
   - Handle potential interactive steps proactively

10. **Robust Error Handling**:
    - Add proper retry mechanisms for network-dependent operations
    - Implement appropriate timeouts for long-running tasks
    - Validate prerequisites before proceeding with critical operations

These lessons have significantly improved the reliability and maintainability of our LXD setup process by implementing a truly modular and resilient approach to VM creation and configuration.