"""
Helper functions for processing Life360 API data.
"""
from typing import Dict, Any, Optional
import logging

from ..models.responses import LocationData, MemberSummary

# Set up logging
logger = logging.getLogger(__name__)


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
        # Parse individual fields with fallbacks
        
        # Parse coordinates
        try:
            latitude = float(location_data.get("latitude", 0))
            longitude = float(location_data.get("longitude", 0))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse coordinates: lat={location_data.get('latitude')}, lon={location_data.get('longitude')}")
            return None  # Coordinates are essential
        
        # Parse accuracy
        try:
            accuracy = int(float(location_data.get("accuracy", 0)))
        except (ValueError, TypeError):
            accuracy = 0
        
        # Handle speed: -1 means not moving/unknown
        speed = None
        speed_value = location_data.get("speed")
        if speed_value is not None:
            try:
                speed = float(speed_value)
                if speed < 0:
                    speed = None
            except (ValueError, TypeError):
                speed = None
        
        # Handle battery - can be int, float, or string
        battery = None
        battery_value = location_data.get("battery")
        if battery_value is not None:
            try:
                # Convert to float first (handles "60.000003814697266"), then to int
                battery = int(float(battery_value))
                # Ensure it's within valid range
                battery = max(0, min(100, battery))
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse battery value: {battery_value}")
        
        # Parse timestamp - ensure it's a string
        timestamp = str(location_data.get("timestamp", ""))
        
        # Parse boolean isDriving
        is_driving = False
        try:
            is_driving = str(location_data.get("isDriving", "0")) == "1"
        except:
            pass
        
        # Create the LocationData object
        return LocationData(
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            name=location_data.get("name"),
            address1=location_data.get("address1"),
            address2=location_data.get("address2"),
            battery=battery,
            timestamp=timestamp,
            speed=speed,
            is_driving=is_driving
        )
        
    except Exception as e:
        logger.error(f"Unexpected error parsing location: {e}, data: {location_data}")
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


def debug_parse_location(location_data: Optional[Dict[str, Any]], member_name: str = "Unknown") -> Optional[LocationData]:
    """
    Debug version of parse_location that logs detailed parsing information.
    
    Args:
        location_data: Raw location dictionary from API
        member_name: Member name for logging context
        
    Returns:
        LocationData model or None if parsing fails
    """
    logger.info(f"Parsing location for {member_name}")
    
    if not location_data:
        logger.info(f"No location data for {member_name}")
        return None
    
    # Log raw data
    logger.debug(f"Raw location data for {member_name}: {location_data}")
    
    # Try parsing with detailed logging
    result = parse_location(location_data)
    
    if result is None:
        logger.warning(f"Failed to parse location for {member_name}")
        # Log specific field values that might be problematic
        logger.debug(f"  latitude: {location_data.get('latitude')} (type: {type(location_data.get('latitude'))})")
        logger.debug(f"  longitude: {location_data.get('longitude')} (type: {type(location_data.get('longitude'))})")
        logger.debug(f"  battery: {location_data.get('battery')} (type: {type(location_data.get('battery'))})")
        logger.debug(f"  speed: {location_data.get('speed')} (type: {type(location_data.get('speed'))})")
        logger.debug(f"  isDriving: {location_data.get('isDriving')} (type: {type(location_data.get('isDriving'))})")
    else:
        logger.info(f"Successfully parsed location for {member_name}")
    
    return result