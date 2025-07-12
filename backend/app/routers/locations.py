"""Location-specific endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from life360 import Life360

from ..dependencies import get_life360_api
from ..models.analytics import BatchMemberLocation
from ..models.responses import MemberSummary

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/current", response_model=List[BatchMemberLocation])
async def get_current_locations(
    only_active: bool = Query(True, description="Only return members with active locations"),
    api: Life360 = Depends(get_life360_api)
):
    """Get current locations for all members across all circles."""
    # Implementation here
    pass

@router.get("/driving", response_model=List[MemberSummary])
async def get_driving_members(api: Life360 = Depends(get_life360_api)):
    """Get all members who are currently driving."""
    # Implementation here
    pass