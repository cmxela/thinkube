# Example: Test-First Development for LXD Profile Setup

This document demonstrates the AI-assisted, test-first development approach for the LXD profile setup playbooks.

## Step 1: Create Test Playbook Framework

```yaml
---
# 28_test_lxd_profiles.yaml - Test LXD profiles configuration
# Run with: ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/28_test_lxd_profiles.yaml

- name: Test LXD profiles configuration
  hosts: management
  gather_facts: true
  tasks:
    - name: Verify LXD is installed
      ansible.builtin.command: which lxc
      register: lxc_check
      failed_when: lxc_check.rc != 0
      changed_when: false

    # More tests will be added incrementally
```

## Step 2: Create Initial Implementation Playbook

```yaml
---
# 20_setup_lxd_profiles.yaml - Create VM profiles for MicroK8s nodes
# Run with: ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/20_setup_lxd_profiles.yaml

- name: Create VM profiles for MicroK8s nodes
  hosts: management
  gather_facts: true
  tasks:
    - name: Verify LXD is installed
      ansible.builtin.command: which lxc
      register: lxc_check
      failed_when: lxc_check.rc != 0
      changed_when: false
      
    # Implementation will be expanded incrementally
```

## Step 3: Add First Test Section

```yaml
# Add to 28_test_lxd_profiles.yaml
- name: Check if vm-networks profile exists
  ansible.builtin.command: lxc profile show vm-networks
  register: profile_check
  failed_when: profile_check.rc != 0
  changed_when: false
```

## Step 4: Implement the Corresponding Feature

```yaml
# Add to 20_setup_lxd_profiles.yaml
- name: Create vm-networks profile
  ansible.builtin.command: >
    lxc profile create vm-networks
  register: profile_create
  failed_when: 
    - profile_create.rc != 0
    - "'already exists' not in profile_create.stderr"
  changed_when: "'already exists' not in profile_create.stderr"
```

## Step 5: Run Test to Verify

Run the test playbook to verify the implementation:
```bash
ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/28_test_lxd_profiles.yaml
```

## Step 6: Add Next Test Section

```yaml
# Add to 28_test_lxd_profiles.yaml
- name: Check vm-networks profile configuration
  ansible.builtin.command: lxc profile show vm-networks
  register: profile_config
  failed_when: profile_config.rc != 0
  changed_when: false

- name: Verify vm-networks has eth0 device
  ansible.builtin.assert:
    that:
      - "'eth0' in profile_config.stdout"
    fail_msg: "eth0 device not found in vm-networks profile"
```

## Step 7: Implement the Network Configuration

```yaml
# Add to 20_setup_lxd_profiles.yaml
- name: Configure vm-networks profile with eth0
  ansible.builtin.command: >
    lxc profile device add vm-networks eth0 nic nictype=bridged parent=lxdbr0
  register: profile_config
  failed_when:
    - profile_config.rc != 0
    - "'already exists' not in profile_config.stderr"
  changed_when: "'already exists' not in profile_config.stderr"
```

## Step 8: Continue with Test-Implement-Verify Cycles

This pattern continues, with each new test section followed by its implementation and verification.

## Benefits of This Approach

1. **Always Testable**: Each increment is immediately testable
2. **Clear Progress**: Easy to see where you are in the implementation
3. **Focused Development**: Work on one small piece at a time
4. **Early Problem Detection**: Tests catch issues before moving on
5. **Natural Documentation**: Tests document the expected behavior