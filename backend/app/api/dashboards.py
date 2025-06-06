# app/api/dashboards.py
from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.config import settings
from app.models.dashboards import DashboardItem, UserInfo
from app.core.security import get_current_active_user

router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)
# Set to debug level
logger.setLevel(logging.DEBUG)

# Define dashboards with their metadata - REMOVE ALL ROLE REQUIREMENTS FOR TESTING
DASHBOARD_ITEMS = [
    DashboardItem(
        id="seaweedfs",
        name="SeaweedFS",
        description="Distributed object storage system",
        url=settings.SEAWEEDFS_URL,
        icon="database",
        color="amber",
        category="storage",
        requires_role=None  # Removed role requirement
    ),
    DashboardItem(
        id="harbor",
        name="Harbor Registry",
        description="Container image registry",
        url=settings.HARBOR_URL,
        icon="cube",
        color="blue",
        category="devops",
        requires_role=None  # Removed role requirement
    ),
    DashboardItem(
        id="gitea",
        name="Gitea",
        description="Git service for version control",
        url=settings.GITEA_URL,
        icon="git-branch",
        color="green",
        category="devops",
        requires_role=None  # Removed role requirement
    ),
    DashboardItem(
        id="argocd",
        name="ArgoCD",
        description="GitOps continuous delivery",
        url=settings.ARGOCD_URL,
        icon="sync",
        color="orange",
        category="devops",
        requires_role=None  # Removed role requirement
    ),
    DashboardItem(
        id="argo-workflows",
        name="Argo Workflows",
        description="Workflow automation platform",
        url=settings.ARGO_WORKFLOWS_URL,
        icon="workflow",
        color="purple",
        category="devops",
        requires_role=None  # Removed role requirement
    ),
    DashboardItem(
        id="keycloak",
        name="Keycloak",
        description="Identity and access management",
        url=settings.KEYCLOAK_URL,
        icon="shield-check",
        color="red",
        category="security",
        requires_role=None  # Removed role requirement
    ),
    # Services not yet deployed - uncomment when ready
    # DashboardItem(
    #     id="opensearch",
    #     name="OpenSearch Dashboard",
    #     description="Log and metrics visualization",
    #     url=settings.OPENSEARCH_URL,
    #     icon="chart-bar",
    #     color="green",
    #     category="monitoring",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="qdrant",
    #     name="Qdrant",
    #     description="Vector database management",
    #     url=settings.QDRANT_URL,
    #     icon="database",
    #     color="purple",
    #     category="ai",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="awx",
    #     name="AWX",
    #     description="Ansible automation platform",
    #     url=settings.AWX_URL,
    #     icon="cog",
    #     color="red",
    #     category="devops",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="pgadmin",
    #     name="pgAdmin 4",
    #     description="PostgreSQL database management",
    #     url=settings.PGADMIN_URL,
    #     icon="table",
    #     color="blue",
    #     category="database",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="devpi",
    #     name="DevPI",
    #     description="Python package index mirror",
    #     url=settings.DEVPI_URL,
    #     icon="code",
    #     color="yellow",
    #     category="development",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="jupyterhub",
    #     name="JupyterHub",
    #     description="Interactive notebooks for data science",
    #     url=settings.JUPYTERHUB_URL,
    #     icon="notebook",
    #     color="orange",
    #     category="ai",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="code-server",
    #     name="Code Server",
    #     description="VS Code in the browser",
    #     url=settings.CODE_SERVER_URL,
    #     icon="code",
    #     color="blue",
    #     category="development",
    #     requires_role=None  # Removed role requirement
    # ),
    # DashboardItem(
    #     id="mkdocs",
    #     name="Documentation",
    #     description="Platform documentation",
    #     url=settings.MKDOCS_URL,
    #     icon="book-open",
    #     color="indigo",
    #     category="documentation",
    #     requires_role=None  # Removed role requirement
    # )
]


@router.get("/dashboards", response_model=List[DashboardItem])
async def get_dashboards(request: Request, user_data: dict = Depends(get_current_active_user)):
    """Return all dashboards - no role filtering for now."""
    logger.debug(f"User data received: {user_data}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    # CRITICAL FIX: Return all dashboards unconditionally for initial troubleshooting
    return DASHBOARD_ITEMS


@router.get("/dashboards/categories")
async def get_dashboard_categories(user_data: dict = Depends(get_current_active_user)):
    """Return all dashboard categories."""
    categories = set()
    for dashboard in DASHBOARD_ITEMS:
        categories.add(dashboard.category)
    return {"categories": sorted(list(categories))}


@router.get("/dashboards/{dashboard_id}", response_model=DashboardItem)
async def get_dashboard(dashboard_id: str, user_data: dict = Depends(get_current_active_user)):
    """Return a specific dashboard by ID."""
    for dashboard in DASHBOARD_ITEMS:
        if dashboard.id == dashboard_id:
            return dashboard
    
    raise HTTPException(status_code=404, detail="Dashboard not found")


@router.get("/debug-info")
async def debug_info(request: Request):
    """Debug endpoint to check request info without authentication."""
    return {
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "cookies": request.cookies,
        "client": request.client,
        "url": str(request.url),
    }