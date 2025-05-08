# DEPRECATED: Container-Based Networking Configuration

⚠️ **DEPRECATED** ⚠️

This directory contains the obsolete container-based networking approach. The playbooks have been moved to `/ansible/obsolete/30_networking/`.

Please use the VM-based deployment approach instead, located in `/ansible/vm_deployment/`. The VM-based approach includes networking configuration for ZeroTier and DNS in the following playbooks:

- `30_setup_zerotier.yaml`: Configure ZeroTier networking for VMs
- `60_setup_coredns.yaml`: Configure CoreDNS for proper DNS resolution

See the `MICROK8S_MIGRATION.md` document for details on the migration from container-based to VM-based deployment.