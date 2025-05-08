# DEPRECATED: Container-Based MicroK8s Deployment

⚠️ **DEPRECATED** ⚠️

This directory contains the obsolete container-based MicroK8s deployment approach. The playbooks have been moved to `/ansible/obsolete/40_core_services/`.

Please use the VM-based deployment approach instead, located in `/ansible/vm_deployment/`. The VM-based approach includes:

- `10_setup_lxd_profiles.yaml`: Create LXD VM profiles
- `20_create_microk8s_vms.yaml`: Create and configure VMs
- `30_setup_zerotier.yaml`: Configure ZeroTier networking
- `40_setup_microk8s.yaml`: Install MicroK8s
- `50_join_workers.yaml`: Join worker nodes
- `60_setup_coredns.yaml`: Configure DNS integration

See the `MICROK8S_MIGRATION.md` document for details on the migration from container-based to VM-based deployment.