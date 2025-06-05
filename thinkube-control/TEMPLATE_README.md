# Thinkube Control Template

This directory contains a template for the Thinkube Control application that can be customized for each deployment.

## How it Works

1. **Template Files**: All Kubernetes manifests and workflows have `.jinja` extensions
2. **Deployment Process**:
   - The Ansible playbook clones this to the shared-code directory
   - Templates are processed with user-specific values
   - Files are committed to the user's GitHub repository
   - ArgoCD deploys from the user's repository

## Template Variables

The following variables are substituted during deployment:

- `{{ namespace }}` - Kubernetes namespace (default: control-hub)
- `{{ domain_name }}` - Your base domain
- `{{ control_subdomain }}` - Subdomain for control interface (default: control)
- `{{ auth_subdomain }}` - Subdomain for auth/Keycloak (default: auth)
- `{{ registry_subdomain }}` - Subdomain for registry (default: registry)
- `{{ keycloak_realm }}` - Keycloak realm name (default: thinkube)
- `{{ github_org }}` - Your GitHub username/organization
- `{{ project_name }}` - Project name

## Manual Testing

To test the template manually:

```bash
# Install copier
pip install copier

# Generate from template
copier copy . /tmp/my-control \
  --data domain_name=mydomain.com \
  --data github_org=myusername

# Check generated files
ls /tmp/my-control/k8s/
```

## Development Workflow

1. **Edit in code-server**: Once deployed, edit files in the shared-code directory
2. **Push changes**: Git push triggers Argo Workflows to build new images
3. **Auto-deploy**: ArgoCD syncs the changes automatically

## Files Structure

```
thinkube-control/
├── k8s/                    # Kubernetes manifests (*.yaml.jinja)
├── workflows/              # Argo Workflow definitions  
├── backend/                # FastAPI backend code
├── frontend/               # Vue.js frontend code
├── copier.yaml            # Template configuration
└── Thinkubefile           # Thinkube app definition
```