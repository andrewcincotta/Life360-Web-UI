"""Enhanced Life360 FastAPI Application.

This API provides comprehensive endpoints to interact with the Life360 service,
including retrieving circles, members, locations, and various analytics.

Authentication is handled via Bearer token in the Authorization header.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from aiohttp import ClientSession
from life360 import Life360

# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class CircleInfo(BaseModel):
    """Basic circle information."""
    id: str = Field(..., description="Unique circle identifier")
    name: str = Field(..., description="Circle name")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "abc123-def456",
                "name": "Family",
                "createdAt": "1532204232"
            }
        }


class LocationData(BaseModel):
    """Location information for a member."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    accuracy: int = Field(..., description="Location accuracy in meters")
    name: Optional[str] = Field(None, description="Location name (e.g., 'Home', 'Work')")
    address1: Optional[str] = Field(None, description="Primary address line")
    address2: Optional[str] = Field(None, description="Secondary address line (city/state)")
    battery: Optional[int] = Field(None, description="Device battery percentage")
    timestamp: str = Field(..., description="Location update timestamp")
    speed: Optional[float] = Field(None, description="Current speed in mph")
    is_driving: Optional[bool] = Field(None, alias="isDriving", description="Whether member is driving")
    
    @validator('battery')
    def validate_battery(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Battery must be between 0 and 100')
        return v


class MemberSummary(BaseModel):
    """Simplified member information."""
    id: str = Field(..., description="Unique member identifier")
    first_name: str = Field(..., alias="firstName", description="Member's first name")
    last_name: Optional[str] = Field("", alias="lastName", description="Member's last name")
    full_name: str = Field(..., description="Full name (computed)")
    status: str = Field(..., description="Member status: Active, Disconnected, Location Off, or No Location")
    location: Optional[LocationData] = Field(None, description="Current location if available")
    avatar: Optional[str] = Field(None, description="Profile picture URL")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "user123",
                "firstName": "John",
                "lastName": "Doe",
                "full_name": "John Doe",
                "status": "Active",
                "avatar": "https://example.com/avatar.jpg"
            }
        }


class CircleStatistics(BaseModel):
    """Statistics for a circle."""
    circle_id: str = Field(..., description="Circle ID")
    circle_name: str = Field(..., description="Circle name")
    total_members: int = Field(..., description="Total number of members")
    active_members: int = Field(..., description="Members with active location")
    disconnected_members: int = Field(..., description="Members who are disconnected")
    location_off_members: int = Field(..., description="Members with location sharing off")
    average_battery: Optional[float] = Field(None, description="Average battery level of active members")
    last_update: datetime = Field(..., description="Most recent location update from any member")


class BatchMemberLocation(BaseModel):
    """Batch response for member locations across circles."""
    circle_id: str
    circle_name: str
    member_id: str
    member_name: str
    location: Optional[LocationData]
    status: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code")


# ============================================================================
# Global State and Lifecycle Management
# ============================================================================

app_state = {}
active_sessions: Dict[str, ClientSession] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup: Create default session
    app_state["default_session"] = ClientSession()
    yield
    # Shutdown: Clean up all sessions
    if "default_session" in app_state:
        await app_state["default_session"].close()
    for session in active_sessions.values():
        await session.close()
    active_sessions.clear()


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Life360 Tracker API",
    description="""
    ## Overview
    
    This API provides comprehensive access to Life360 location tracking data.
    
    ## Authentication
    
    All endpoints require a Life360 Bearer token. You can provide it in two ways:
    
    1. **Authorization Header** (Recommended):
       ```
       Authorization: Bearer YOUR_TOKEN_HERE
       ```
    
    2. **Environment Variable** (Fallback):
       Set `LIFE360_AUTHORIZATION` with your token
    
    ## Features
    
    - 📍 **Location Tracking**: Real-time member locations
    - 👥 **Circle Management**: View circles and members
    - 📊 **Analytics**: Statistics and insights
    - 🔍 **Search**: Find members across circles
    - 🔋 **Battery Monitoring**: Track device battery levels
    - 🚗 **Driving Detection**: See who's currently driving
    
    ## Rate Limiting
    
    Please be mindful of Life360's rate limits. This API includes retry logic
    but excessive requests may result in temporary blocks.
    """,
    version="2.0.0",
    lifespan=lifespan,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
        401: {"model": ErrorResponse, "description": "Authentication failed"},
        404: {"model": ErrorResponse, "description": "Resource not found"}
    }
)

# Add CORS middleware for frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Dependencies
# ============================================================================

def get_life360_api(
    authorization: Optional[str] = Header(None, description="Bearer token for Life360 API")
) -> Life360:
    """
    Get Life360 API client instance.
    
    Attempts to use the Authorization header first, falls back to environment variable.
    Creates a new session for each unique token to support multiple users.
    """
    # Try header first
    if authorization and authorization.startswith("Bearer "):
        token = authorization
    elif authorization:  # Add Bearer prefix if missing
        token = f"Bearer {authorization}"
    else:
        # Fall back to environment variable
        env_token = os.getenv("LIFE360_AUTHORIZATION")
        if not env_token:
            raise HTTPException(
                status_code=401,
                detail="No authorization provided. Pass Bearer token in Authorization header."
            )
        token = f"Bearer {env_token}" if not env_token.startswith("Bearer ") else env_token
    
    # Create or reuse session for this token
    if token not in active_sessions:
        active_sessions[token] = ClientSession()
    
    return Life360(
        session=active_sessions[token],
        authorization=token,
        max_retries=3
    )


# ============================================================================
# Helper Functions
# ============================================================================

def parse_member_status(member: Dict[str, Any]) -> str:
    """Determine member status from their data."""
    if member.get("issues", {}).get("disconnected") == "1":
        return "Disconnected"
    elif member.get("features", {}).get("shareLocation") == "0":
        return "Location Off"
    elif member.get("location") is None:
        return "No Location"
    return "Active"


def parse_location(location_data: Optional[Dict[str, Any]]) -> Optional[LocationData]:
    """Parse location data from API response."""
    if not location_data:
        return None
    
    try:
        return LocationData(
            latitude=float(location_data.get("latitude", 0)),
            longitude=float(location_data.get("longitude", 0)),
            accuracy=int(location_data.get("accuracy", 0)),
            name=location_data.get("name"),
            address1=location_data.get("address1"),
            address2=location_data.get("address2"),
            battery=int(location_data.get("battery")) if location_data.get("battery") else None,
            timestamp=location_data.get("timestamp", ""),
            speed=float(location_data.get("speed")) if location_data.get("speed") else None,
            isDriving=location_data.get("isDriving") == "1"
        )
    except (ValueError, TypeError) as e:
        return None


def create_member_summary(member: Dict[str, Any]) -> MemberSummary:
    """Create a simplified member summary from raw API data."""
    first_name = member.get("firstName", "")
    last_name = member.get("lastName", "")
    
    # Extract contact info
    phone = member.get("loginPhone")
    email = member.get("loginEmail")
    
    # Try to get from communications if not in main fields
    if not phone or not email:
        for comm in member.get("communications", []):
            if comm.get("channel") == "Voice" and not phone:
                phone = comm.get("value")
            elif comm.get("channel") == "Email" and not email:
                email = comm.get("value")
    
    return MemberSummary(
        id=member["id"],
        firstName=first_name,
        lastName=last_name,
        full_name=f"{first_name} {last_name}".strip(),
        status=parse_member_status(member),
        location=parse_location(member.get("location")),
        avatar=member.get("avatar"),
        phone=phone,
        email=email
    )


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", 
    summary="API Health Check",
    tags=["System"],
    response_model=Dict[str, str]
)
async def health_check():
    """Check if the API is running and healthy."""
    return {
        "status": "healthy",
        "service": "Life360 Tracker API",
        "version": "2.0.0"
    }


@app.post("/auth/validate",
    summary="Validate Token",
    tags=["Authentication"],
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Token is valid"},
        401: {"description": "Invalid token"}
    }
)
async def validate_token(api: Life360 = Depends(get_life360_api)):
    """
    Validate a Life360 token by attempting to fetch circles.
    
    This is useful for frontend applications to verify token validity
    before making other API calls.
    """
    try:
        circles = await api.get_circles()
        return {
            "valid": True,
            "message": "Token is valid",
            "circles_count": len(circles)
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or API error")


@app.get("/circles",
    summary="List All Circles",
    tags=["Circles"],
    response_model=List[CircleInfo],
    responses={
        200: {"description": "List of circles"}
    }
)
async def get_circles(api: Life360 = Depends(get_life360_api)) -> List[Dict[str, str]]:
    """
    Retrieve all circles associated with the authenticated Life360 account.
    
    Circles are groups of members who share their locations with each other.
    """
    try:
        return await api.get_circles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}",
    summary="Get Circle Details",
    tags=["Circles"],
    response_model=Dict[str, Any]
)
async def get_circle(
    circle_id: str = Path(..., description="The unique circle identifier"),
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, Any]:
    """Get detailed information about a specific circle including all members."""
    try:
        return await api.get_circle(circle_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}/members",
    summary="List Circle Members",
    tags=["Members"],
    response_model=List[MemberSummary],
    responses={
        200: {"description": "List of circle members with their current status"}
    }
)
async def get_circle_members(
    circle_id: str = Path(..., description="The unique circle identifier"),
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSummary]:
    """
    Get all members of a specific circle with their current location status.
    
    Returns simplified member information including:
    - Personal details (name, contact info)
    - Current status (Active, Disconnected, etc.)
    - Location data if available
    """
    try:
        members_data = await api.get_circle_members(circle_id)
        return [create_member_summary(member) for member in members_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}/members/{member_id}",
    summary="Get Member Details",
    tags=["Members"],
    response_model=Dict[str, Any]
)
async def get_member(
    circle_id: str = Path(..., description="The unique circle identifier"),
    member_id: str = Path(..., description="The unique member identifier"),
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, Any]:
    """Get detailed information about a specific member in a circle."""
    try:
        return await api.get_circle_member(circle_id, member_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/me",
    summary="Get Current User",
    tags=["User"],
    response_model=Dict[str, Any]
)
async def get_me(api: Life360 = Depends(get_life360_api)) -> Dict[str, Any]:
    """Get information about the currently authenticated Life360 user."""
    try:
        return await api.get_me()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/members/all",
    summary="Get All Members",
    tags=["Members"],
    response_model=Dict[str, List[MemberSummary]],
    responses={
        200: {"description": "Dictionary mapping circle names to their members"}
    }
)
async def get_all_members(
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, List[MemberSummary]]:
    """
    Get all members from all circles organized by circle name.
    
    This endpoint fetches all circles and their members in one call,
    useful for getting a complete overview of all tracked individuals.
    """
    try:
        circles = await api.get_circles()
        result = {}
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            members = [create_member_summary(member) for member in members_data]
            result[circle["name"]] = members
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/members/active",
    summary="Get Active Members",
    tags=["Members"],
    response_model=Dict[str, List[MemberSummary]]
)
async def get_active_members(
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, List[MemberSummary]]:
    """
    Get all members with active location sharing across all circles.
    
    Filters out members who are:
    - Disconnected
    - Have location sharing turned off
    - Have no location data
    """
    try:
        all_members = await get_all_members(api)
        
        active_members = {}
        for circle_name, members in all_members.items():
            active = [m for m in members if m.status == "Active" and m.location]
            if active:
                active_members[circle_name] = active
        
        return active_members
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/members/search",
    summary="Search Members",
    tags=["Members"],
    response_model=List[Dict[str, Any]]
)
async def search_members(
    name: str = Query(..., description="Name to search for (case-insensitive)", min_length=1),
    api: Life360 = Depends(get_life360_api)
) -> List[Dict[str, Any]]:
    """
    Search for members by name across all circles.
    
    Performs a case-insensitive search on both first and last names.
    Returns matching members along with their circle information.
    """
    try:
        circles = await api.get_circles()
        results = []
        
        search_term = name.lower()
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                full_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                if search_term in full_name.lower():
                    results.append({
                        "circle": circle["name"],
                        "circle_id": circle["id"],
                        "member": create_member_summary(member)
                    })
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/locations/current",
    summary="Get Current Locations",
    tags=["Locations"],
    response_model=List[BatchMemberLocation]
)
async def get_current_locations(
    only_active: bool = Query(True, description="Only return members with active locations"),
    api: Life360 = Depends(get_life360_api)
) -> List[BatchMemberLocation]:
    """
    Get current locations for all members across all circles.
    
    Returns a flat list of all member locations with circle context.
    Useful for mapping applications that need all locations at once.
    """
    try:
        circles = await api.get_circles()
        locations = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                member_summary = create_member_summary(member)
                
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/locations/driving",
    summary="Get Driving Members",
    tags=["Locations"],
    response_model=List[MemberSummary]
)
async def get_driving_members(
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSummary]:
    """
    Get all members who are currently driving.
    
    Checks the isDriving flag and returns only members who are
    actively driving at the time of the request.
    """
    try:
        all_locations = await get_current_locations(only_active=True, api=api)
        
        driving_members = []
        seen_ids = set()  # Avoid duplicates if member is in multiple circles
        
        for loc in all_locations:
            if loc.location and loc.location.is_driving and loc.member_id not in seen_ids:
                # Fetch full member data to create summary
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics",
    summary="Get Statistics",
    tags=["Analytics"],
    response_model=List[CircleStatistics]
)
async def get_statistics(
    api: Life360 = Depends(get_life360_api)
) -> List[CircleStatistics]:
    """
    Get statistical summary for all circles.
    
    Provides analytics including:
    - Member counts by status
    - Average battery levels
    - Most recent update times
    """
    try:
        circles = await api.get_circles()
        stats = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            total = len(members_data)
            active = 0
            disconnected = 0
            location_off = 0
            battery_sum = 0
            battery_count = 0
            latest_timestamp = 0
            
            for member in members_data:
                status = parse_member_status(member)
                
                if status == "Active":
                    active += 1
                    location = member.get("location", {})
                    if location.get("battery"):
                        battery_sum += int(location["battery"])
                        battery_count += 1
                    if location.get("timestamp"):
                        timestamp = int(location["timestamp"])
                        latest_timestamp = max(latest_timestamp, timestamp)
                elif status == "Disconnected":
                    disconnected += 1
                elif status == "Location Off":
                    location_off += 1
            
            stats.append(CircleStatistics(
                circle_id=circle["id"],
                circle_name=circle["name"],
                total_members=total,
                active_members=active,
                disconnected_members=disconnected,
                location_off_members=location_off,
                average_battery=battery_sum / battery_count if battery_count > 0 else None,
                last_update=datetime.fromtimestamp(latest_timestamp) if latest_timestamp > 0 else datetime.now()
            ))
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/battery/low",
    summary="Get Low Battery Members",
    tags=["Analytics"],
    response_model=List[Dict[str, Any]]
)
async def get_low_battery_members(
    threshold: int = Query(20, description="Battery percentage threshold", ge=0, le=100),
    api: Life360 = Depends(get_life360_api)
) -> List[Dict[str, Any]]:
    """
    Find all members with battery levels below the specified threshold.
    
    Useful for monitoring members who may need to charge their devices soon.
    """
    try:
        all_locations = await get_current_locations(only_active=True, api=api)
        
        low_battery = []
        for loc in all_locations:
            if loc.location and loc.location.battery is not None and loc.location.battery <= threshold:
                low_battery.append({
                    "circle": loc.circle_name,
                    "member": loc.member_name,
                    "battery": loc.location.battery,
                    "location": loc.location.name or "Unknown"
                })
        
        # Sort by battery level (lowest first)
        low_battery.sort(key=lambda x: x["battery"])
        
        return low_battery
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)