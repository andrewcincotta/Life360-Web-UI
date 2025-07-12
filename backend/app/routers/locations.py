"""
Location-specific API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from life360 import Life360

from ..dependencies import get_life360_api
from ..models.analytics import BatchMemberLocation
from ..models.responses import MemberSummary
from ..services.life360_helpers import create_member_summary


router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
    responses={
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/current",
    response_model=List[BatchMemberLocation],
    summary="Get Current Locations",
    description="""
    Get current locations for all members across all circles.
    
    Returns a flat list of all member locations with circle context.
    Useful for mapping applications that need all locations at once.
    
    Query Parameters:
    - only_active: If true, only returns members with active locations
    """
)
async def get_current_locations(
    only_active: bool = Query(
        True,
        description="Only return members with active locations"
    ),
    api: Life360 = Depends(get_life360_api)
) -> List[BatchMemberLocation]:
    """Get all member locations across circles."""
    try:
        circles = await api.get_circles()
        locations = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                member_summary = create_member_summary(member)
                
                # Apply active filter if requested
                if not only_active or (member_summary.status == "Active" and member_summary.location):
                    locations.append(BatchMemberLocation(
                        circle_id=circle["id"],
                        circle_name=circle["name"],
                        member_id=member_summary.id,
                        member_name=member_summary.full_name,
                        location=member_summary.location,
                        status=member_summary.status
                    ))
        
        return locations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch locations: {str(e)}"
        )


@router.get(
    "/driving",
    response_model=List[MemberSummary],
    summary="Get Driving Members",
    description="""
    Get all members who are currently driving.
    
    Checks the isDriving flag and returns only members who are
    actively driving at the time of the request. This is useful
    for safety monitoring or notifications.
    """
)
async def get_driving_members(
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSummary]:
    """Get members currently driving."""
    try:
        # Get all active locations
        all_locations = await get_current_locations(only_active=True, api=api)
        
        driving_members = []
        seen_ids = set()  # Avoid duplicates if member is in multiple circles
        
        for loc in all_locations:
            # Check if member is driving and hasn't been added yet
            if (loc.location and 
                loc.location.is_driving and 
                loc.member_id not in seen_ids):
                
                # Fetch full member data to create proper summary
                circles = await api.get_circles()
                for circle in circles:
                    if circle["id"] == loc.circle_id:
                        members = await api.get_circle_members(circle["id"])
                        for member in members:
                            if member["id"] == loc.member_id:
                                driving_members.append(create_member_summary(member))
                                seen_ids.add(loc.member_id)
                                break
                        break
        
        return driving_members
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch driving members: {str(e)}"
        )