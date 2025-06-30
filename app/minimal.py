"""Minimal FastAPI app for Life360 API integration.

This API provides endpoints to interact with the Life360 service, including retrieving circles, members, and user information.
"""
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from app.shared_state import get_life360_client
from life360 import Life360


app = FastAPI(
    title="Life360 API V1",
    description="""
    This FastAPI app provides a RESTful interface to the Life360 API. 
    Use these endpoints to retrieve information about your circles, members, and account.
    """,
    version="1.0.0"
)


# Dependency
def get_api() -> Life360:
    """Dependency to provide the Life360 API client."""
    client = get_life360_client()
    if not client:
        raise HTTPException(status_code=500, detail="Life360 client not initialized")
    return client


@app.get("/", summary="API Health Check", tags=["Utility"])
async def root():
    """Check if the API is running."""
    return {"status": "ok", "version": "v1"}


@app.get(
    "/circles",
    response_model=List[Dict[str, str]],
    summary="Get Circles",
    tags=["Circles"],
    response_description="A list of circles the user belongs to."
)
async def get_circles(api: Life360 = Depends(get_api)) -> List[Dict[str, str]]:
    """
    Retrieve all circles associated with the authenticated Life360 account.
    
    Returns a list of circles, each with its ID and name.
    """
    try:
        return await api.get_circles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/circles/{circle_id}/members",
    response_model=List[Dict[str, Any]],
    summary="Get Members of a Circle",
    tags=["Circles"],
    response_description="A list of members in the specified circle."
)
async def get_members(
    circle_id: str,
    api: Life360 = Depends(get_api)
) -> List[Dict[str, Any]]:
    """
    Get all members of a specific circle by its ID.
    
    - **circle_id**: The unique identifier of the circle.
    """
    try:
        return await api.get_circle_members(circle_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get(
    "/me",
    response_model=Dict[str, Any],
    summary="Get Current User Info",
    tags=["User"],
    response_description="Information about the authenticated user."
)
async def get_me(api: Life360 = Depends(get_api)) -> Dict[str, Any]:
    """
    Retrieve information about the currently authenticated Life360 user.
    """
    try:
        return await api.get_me()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/circles/{circle_id}/members/{member_id}",
    response_model=Dict[str, Any],
    summary="Get Member Info",
    tags=["Circles"],
    response_description="Information about a specific member in a circle."
)
async def get_member(
    circle_id: str,
    member_id: str,
    api: Life360 = Depends(get_api)
) -> Dict[str, Any]:
    """
    Get information about a specific member in a circle.
    
    - **circle_id**: The unique identifier of the circle.
    - **member_id**: The unique identifier of the member.
    """
    try:
        return await api.get_circle_member(circle_id, member_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))