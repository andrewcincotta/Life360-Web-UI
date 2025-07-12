"""
Helper functions for processing Life360 API data.
"""
from typing import Dict, Any, Optional

from ..models.responses import LocationData, MemberSummary


def parse_member_status(member: Dict[str, Any]) -> str:
    """
    Determine member status from their raw API data.
    
    Args:
        member: Raw member data from Life360 API
        
    Returns:
        Status string: "Active", "Disconnected", "Location Off", or "No Location"
    """
    # Check for disconnection issues
    if member.get("issues", {}).get("disconnected") == "1":
        return "Disconnected"
    
    # Check if location sharing is disabled
    elif member.get("features", {}).get("shareLocation") == "0":
        return "Location Off"
    
    # Check if location data exists
    elif member.get("location") is None:
        return "No Location"
    
    return "Active"


def parse_location(location_data: Optional[Dict[str, Any]]) -> Optional[LocationData]:
    """
    Parse location data from API response into LocationData model.
    
    Args:
        location_data: Raw location dictionary from API
        
    Returns:
        LocationData model or None if parsing fails
    """
    if not location_data:
        return None
    
    try:
        # Convert string values to appropriate types
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
        # Log error in production
        return None


def create_member_summary(member: Dict[str, Any]) -> MemberSummary:
    """
    Create a simplified member summary from raw API data.
    
    This function extracts relevant fields and creates a clean
    MemberSummary object suitable for API responses.
    
    Args:
        member: Raw member data from Life360 API
        
    Returns:
        MemberSummary model with processed data
    """
    # Extract basic info
    first_name = member.get("firstName", "")
    last_name = member.get("lastName", "")
    
    # Extract contact info - check multiple possible locations
    phone = member.get("loginPhone")
    email = member.get("loginEmail")
    
    # Try to get contact info from communications array if not in main fields
    if not phone or not email:
        for comm in member.get("communications", []):
            if comm.get("channel") == "Voice" and not phone:
                phone = comm.get("value")
            elif comm.get("channel") == "Email" and not email:
                email = comm.get("value")
    
    # Create the summary
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


def extract_battery_info(member: Dict[str, Any]) -> Optional[int]:
    """
    Extract battery percentage from member data.
    
    Args:
        member: Raw member data
        
    Returns:
        Battery percentage or None
    """
    location = member.get("location", {})
    battery = location.get("battery")
    
    if battery is not None:
        try:
            return int(battery)
        except (ValueError, TypeError):
            pass
    
    return None