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

2. **Storage Pool Issues**:
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