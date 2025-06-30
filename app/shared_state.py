"""
Shared state module for Life360 API clients
"""
from typing import Optional
from aiohttp import ClientSession
from life360 import Life360

# Shared state that will be initialized by the main app
shared_state = {
    "session": None,
    "life360_client": None
}

def get_session() -> Optional[ClientSession]:
    """Get the shared aiohttp session"""
    return shared_state.get("session")

def get_life360_client() -> Optional[Life360]:
    """Get the shared Life360 client"""
    return shared_state.get("life360_client")