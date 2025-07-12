"""
Pydantic models for API responses.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class CircleInfo(BaseModel):
    """Basic circle information returned by the API."""
    id: str = Field(..., description="Unique circle identifier", example="abc123-def456")
    name: str = Field(..., description="Circle name", example="Family")
    created_at: str = Field(
        ..., 
        alias="createdAt", 
        description="Creation timestamp (Unix timestamp as string)",
        example="1532204232"
    )
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "0fae83b9-1bb9-4149-9ff3-ba1239d26788",
                "name": "Family",
                "createdAt": "1532204232"
            }
        }


class LocationData(BaseModel):
    """Location information for a member."""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    accuracy: int = Field(..., description="Location accuracy in meters", ge=0)
    name: Optional[str] = Field(None, description="Location name (e.g., 'Home', 'Work')")
    address1: Optional[str] = Field(None, description="Street address")
    address2: Optional[str] = Field(None, description="City, State")
    battery: Optional[int] = Field(None, description="Device battery percentage (0-100)", ge=0, le=100)
    timestamp: str = Field(..., description="Location update timestamp (Unix timestamp as string)")
    speed: Optional[float] = Field(None, description="Current speed in mph", ge=0)
    is_driving: Optional[bool] = Field(None, alias="isDriving", description="Whether member is currently driving")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "accuracy": 65,
                "name": "Home",
                "address1": "123 Main St",
                "address2": "New York, NY",
                "battery": 85,
                "timestamp": "1749949224",
                "speed": 0,
                "is_driving": False
            }
        }


class MemberSummary(BaseModel):
    """Simplified member information for API responses."""
    id: str = Field(..., description="Unique member identifier")
    first_name: str = Field(..., alias="firstName", description="Member's first name")
    last_name: Optional[str] = Field("", alias="lastName", description="Member's last name")
    full_name: str = Field(..., description="Full name (computed from first + last)")
    status: str = Field(
        ..., 
        description="Member status",
        pattern="^(Active|Disconnected|Location Off|No Location)$"
    )
    location: Optional[LocationData] = Field(None, description="Current location if available")
    avatar: Optional[str] = Field(None, description="Profile picture URL")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "8e935520-60b3-47c5-8ddb-91c6fd1793bc",
                "firstName": "John",
                "lastName": "Doe",
                "full_name": "John Doe",
                "status": "Active",
                "avatar": "https://www.life360.com/img/user_images/...",
                "phone": "+1234567890",
                "email": "john.doe@example.com",
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


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Authentication Error",
                "detail": "Invalid or missing bearer token",
                "status_code": 401
            }
        }