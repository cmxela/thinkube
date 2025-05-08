# AI-Assisted Development for Thinkube

## Development Approach

1. **Test-First Development**: Create test playbooks (x8) before implementation playbooks
2. **Small Increments**: One playbook at a time
3. **Validation Gates**: No progress until tests pass
4. **Iterative Refinement**: Improve each playbook through multiple small iterations

## Practical Workflow

### Phase 1: Component Setup

For each component (initial_setup, baremetal_infra, etc.):

1. **Create Test Playbook First**
   - Develop component_x8_test.yaml first
   - Define clear pass/fail criteria

2. **Section-by-Section Implementation**
   - Implement implementation playbooks incrementally
   - Each section must pass its corresponding test section

3. **Review & Refine**
   - Test
   - Fix
   - Commit only when tests pass

### Development Sequence

Example for `20_lxd_setup`:

1. Create `28_test_lxd_profiles.yaml`
2. Implement `20_setup_lxd_profiles.yaml`
3. Test until pass
4. Create next test section in `28_test_lxd_profiles.yaml`
5. Implement next section in `20_setup_lxd_profiles.yaml`
6. Repeat

## Interaction Guidelines

1. **Small Code Snippets**: Request small, focused code segments instead of complete playbooks
2. **Verification Steps**: Include verification after each implementation
3. **Fixed Problems**: Document issues and solutions for reference
4. **Pattern Establishment**: Document reusable patterns and approaches

## Output Control

To avoid generating too much code at once:
- "Generate only the test for X"
- "Focus only on the verification section"
- "Show only the task that handles Y"