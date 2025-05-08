# LXD Role

This Ansible role installs and configures LXD on target hosts, sets up storage backends, and prepares the system for MicroCloud deployment. The role includes strict validation to ensure successful deployment and proper resource allocation.

## Requirements

- Ubuntu Noble (24.04) only
- Ansible 2.9+
- Hosts must be connected via ZeroTier (setup using the ZeroTier role)
- Sufficient disk space for ZFS storage pools

This role is specifically designed for homogeneous Ubuntu Noble environments, including DGX systems running DGX OS (which is equivalent to Ubuntu Noble).

## Environment Variables

The role can use the following environment variables (typically set in your `.env` file):

| Environment Variable | Description | Default |
|------------|-------------|---------|
| `LXD_STORAGE_POOL` | Name of the primary storage pool | default |
| `LXD_STORAGE_DRIVER` | Storage driver (zfs, dir, btrfs, lvm) | zfs |
| `LXD_CEPH_POOL_SIZE` | Size of Ceph storage pool (for MicroCloud) | 500GB |
| `LXD_ZFS_POOL_SIZE` | Size of ZFS storage pool | 80% |
| `LXD_PASSWORD` | Password for LXD remote authentication | None (required) |
| `LXD_BCN1_LOCAL_STORAGE` | Size of local storage on bcn1 | 300GB |
| `LXD_BCN2_LOCAL_STORAGE` | Size of local storage on bcn2 | 750GB |

## Required Variables

If not using environment variables, the following variables **must** be defined in your vault file:

| Variable | Description | Required |
|----------|-------------|----------|
| `lxd_password` | The password for LXD remote authentication | Yes |

## Optional Variables

These variables have defaults but can be overridden:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `lxd_storage_pool` | Main storage pool name | `default` | No |
| `lxd_storage_driver` | Storage backend driver | `zfs` | No |
| `lxd_address` | LXD API address | `[::]:8443` | No |
| `lxd_network_name` | LXD network bridge name | `lxdbr0` | No |
| `lxd_network_ipv4_address` | LXD network IPv4 CIDR | `auto` | No |
| `lxd_network_ipv6_address` | LXD network IPv6 CIDR | `none` | No |
| `lxd_storage_pool_size` | Size of storage pool | From env or `80%` | No |

## Example Usage

```yaml
- hosts: all
  become: yes
  vars_files:
    - group_vars/all/vault.yml
  roles:
    - lxd
```

## Example .env Configuration

```
# LXD configuration
LXD_STORAGE_POOL=default
LXD_STORAGE_DRIVER=zfs
LXD_CEPH_POOL_SIZE=500GB
LXD_ZFS_POOL_SIZE=80%
LXD_TRUST_PASSWORD=your_secure_password
LXD_BCN1_LOCAL_STORAGE=300GB
LXD_BCN2_LOCAL_STORAGE=750GB
```

## Verification Steps

The role includes built-in verification at each step:

1. Validates required variables are defined before starting
2. Validates target is running Ubuntu Noble
3. Confirms LXD installation completed successfully
4. Verifies storage pool creation
5. Confirms network bridge configuration
6. Tests remote authentication

## Failure Points

The role will fail explicitly rather than silently proceeding when:

- Required variables are undefined
- Target is not running Ubuntu Noble (24.04)
- Package installation fails
- Storage setup fails
- Network configuration fails
- Remote authentication fails

## Notes

- The role reads configuration from environment variables (typically loaded from .env file)
- This allows consistent configuration between Ansible and OpenTofu
- ZFS is strongly recommended as the storage backend for performance and reliability
- The role prepares the system for MicroCloud deployment in the next phase
- Use the separate `verify_lxd.yml` playbook to test LXD functionality

## Security Considerations

- The LXD trust password is used for remote authentication and should be kept secure
- LXD API is exposed on all interfaces by default ([::]:8443)
- Consider using a firewall to restrict access to the LXD API