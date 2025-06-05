# app/api/auth.py
import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.config import settings
from app.models.dashboards import UserInfo, AuthInfo, Token
from app.core.security import get_current_active_user, exchange_code_for_token, User

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

@router.post("/token", response_model=Token)
async def get_token(code: str, redirect_uri: str):
    """Exchange authorization code for access token."""
    try:
        token_response = await exchange_code_for_token(code, redirect_uri)
        return Token(
            access_token=token_response.get("access_token"),
            token_type="Bearer",
            expires_in=token_response.get("expires_in", 3600),
            refresh_token=token_response.get("refresh_token"),
            refresh_expires_in=token_response.get("refresh_expires_in", 86400)
        )
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")

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
async def get_user_info(current_user: User = Depends(get_current_active_user)):
    """Return info about the current authenticated user."""
    logger.debug(f"User data for user info: {current_user}")
    
    # Extract roles from realm_access
    roles = current_user.realm_access.get("roles", ["dashboard-user"])
    
    # Create user info
    user_info = UserInfo(
        sub=current_user.sub,
        preferred_username=current_user.preferred_username,
        email=current_user.email or "default@example.com",
        name=current_user.name or current_user.preferred_username,
        given_name=current_user.name.split()[0] if current_user.name else "User",
        family_name=current_user.name.split()[-1] if current_user.name and len(current_user.name.split()) > 1 else "",
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