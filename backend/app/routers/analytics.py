"""
Analytics and statistics API endpoints.
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from life360 import Life360

from ..dependencies import get_life360_api
from ..models.analytics import CircleStatistics, LowBatteryMember
from ..services.life360_helpers import parse_member_status


router = APIRouter(
    tags=["Analytics"],
    responses={
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/statistics",
    response_model=List[CircleStatistics],
    summary="Get Circle Statistics",
    description="""
    Get statistical summary for all circles.
    
    Provides analytics including:
    - Total member count per circle
    - Active vs inactive members
    - Average battery levels
    - Most recent update times
    
    Useful for dashboards and monitoring overall system health.
    """
)
async def get_statistics(
    api: Life360 = Depends(get_life360_api)
) -> List[CircleStatistics]:
    """Get statistics for all circles."""
    try:
        circles = await api.get_circles()
        stats = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            # Initialize counters
            total = len(members_data)
            active = 0
            disconnected = 0
            location_off = 0
            battery_sum = 0
            battery_count = 0
            latest_timestamp = 0
            
            # Process each member
            for member in members_data:
                status = parse_member_status(member)
                
                if status == "Active":
                    active += 1
                    location = member.get("location", {})
                    
                    # Track battery levels
                    if location.get("battery"):
                        try:
                            battery = int(location["battery"])
                            battery_sum += battery
                            battery_count += 1
                        except (ValueError, TypeError):
                            pass
                    
                    # Track latest update
                    if location.get("timestamp"):
                        try:
                            timestamp = int(location["timestamp"])
                            latest_timestamp = max(latest_timestamp, timestamp)
                        except (ValueError, TypeError):
                            pass
                            
                elif status == "Disconnected":
                    disconnected += 1
                elif status == "Location Off":
                    location_off += 1
            
            # Calculate average battery
            avg_battery = None
            if battery_count > 0:
                avg_battery = round(battery_sum / battery_count, 1)
            
            # Determine last update time
            last_update = datetime.now()
            if latest_timestamp > 0:
                last_update = datetime.fromtimestamp(latest_timestamp)
            
            stats.append(CircleStatistics(
                circle_id=circle["id"],
                circle_name=circle["name"],
                total_members=total,
                active_members=active,
                disconnected_members=disconnected,
                location_off_members=location_off,
                average_battery=avg_battery,
                last_update=last_update
            ))
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate statistics: {str(e)}"
        )


@router.get(
    "/battery/low",
    response_model=List[LowBatteryMember],
    summary="Get Low Battery Members",
    description="""
    Find all members with battery levels below the specified threshold.
    
    Useful for:
    - Monitoring members who may need to charge their devices
    - Sending notifications before devices die
    - Dashboard alerts
    
    Results are sorted by battery level (lowest first).
    """
)
async def get_low_battery_members(
    threshold: int = Query(
        20,
        ge=0,
        le=100,
        description="Battery percentage threshold"
    ),
    api: Life360 = Depends(get_life360_api)
) -> List[LowBatteryMember]:
    """Find members with low battery."""
    try:
        # Get all circles and check battery levels
        circles = await api.get_circles()
        low_battery = []
        
        for circle in circles:
            members_data = await api.get_circle_members(circle["id"])
            
            for member in members_data:
                # Check if member is active and has location
                status = parse_member_status(member)
                if status == "Active" and member.get("location"):
                    location = member["location"]
                    
                    # Check battery level
                    if location.get("battery"):
                        try:
                            battery = int(location["battery"])
                            if battery <= threshold:
                                member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                                location_name = location.get("name", "Unknown")
                                
                                low_battery.append(LowBatteryMember(
                                    circle=circle["name"],
                                    member=member_name,
                                    battery=battery,
                                    location=location_name
                                ))
                        except (ValueError, TypeError):
                            pass
        
        # Sort by battery level (lowest first)
        low_battery.sort(key=lambda x: x.battery)
        
        return low_battery
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check battery levels: {str(e)}"
        )