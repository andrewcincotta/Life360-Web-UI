"""
Analytics and statistics related models.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .responses import LocationData


class CircleStatistics(BaseModel):
    """Statistical summary for a circle."""
    circle_id: str = Field(..., description="Circle ID")
    circle_name: str = Field(..., description="Circle name")
    total_members: int = Field(..., description="Total number of members", ge=0)
    active_members: int = Field(..., description="Members with active location sharing", ge=0)
    disconnected_members: int = Field(..., description="Members who are disconnected", ge=0)
    location_off_members: int = Field(..., description="Members with location sharing turned off", ge=0)
    average_battery: Optional[float] = Field(
        None, 
        description="Average battery level of active members",
        ge=0,
        le=100
    )
    last_update: datetime = Field(..., description="Most recent location update from any member")
    
    class Config:
        json_schema_extra = {
            "example": {
                "circle_id": "abc123",
                "circle_name": "Family",
                "total_members": 5,
                "active_members": 4,
                "disconnected_members": 0,
                "location_off_members": 1,
                "average_battery": 67.5,
                "last_update": "2024-01-15T10:30:00"
            }
        }


class BatchMemberLocation(BaseModel):
    """Member location with circle context for batch responses."""
    circle_id: str = Field(..., description="Circle ID")
    circle_name: str = Field(..., description="Circle name")
    member_id: str = Field(..., description="Member ID")
    member_name: str = Field(..., description="Member full name")
    location: Optional[LocationData] = Field(None, description="Current location if available")
    status: str = Field(..., description="Member status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "circle_id": "abc123",
                "circle_name": "Family",
                "member_id": "user456",
                "member_name": "John Doe",
                "status": "Active",
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "accuracy": 65,
                    "name": "Home",
                    "battery": 85,
                    "timestamp": "1749949224"
                }
            }
        }


class LowBatteryMember(BaseModel):
    """Member with low battery information."""
    circle: str = Field(..., description="Circle name")
    member: str = Field(..., description="Member name")
    battery: int = Field(..., description="Current battery percentage", ge=0, le=100)
    location: str = Field(..., description="Current location name or 'Unknown'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "circle": "Family",
                "member": "John Doe",
                "battery": 15,
                "location": "Work"
            }
        }


class MemberSearchResult(BaseModel):
    """Search result for member lookup."""
    circle: str = Field(..., description="Circle name")
    circle_id: str = Field(..., description="Circle ID")
    member: "MemberSummary" = Field(..., description="Member information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "circle": "Family",
                "circle_id": "abc123",
                "member": {
                    "id": "user456",
                    "firstName": "John",
                    "lastName": "Doe",
                    "full_name": "John Doe",
                    "status": "Active"
                }
            }
        }


# Fix circular import
from .responses import MemberSummary
MemberSearchResult.model_rebuild()