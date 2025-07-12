"""
Member-related API endpoints.

This module handles all /members/* routes including listing,
searching, and filtering members across circles.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from life360 import Life360

from ..dependencies import get_life360_api
from ..models.responses import MemberSummary
from ..models.analytics import MemberSearchResult
from ..services.life360_helpers import create_member_summary


router = APIRouter(
    prefix="/members",
    tags=["Members"],
    responses={
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/all",
    response_model=Dict[str, List[MemberSummary]],
    summary="Get All Members",
    description="""
    Get all members from all circles organized by circle name.
    
    This endpoint fetches all circles and their members in one call,
    useful for getting a complete overview of all tracked individuals.
    
    Returns a dictionary where:
    - Keys are circle names
    - Values are lists of member summaries
    """
)
async def get_all_members(
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, List[MemberSummary]]:
    """Get all members organized by circle."""
    try:
        circles = await api.get_circles()
        result = {}
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            members = [create_member_summary(member) for member in members_data]
            result[circle["name"]] = members
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch members: {str(e)}"
        )


@router.get(
    "/active",
    response_model=Dict[str, List[MemberSummary]],
    summary="Get Active Members Only",
    description="""
    Get all members with active location sharing across all circles.
    
    Filters out members who are:
    - Disconnected from Life360
    - Have location sharing turned off
    - Have no location data available
    
    Perfect for map displays where you only want to show trackable members.
    """
)
async def get_active_members(
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, List[MemberSummary]]:
    """Get only members with active location sharing."""
    try:
        # Reuse the get_all_members logic
        all_members = await get_all_members(api)
        
        # Filter to only active members
        active_members = {}
        for circle_name, members in all_members.items():
            active = [m for m in members if m.status == "Active" and m.location]
            if active:  # Only include circles with active members
                active_members[circle_name] = active
        
        return active_members
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch active members: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[MemberSearchResult],
    summary="Search Members by Name",
    description="""
    Search for members by name across all circles.
    
    - Case-insensitive search
    - Searches both first and last names
    - Returns members with their circle information
    - Partial matches are supported
    
    Example: Searching for "john" will find "John Doe", "Johnny Smith", etc.
    """
)
async def search_members(
    name: str = Query(
        ...,
        description="Name to search for",
        min_length=1,
        example="John"
    ),
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSearchResult]:
    """Search for members by name across all circles."""
    try:
        circles = await api.get_circles()
        results = []
        
        search_term = name.lower()
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                full_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                
                # Check if search term appears in the full name
                if search_term in full_name.lower():
                    results.append(MemberSearchResult(
                        circle=circle["name"],
                        circle_id=circle["id"],
                        member=create_member_summary(member)
                    ))
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/me",
    summary="Get Current User Info",
    description="""
    Get information about the currently authenticated Life360 user.
    
    This returns the account owner's information, which may include
    additional fields not available for other members.
    """,
    response_model=None  # Returns raw user data
)
async def get_me(api: Life360 = Depends(get_life360_api)):
    """Get current user information."""
    try:
        return await api.get_me()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user info: {str(e)}"
        )