# Implement GitHub Issue #$ARGUMENTS

Please implement issue #$ARGUMENTS from the thinkube repository following this strict process:

## Project Structure Reference

Common paths and files you'll need:
- **Inventory**: `/home/thinkube/thinkube/inventory/inventory.yaml`
- **Group variables**: `/home/thinkube/thinkube/inventory/group_vars/`
- **Host variables**: `/home/thinkube/thinkube/inventory/host_vars/`
- **Reference playbooks**: `/home/thinkube/thinkube/thinkube-core/playbooks/`
- **40_thinkube directory**: `/home/thinkube/thinkube/ansible/40_thinkube/`
- **Architecture docs**: `/home/thinkube/thinkube/docs/architecture-k8s/`
- **CLAUDE.md**: `/home/thinkube/thinkube/CLAUDE.md` (project conventions)
- **Thinkube-core CLAUDE.md**: `/home/thinkube/thinkube/thinkube-core/CLAUDE.md` (reference conventions)

Common variables to check in inventory:
- `domain_name`, `k8s_domain`, `registry_domain`
- `system_username`, `admin_username` 
- `lan_ip`, `zerotier_ip`
- `ssl_cert_dir`, `tls_crt_path`, `tls_key_path`
- `vault_cf_token` (for Cloudflare)
- `kubectl_bin`, `helm_bin`, `kubeconfig`

## Implementation Process Checklist

1. **Issue Analysis**
   - [ ] Read the GitHub issue #$ARGUMENTS completely
   - [ ] Identify all reference implementation URLs mentioned in the issue
   - [ ] List the issue requirements explicitly
   - [ ] Check for missing inventory variables or environment variables

2. **Reference Review**
   - [ ] Check `/home/thinkube/thinkube/docs/architecture-k8s/MIGRATION_MAPPING_CORRECTED.md` for component mapping
   - [ ] If migration from thinkube-core, check source playbooks in `/home/thinkube/thinkube/thinkube-core/playbooks/`
   - [ ] Analyze the reference implementation line-by-line
   - [ ] Document what features ARE in the reference
   - [ ] Document what features ARE NOT in the reference (to avoid adding them)
   - [ ] Note any hardcoded values that need to become variables

3. **Environment Preparation**
   - [ ] Create component directory: `/home/thinkube/thinkube/ansible/40_thinkube/[category]/[component]/`
   - [ ] Check inventory for required variables
   - [ ] Note any missing environment variables (like CLOUDFLARE_TOKEN)
   - [ ] Verify dependencies are met (check issue dependencies section)

4. **Implementation**
   - [ ] Create test playbook first (`18_test_[component].yaml`)
   - [ ] Create deployment playbook (`10_deploy_[component].yaml`)
   - [ ] Create rollback playbook (`19_rollback_[component].yaml`)
   - [ ] Follow numbering convention from `/home/thinkube/thinkube/docs/architecture-k8s/PLAYBOOK_STRUCTURE.md`
   - [ ] Use FQCN for all modules (ansible.builtin.*, kubernetes.core.*)
   - [ ] Don't use `become: true` at playbook level
   - [ ] Follow variable conventions from CLAUDE.md

5. **Testing**
   - [ ] Test the implementation as specified
   - [ ] Fix any issues while maintaining reference compliance
   - [ ] Verify all tests pass
   - [ ] Check resource limits are configured

6. **Documentation**
   - [ ] Update component README.md
   - [ ] Document any new variables needed
   - [ ] Note if environment variables are required
   - [ ] Update PR #37 if on infrastructure branch

## IMPORTANT RULES
- Always explicitly state: "Checking reference from [URL]" or "Checking reference from [FILE]"
- Always list: "Reference includes: [features]" and "Reference excludes: [features]" 
- Never add functionality not in the reference without explicit discussion
- If you think something is missing, ask: "Reference doesn't include X, should I add it?"
- Check both project CLAUDE.md files for conventions
- Maintain consistency with existing variable naming in inventory

Begin by fetching and analyzing issue #$ARGUMENTS.