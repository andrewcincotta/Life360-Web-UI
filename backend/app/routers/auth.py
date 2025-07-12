"""
Authentication-related endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from life360 import Life360

from ..dependencies import get_life360_api


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/validate",
    summary="Validate Token",
    description="""
    Validate a Life360 token by attempting to fetch circles.
    
    This is useful for frontend applications to verify token validity
    before making other API calls. Returns information about the token's
    validity and the number of circles accessible.
    """,
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "Token is valid",
            "content": {
                "application/json": {
                    "example": {
                        "valid": True,
                        "message": "Token is valid",
                        "circles_count": 2
                    }
                }
            }
        },
        401: {
            "description": "Invalid token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid token or API error"
                    }
                }
            }
        }
    }
)
async def validate_token(api: Life360 = Depends(get_life360_api)):
    """Validate the provided Life360 token."""
    try:
        circles = await api.get_circles()
        return {
            "valid": True,
            "message": "Token is valid",
            "circles_count": len(circles)
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or API error"
        )


@router.get(
    "/debug",
    summary="Debug Token Info",
    description="""
    Debug endpoint to check how tokens are being received and processed.
    
    This endpoint shows:
    - Whether a token was provided in the header
    - Whether an environment variable is set
    - Recommendations for best practices
    
    Note: Only shows partial token values for security.
    """,
    tags=["Debug"]
)
async def debug_token(
    authorization: Optional[str] = Header(None, description="Authorization header value")
):
    """Debug token handling - shows how tokens are received."""
    import os
    
    env_token = os.getenv("LIFE360_AUTHORIZATION", "Not set")
    
    return {
        "header_provided": authorization is not None,
        "header_value": f"{authorization[:20]}..." if authorization and len(authorization) > 20 else authorization,
        "header_has_bearer": authorization.startswith("Bearer ") if authorization else None,
        "env_var_set": env_token != "Not set",
        "env_var_preview": f"{env_token[:20]}..." if env_token != "Not set" and len(env_token) > 20 else env_token,
        "env_has_bearer": env_token.startswith("Bearer ") if env_token != "Not set" else None,
        "recommendation": "Use Authorization header with 'Bearer YOUR_TOKEN' format"
    }