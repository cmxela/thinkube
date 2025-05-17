# MicroK8s Implementation Lessons Learned

## Phase: Core Infrastructure (CORE-001 and CORE-002)
Date: 2025-05-17

### Key Issues Encountered

#### 1. Reference Implementation Process
**Problem**: Started creating playbooks from scratch instead of using reference implementations from GitHub issues.
- Impact: Wasted time creating custom implementations
- Root Cause: Didn't check issue for reference URLs first

**Solution**: Created custom slash command `/project:implement-issue` to enforce proper process
- Always check GitHub issue for reference URLs first
- Download and analyze reference before implementing
- Only deviate from reference with explicit justification

#### 2. Feature Creep
**Problem**: Added addon installation to worker node playbook when reference didn't include it.
- Impact: Worker nodes tried to manage addons (control plane responsibility)
- Root Cause: Made assumptions instead of following reference

**Solution**: Strict adherence to reference implementation
- Document what IS in reference
- Document what IS NOT in reference
- Don't add features without discussion

#### 3. Network Configuration Confusion
**Problem**: Initial implementation used ZeroTier IP (192.168.100.x) instead of LAN IP for cluster communication.
- Impact: Worker nodes couldn't join cluster due to network isolation
- Root Cause: Misunderstanding of network architecture

**Solution**: Use appropriate network for each service
- MicroK8s cluster: LAN network (br0, 192.168.1.x)
- Management traffic: Can use ZeroTier
- Internal LXD: Uses lxdbr0 (10.229.145.x)

#### 4. Hostname Inconsistency
**Problem**: Baremetal hosts use short names, VMs use FQDNs in Kubernetes.
- Impact: Test playbooks failed to find nodes
- Root Cause: Different hostname configurations between baremetal and VMs

**Solution**: Handle both formats in playbooks
- Use regex patterns to match both short and FQDN
- Check for multiple hostname variations
- Consider standardizing hostnames in future

#### 5. Timeout Handling
**Problem**: Playbooks had insufficient timeout values and poor error handling.
- Impact: Automated deployment would fail unnecessarily
- Root Cause: Not planning for real-world delays

**Solution**: Robust timeout and retry logic
- Check if nodes already joined before attempting
- Use appropriate wait times for operations
- Better error messages for debugging

### Process Improvements Implemented

1. **Custom Slash Command**: `/project:implement-issue`
   - Enforces proper issue implementation process
   - Provides checklist for consistency
   - Located in `.claude/commands/implement-issue.md`

2. **Network Documentation**: Creating comprehensive network architecture doc
   - Clarifies different network segments
   - Shows proper IP usage for services
   - Prevents future network confusion

3. **Testing Strategy**
   - Test playbooks handle multiple hostname formats
   - Verify on both control plane and worker nodes
   - Check appropriate delegation for operations

### Technical Decisions

1. **Storage Driver**: Confirmed ZFS for LXD (already default)
2. **Network Selection**: LAN (br0) for K8s cluster communication
3. **User Management**: Using system_username consistently
4. **Addons**: Only manage on control plane, not workers

### Best Practices Established

1. Always check GitHub issues for reference implementations
2. Use batch operations for multiple similar tasks
3. Test for existing state before making changes
4. Use appropriate network for each service type
5. Document deviations from reference with justification

### Future Recommendations

1. Standardize hostname configuration across all nodes
2. Create comprehensive network diagram
3. Implement automated testing for playbooks
4. Consider service mesh for complex networking
5. Document all custom tooling (like slash commands)

### Tooling Created

- **Slash Command**: `/project:implement-issue <number>`
  - Purpose: Enforce proper implementation process
  - Location: `.claude/commands/implement-issue.md`
  - Usage: Ensures reference checking before implementation