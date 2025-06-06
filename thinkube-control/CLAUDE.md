# CLAUDE.md - Thinkube Control Hub Documentation

This file provides guidance to Claude Code (claude.ai/code) and developers when working with the Thinkube Control Hub repository.

## Project Overview

Thinkube Control Hub is a unified dashboard interface for accessing all Thinkube platform services. It provides:
- Single sign-on (SSO) via Keycloak integration
- Dynamic service discovery and dashboard presentation
- Role-based access control for different services
- Modern Vue.js frontend with FastAPI backend

## Architecture

### Frontend (Vue.js + DaisyUI)
- **Location**: `/frontend`
- **Technology**: Vue 3, Vue Router, Axios, Tailwind CSS, DaisyUI
- **Purpose**: Provides a modern, responsive UI for accessing platform services

### Backend (FastAPI)
- **Location**: `/backend`
- **Technology**: FastAPI, Pydantic, Python 3.11
- **Purpose**: API gateway that handles authentication and service discovery

### Kubernetes Manifests
- **Location**: `/k8s`
- **Templates**: Jinja2 templates (`.jinja` files) for multi-domain deployment
- **Processed**: YAML files generated from templates during deployment

## GitOps Workflow

This project follows a GitOps workflow designed for live development and testing:

### 1. Initial Deployment (GitHub → vm-2)
- **Source**: https://github.com/{github_org}/thinkube-control (templates)
- **Process**: 
  1. Ansible clones from GitHub to vm-2: `/home/thinkube/shared-code/thinkube-control`
  2. Processes Jinja2 templates with domain-specific values
  3. Generates deployment-ready YAML manifests
  4. Pushes to Gitea for ArgoCD deployment

### 2. Live Development (vm-2)
- **Location**: `/home/thinkube/shared-code/thinkube-control` on vm-2
- **Automation**: Pre-push hook installed by deployment playbook
- **Process**:
  1. Make changes directly in the shared-code directory
  2. Commit changes locally
  3. Push to Gitea (triggers automated workflow)
  4. Pre-push hook creates pending commit file
  5. Repository monitor detects and triggers Argo Workflow
  6. Argo Workflow builds new container images
  7. ArgoCD detects new images and redeploys
  8. Test changes in live environment

### 3. Deployment Repository (Gitea)
- **Repository**: https://git.{domain_name}/thinkube-deployments/control-hub-deployment
- **Content**: Processed manifests with domain-specific values
- **Purpose**: ArgoCD source for deployments
- **Updates**: Automatically when pushing from vm-2

### 4. Continuous Deployment (ArgoCD)
- **Application**: control-hub
- **Source**: Gitea repository
- **Target**: Kubernetes cluster
- **Sync**: Automatic, monitors Gitea for changes

### 5. Stabilization (vm-2 → GitHub)
- **When**: After testing and confirming changes work
- **Process**:
  1. Remove generated YAML files (keep .jinja templates)
  2. Ensure templates use variables (not hardcoded domains)
  3. Push stable code back to GitHub for other deployments

## Making Changes

### To modify the application (LIVE DEVELOPMENT):

1. **Access the deployed code on vm-2**:
   ```bash
   ssh vm-2
   cd /home/thinkube/shared-code/thinkube-control
   ```

2. **Make your changes**:
   - Frontend code: `frontend/src/`
   - Backend code: `backend/app/`
   - Kubernetes manifests: Edit `.jinja` templates, not generated YAML
   - Workflows: `workflows/*.jinja`

3. **Commit and push to Gitea**:
   ```bash
   git add .
   git commit -m "Your descriptive message"
   git push  # Pre-push hook automatically handles the GitOps workflow
   ```
   
   **Note**: The pre-push hook (`.git/hooks/pre-push`) automatically:
   - Records the commit being pushed
   - Creates a pending commit file for the repository monitor
   - Triggers a build workflow once the push completes
   - Updates the container images in Harbor
   - ArgoCD then detects and deploys the changes

4. **Monitor deployment**:
   ```bash
   # Check ArgoCD sync status
   kubectl get applications -n argocd control-hub
   
   # Watch pods restart
   kubectl get pods -n control-hub -w
   ```

5. **Test your changes**:
   - Access https://control.{domain_name}
   - Verify functionality works as expected

### To push stable changes back to GitHub:

1. **Clean up domain-specific files**:
   ```bash
   cd /home/thinkube/shared-code/thinkube-control
   
   # Remove generated YAML files (keep .jinja)
   rm k8s/*.yaml
   rm workflows/*.yaml
   
   # Ensure no hardcoded domains in templates
   grep -r "thinkube.com" k8s/ workflows/
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update templates for multi-domain deployment"
   git push github main  # Assuming 'github' remote is configured
   ```

## Adding New Services

When a new service is deployed to the platform, add it to the Control Hub:

1. **Update backend configuration** (`backend/app/core/config.py`):
   ```python
   # Uncomment or add the service URL
   NEW_SERVICE_URL: str
   ```

2. **Update dashboard list** (`backend/app/api/dashboards.py`):
   ```python
   # Uncomment or add the dashboard item
   DashboardItem(
       id="new-service",
       name="New Service",
       description="Description of the service",
       url=settings.NEW_SERVICE_URL,
       icon="appropriate-icon",
       color="color-choice",
       category="category",
       requires_role=None  # or specific role
   ),
   ```

3. **Update deployment manifest** (`k8s/backend-deployment.yaml.jinja`):
   ```yaml
   # Uncomment or add the environment variable
   - name: NEW_SERVICE_URL
     value: "https://new-service.{{ domain_name }}"
   ```

4. **Commit, push, and redeploy** as described above.

## Environment Variables

The backend expects these environment variables for deployed services:
- `SEAWEEDFS_URL`: SeaweedFS object storage
- `HARBOR_URL`: Harbor container registry
- `GITEA_URL`: Gitea git service
- `ARGOCD_URL`: ArgoCD GitOps
- `ARGO_WORKFLOWS_URL`: Argo Workflows
- `KEYCLOAK_URL`: Keycloak authentication

Additional services (currently commented out):
- `OPENSEARCH_URL`: OpenSearch dashboards
- `QDRANT_URL`: Qdrant vector database
- `AWX_URL`: AWX/Ansible automation
- `PGADMIN_URL`: PostgreSQL administration
- `DEVPI_URL`: Python package index
- `JUPYTERHUB_URL`: JupyterHub notebooks
- `CODE_SERVER_URL`: VS Code server
- `MKDOCS_URL`: Documentation site

## Troubleshooting

### Blank screen on frontend
- Check browser console for errors
- Verify API endpoints are correct in `frontend/src/services/api.js`
- Check backend logs: `kubectl logs -n control-hub deployment/control-backend`

### Backend crashes
- Check for missing environment variables
- Verify all referenced services in `dashboards.py` have corresponding config entries
- Check Keycloak client configuration

### Images not pulling
- Verify image URLs use external registry URL (`registry.{domain_name}`)
- Check image pull secrets are configured
- Ensure images were built and pushed successfully

### GitOps not updating
- Verify Gitea repository was created and contains processed manifests
- Check ArgoCD application sync status
- Ensure no hardcoded values in templates

### Automated build not triggering
- Check pre-push hook exists: `ls -la /home/thinkube/shared-code/thinkube-control/.git/hooks/pre-push`
- Check pending commits directory: `ls -la /home/coder/.pending-commits/`
- Check Argo Workflow status: `kubectl get workflows -n argo`
- Verify repository monitor service is running
- Check logs: `cat /home/coder/.hooks-logs/pre-push.log`

## Important Notes

1. **Never hardcode domain-specific values** - Always use Jinja2 variables
2. **Test deployment locally first** - Use a development cluster if available
3. **Always run rollback before redeploying** - Ensures clean state
4. **Comment out undeployed services** - Don't delete, just comment for future use
5. **Use external URLs for dashboards** - Users access through browser, not from within cluster

## Repository Structure

```
thinkube-control/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   └── models/         # Pydantic models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue.js frontend application
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API services
│   │   └── views/          # Page views
│   ├── Dockerfile
│   └── package.json
├── k8s/                    # Kubernetes manifests (Jinja2 templates)
│   ├── backend-deployment.yaml.jinja
│   ├── frontend-deployment.yaml.jinja
│   ├── ingress.yaml.jinja
│   └── ...
├── workflows/              # Argo Workflows definitions
│   └── build-workflow.yaml.jinja
└── CLAUDE.md              # This file
```

## Contact

For issues or questions about the Thinkube Control Hub, please refer to the main Thinkube documentation or create an issue in the GitHub repository.