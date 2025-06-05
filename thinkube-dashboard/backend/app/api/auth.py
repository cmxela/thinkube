# app/api/auth.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.config import settings
from app.models.dashboards import UserInfo, AuthInfo, Token
from app.core.security import get_current_active_user

router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@router.get("/auth-config", response_model=AuthInfo)
async def get_auth_config():
    """Return authentication configuration for frontend."""
    return AuthInfo(
        keycloak_url=settings.KEYCLOAK_URL,
        realm=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        auth_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/auth",
        token_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
        userinfo_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/userinfo",
        logout_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout",
        end_session_endpoint=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout",
    )

# This endpoint is no longer used with OAuth2 Proxy
@router.post("/token", response_model=Token)
async def get_token(code: str, redirect_uri: str):
    """Return a dummy token for compatibility."""
    return Token(
        access_token="dummy-token-for-compatibility",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="dummy-refresh-token",
        refresh_expires_in=86400
    )

# This endpoint is no longer used with OAuth2 Proxy
@router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str):
    """Return a dummy token for compatibility."""
    return Token(
        access_token="dummy-token-for-compatibility",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="dummy-refresh-token",
        refresh_expires_in=86400
    )

@router.get("/user-info", response_model=UserInfo)
async def get_user_info(request: Request, user_data: dict = Depends(get_current_active_user)):
    """Return info about the current authenticated user."""
    logger.debug(f"User info request headers: {dict(request.headers)}")
    logger.debug(f"User data for user info: {user_data}")
    
    # Extract roles from realm_access if available, otherwise use a default role
    roles = user_data.get("realm_access", {}).get("roles", ["dashboard-user"])
    
    # Create user info
    user_info = UserInfo(
        sub=user_data.get("sub", "default-user"),
        preferred_username=user_data.get("preferred_username", "Default User"),
        email=user_data.get("email", "default@example.com"),
        name=user_data.get("name", "Default User"),
        given_name=user_data.get("given_name", "Default"),
        family_name=user_data.get("family_name", "User"),
        roles=roles,
    )
    
    logger.debug(f"Returning user info: {user_info}")
    return user_info

@router.get("/debug-headers")
async def debug_headers(request: Request):
    """Debug endpoint to show all headers."""
    return {
        "headers": dict(request.headers),
        "cookies": request.cookies
    }