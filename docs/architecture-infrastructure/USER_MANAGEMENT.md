# User Management

This document outlines the user management approach for the Thinkube platform, covering system users, application admin accounts, and SSO integration.

## User Categories

The Thinkube platform has three distinct user categories that must be kept separate and configurable:

### 1. System Users (OS Level)

These are Linux users at the operating system level:

- **Default Username**: `thinkube` (configurable in inventory)
- **Scope**: Used on baremetal servers and VMs
- **Purpose**: Running services, SSH access, system administration
- **Configuration Point**: Defined in inventory as `system_username`
- **Authentication**: SSH keys, local passwords
- **Home Directory**: `/home/{{system_username}}`

### 2. Application Admin Users (Basic Auth)

These are application-specific administrator accounts using basic authentication:

- **Default Username**: `tkadmin` (configurable in inventory)
- **Scope**: Used for initial access to all deployed applications, including Keycloak
- **Purpose**: Application administration before SSO is configured
- **Configuration Point**: Defined in inventory as `admin_username`
- **Authentication**: Basic auth (username/password)
- **Creation**: During application deployment

**Note**: We use `tkadmin` instead of `admin` because some services create temporary admin users that cannot be converted to permanent users. Using a distinct username avoids conflicts.

### 3. Keycloak Realm Users

These are users managed through Keycloak for Single Sign-On:

- **Default Realm User**: `thinkube` (configurable in inventory)
- **Scope**: Used across all applications integrated with authentication provider
- **Purpose**: Unified authentication and authorization within the realm
- **Configuration Point**: Defined in inventory as `auth_realm_username`
- **Authentication**: OpenID Connect/OAuth2
- **Creation**: During Keycloak realm setup

## Inventory Configuration

All user-related variables must be defined in inventory, never hardcoded in playbooks. Here's an example inventory structure:

```yaml
all:
  vars:
    # System user configuration
    system_username: "thinkube"          # OS-level user on all servers/VMs
    
    # Application admin configuration (used for all applications including Keycloak)
    admin_username: "tkadmin"            # Default application admin username
    admin_password: "{{ lookup('env', 'ADMIN_PASSWORD') }}"      # From environment
    
    # Auth realm user configuration
    auth_realm_username: "thinkube"      # Username for primary user in authentication realm
    auth_realm_password: "{{ lookup('env', 'AUTH_REALM_PASSWORD') }}"
```

## Implementation Guidelines

### System User Creation

1. The system user (`system_username`) must be created consistently across all servers and VMs
2. This user must have sudo privileges for system administration
3. SSH keys must be distributed for this user across all systems
4. All services should run under this user where appropriate

Example task:
```yaml
- name: Create system user
  ansible.builtin.user:
    name: "{{ system_username }}"
    shell: /bin/bash
    create_home: yes
    groups: sudo
    append: yes
  become: true
```

### Application Admin Setup

1. Application admin credentials must be configured during application deployment
2. Never use hardcoded "tkadmin" string for username
3. Always use `admin_username` from inventory
4. Store passwords in environment variables, never in inventory files
5. Use the same admin credentials consistently across all applications (including Keycloak)

Example snippet:
```yaml
- name: Set up application admin
  kubernetes.core.k8s:
    definition:
      apiVersion: v1
      kind: Secret
      metadata:
        name: admin-credentials
        namespace: "{{ app_namespace }}"
      type: Opaque
      stringData:
        username: "{{ admin_username }}"
        password: "{{ admin_password }}"
```

### Keycloak Configuration

#### Keycloak Admin User (Basic Auth)

1. Keycloak's built-in admin user must be configured using the common `admin_username`
2. This maintains consistency across all applications
3. This is for direct administration of Keycloak itself

Example snippet:
```yaml
- name: Configure Keycloak admin
  kubernetes.core.k8s:
    definition:
      apiVersion: v1
      kind: Secret
      metadata:
        name: keycloak-admin
        namespace: keycloak
      type: Opaque
      stringData:
        username: "{{ admin_username }}"
        password: "{{ admin_password }}"
```

#### Keycloak Realm User

1. After Keycloak is set up, create a Thinkube realm
2. Create a user in this realm using `auth_realm_username` from inventory
3. Assign appropriate realm roles to this user
4. This user will be used for accessing applications integrated with Keycloak

Example snippet:
```yaml
- name: Create Keycloak realm user
  community.general.keycloak_user:
    auth_keycloak_url: "https://keycloak.{{ domain_name }}/auth"
    auth_realm: "master"
    auth_username: "{{ admin_username }}"
    auth_password: "{{ admin_password }}"
    realm: "thinkube"
    username: "{{ auth_realm_username }}"
    password: "{{ auth_realm_password }}"
    email: "{{ auth_realm_username }}@{{ domain_name }}"
    first_name: Thinkube
    last_name: User
    enabled: true
    state: present
```

## Password Handling

1. **NEVER** store passwords in inventory files or playbooks
2. Use environment variables for password lookup
3. Document required environment variables for deployment
4. Provide option for interactive password entry during deployment

Example password handling in environment:
```bash
# Add to ~/.env file (symlinked to project root)
export ADMIN_PASSWORD='secure_password'
export AUTH_REALM_PASSWORD='another_secure_password'
```

## Playbook Implementation

All playbooks that create or configure users must:

1. Validate required variables exist at the start
2. Use inventory variables for usernames, never hardcode
3. Check for required environment variables for passwords
4. Provide meaningful error messages if variables are missing

Example validation:
```yaml
- name: Verify user variables are defined
  ansible.builtin.assert:
    that:
      - system_username is defined and system_username != ""
      - admin_username is defined and admin_username != ""
      - auth_realm_username is defined and auth_realm_username != ""
    fail_msg: >
      ERROR: Required user variables not defined in inventory.
      Please ensure system_username, admin_username, and auth_realm_username are set.
```

## SSH Configuration

SSH configuration must respect the system username:

1. Use `system_username` for SSH config setup
2. Configure SSH keys for the correct user
3. Generate SSH key path based on username

Example SSH config setup:
```yaml
- name: Set up SSH config for VMs
  ansible.builtin.template:
    src: ssh_config.j2
    dest: "/home/{{ system_username }}/.ssh/config"
    owner: "{{ system_username }}"
    group: "{{ system_username }}"
    mode: '0600'
```

## Variables Reference

| Variable Name | Purpose | Default | Required |
|---------------|---------|---------|----------|
| `system_username` | OS-level user | "thinkube" | Yes |
| `admin_username` | Application admin for all apps including Keycloak | "tkadmin" | Yes |
| `admin_password` | App admin password | From env | Yes |
| `auth_realm_username` | User in authentication realm | "thinkube" | Yes |
| `auth_realm_password` | Realm user password | From env | Yes |