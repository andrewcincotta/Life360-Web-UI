"""
Life360 FastAPI Application
A REST API for accessing Life360 data with proper type hints
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
from life360 import Life360
from app.shared_state import get_life360_client

# Pydantic models for request/response (simpler than full OOD)
class CircleResponse(BaseModel):
    """Response model for circle data"""
    id: str
    name: str
    created_at: str = Field(alias="createdAt")
    
    class Config:
        populate_by_name = True


class LocationData(BaseModel):
    """Location information"""
    latitude: float
    longitude: float
    accuracy: int
    name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    battery: Optional[int] = None
    timestamp: str
    

class MemberSummary(BaseModel):
    """Simplified member information for responses"""
    id: str
    first_name: str = Field(alias="firstName")
    last_name: Optional[str] = Field(alias="lastName")
    full_name: str
    status: str
    location: Optional[LocationData] = None
    
    class Config:
        populate_by_name = True


class MemberLocationHistory(BaseModel):
    """Model for storing location history (for future DB integration)"""
    member_id: str
    circle_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    battery: Optional[int] = None


# Create FastAPI app without lifespan
app = FastAPI(
    title="Life360 API V2",
    description="REST API for accessing Life360 location data with Pydantic models",
    version="2.0.0"
)


# Dependency to get Life360 API client
def get_life360_api() -> Life360:
    """Get the Life360 API client instance"""
    client = get_life360_client()
    if not client:
        raise HTTPException(status_code=500, detail="Life360 client not initialized")
    return client


# Helper functions with type hints
def parse_member_status(member: Dict[str, Any]) -> str:
    """
    Determine member status from their data
    
    Args:
        member: Raw member data from API
        
    Returns:
        Status string: "Active", "Disconnected", "Location Off", or "No Location"
    """
    if member.get("issues", {}).get("disconnected") == "1":
        return "Disconnected"
    elif member.get("features", {}).get("shareLocation") == "0":
        return "Location Off"
    elif member.get("location") is None:
        return "No Location"
    return "Active"


def parse_location(location_data: Optional[Dict[str, Any]]) -> Optional[LocationData]:
    """
    Parse location data from API response
    
    Args:
        location_data: Raw location data from API
        
    Returns:
        LocationData model or None
    """
    if not location_data:
        return None
        
    return LocationData(
        latitude=float(location_data.get("latitude", 0)),
        longitude=float(location_data.get("longitude", 0)),
        accuracy=int(location_data.get("accuracy", 0)),
        name=location_data.get("name"),
        address1=location_data.get("address1"),
        address2=location_data.get("address2"),
        battery=int(location_data.get("battery", 0)) if location_data.get("battery") else None,
        timestamp=location_data.get("timestamp", "")
    )


def create_member_summary(member: Dict[str, Any]) -> MemberSummary:
    """
    Create a simplified member summary from raw API data
    
    Args:
        member: Raw member data from API
        
    Returns:
        MemberSummary model
    """
    first_name = member.get("firstName", "")
    last_name = member.get("lastName", "")
    
    return MemberSummary(
        id=member["id"],
        firstName=first_name,
        lastName=last_name,
        full_name=f"{first_name} {last_name}".strip(),
        status=parse_member_status(member),
        location=parse_location(member.get("location"))
    )


# API Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Life360 API", "version": "v2"}


@app.get("/circles", response_model=List[CircleResponse])
async def get_circles(api: Life360 = Depends(get_life360_api)) -> List[Dict[str, str]]:
    """
    Get all circles for the authenticated user
    
    Returns:
        List of circles with basic information
    """
    try:
        circles = await api.get_circles()
        return circles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}/members", response_model=List[MemberSummary])
async def get_circle_members(
    circle_id: str,
    api: Life360 = Depends(get_life360_api)
) -> List[MemberSummary]:
    """
    Get all members in a specific circle
    
    Args:
        circle_id: The circle ID
        
    Returns:
        List of member summaries with current location
    """
    try:
        members_data = await api.get_circle_members(circle_id)
        return [create_member_summary(member) for member in members_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/members/all")
async def get_all_members(api: Life360 = Depends(get_life360_api)) -> Dict[str, List[MemberSummary]]:
    """
    Get all members from all circles
    
    Returns:
        Dictionary mapping circle names to member lists
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


@app.get("/members/active")
async def get_active_members(api: Life360 = Depends(get_life360_api)) -> Dict[str, List[MemberSummary]]:
    """
    Get all members with active locations
    
    Returns:
        Dictionary mapping circle names to lists of active members
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


@app.get("/members/search")
async def search_members(
    name: str,
    api: Life360 = Depends(get_life360_api)
) -> List[Dict[str, Any]]:
    """
    Search for members by name across all circles
    
    Args:
        name: Name to search for (case-insensitive)
        
    Returns:
        List of matching members with their circle information
    """
    try:
        circles = await api.get_circles()
        results = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                full_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                if name.lower() in full_name.lower():
                    results.append({
                        "circle": circle["name"],
                        "circle_id": circle["id"],
                        "member": create_member_summary(member)
                    })
                    
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/locations/current")
async def get_current_locations(api: Life360 = Depends(get_life360_api)) -> List[Dict[str, Any]]:
    """
    Get current locations for all active members
    
    Returns:
        Flat list of all member locations with circle info
    """
    try:
        circles = await api.get_circles()
        locations = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                if member.get("location") and parse_member_status(member) == "Active":
                    locations.append({
                        "circle_name": circle["name"],
                        "circle_id": circle["id"],
                        "member_id": member["id"],
                        "member_name": f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        "location": parse_location(member.get("location"))
                    })
                    
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/locations/track/{member_id}")
async def start_tracking_member(
    member_id: str,
    background_tasks: BackgroundTasks,
    interval_seconds: int = 300,  # 5 minutes default
    api: Life360 = Depends(get_life360_api)
) -> Dict[str, str]:
    """
    Start tracking a member's location (for future DB integration)
    
    Args:
        member_id: Member ID to track
        interval_seconds: Polling interval in seconds
        
    Returns:
        Confirmation message
    """
    # This is a placeholder for future implementation with database
    # In production, you'd want to use a proper task queue like Celery
    
    async def track_location():
        # This would save to PostgreSQL in the future
        pass
    
    background_tasks.add_task(track_location)
    
    return {
        "status": "tracking_started",
        "member_id": member_id,
        "interval": interval_seconds
    }


# WebSocket endpoint for real-time updates (future enhancement)
# Store active websocket connections
active_connections: Set[WebSocket] = set()


@app.websocket("/ws/locations")
async def websocket_locations(websocket: WebSocket):
    """
    WebSocket endpoint for real-time location updates
    Useful for React frontend to get live updates
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # In production, this would push updates when locations change
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "path": request.url.path}


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return {"error": "Internal server error"}