"""
Circle-related API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from life360 import Life360

from ..dependencies import get_life360_api
from ..models.responses import CircleInfo, MemberSummary
from ..services.life360_helpers import create_member_summary


router = APIRouter(
    prefix="/circles",
    tags=["Circles"],
    responses={
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=List[CircleInfo],
    summary="List All Circles",
    description="""
    Retrieve all circles associated with the authenticated Life360 account.
    
    Circles are groups of members who share their locations with each other.
    Common examples include 'Family', 'Friends', or custom group names.
    """
)
async def get_circles(api: Life360 = Depends(get_life360_api)) -> List[CircleInfo]:
    """Get all circles for the authenticated user."""
    try:
        circles = await api.get_circles()
        return circles
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch circles: {str(e)}"
        )


@router.get(
    "/{circle_id}/members",
    response_model=List[MemberSummary],
    summary="List Circle Members",
    description="""
    Get all members of a specific circle with their current location status.
    
    This endpoint returns simplified member information including:
    - Personal details (name, contact info)
    - Current status (Active, Disconnected, Location Off, No Location)
    - Location data if available and sharing is enabled
    - Device information (battery level, etc.)
    """
)
async def get_circle_members(
    circle_id: str = Path(
        ..., 
        description="The unique circle identifier",
        example="abc123-def456-7890"
    ),
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSummary]:
    """Get all members in a specific circle."""
    try:
        members_data = await api.get_circle_members(circle_id)
        return [create_member_summary(member) for member in members_data]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch circle members: {str(e)}"
        )


@router.get(
    "/{circle_id}/members/{member_id}",
    summary="Get Member Details",
    description="""
    Get detailed information about a specific member in a circle.
    
    This returns the raw member data from Life360 API, which includes
    all available fields. Use this for debugging or when you need
    access to fields not included in the simplified MemberSummary.
    """,
    response_model=None  # Returns raw dict
)
async def get_member_details(
    circle_id: str = Path(..., description="The unique circle identifier"),
    member_id: str = Path(..., description="The unique member identifier"),
    api: Life360 = Depends(get_life360_api)
):
    """Get raw member details from Life360 API."""
    try:
        return await api.get_circle_member(circle_id, member_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch member details: {str(e)}"
        )