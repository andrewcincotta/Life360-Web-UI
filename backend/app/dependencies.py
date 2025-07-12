"""
FastAPI dependency functions.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException
from life360 import Life360


async def get_life360_api(
    authorization: Optional[str] = Header(
        None, 
        description="Bearer token for Life360 API. Format: 'Bearer YOUR_TOKEN'"
    )
) -> Life360:
    """
    Get Life360 API client instance with proper authentication.
    
    This dependency:
    1. Checks for Bearer token in Authorization header (preferred)
    2. Falls back to LIFE360_AUTHORIZATION environment variable
    3. Ensures proper "Bearer" prefix
    4. Returns configured Life360 client
    
    Raises:
        HTTPException: 401 if no valid authorization is provided
        HTTPException: 500 if session is not initialized
    """
    # Import here to avoid circular dependency
    from .main import app_state
    
    # Determine the token to use
    if authorization:
        # Header takes precedence
        if authorization.startswith("Bearer "):
            token = authorization
        else:
            # Add Bearer prefix if missing
            token = f"Bearer {authorization}"
    else:
        # Fall back to environment variable
        env_token = os.getenv("LIFE360_AUTHORIZATION")
        if not env_token:
            raise HTTPException(
                status_code=401,
                detail="No authorization provided. Pass Bearer token in Authorization header or set LIFE360_AUTHORIZATION environment variable."
            )
        # Ensure Bearer prefix
        if env_token.startswith("Bearer "):
            token = env_token
        else:
            token = f"Bearer {env_token}"
    
    # Get the shared session
    session = app_state.get("default_session")
    if not session:
        raise HTTPException(
            status_code=500,
            detail="Session not initialized. Server may be starting up."
        )
    
    # Create a new Life360 instance with the token
    # This is lightweight since we're reusing the session
    return Life360(
        session=session,
        authorization=token,
        max_retries=3
    )