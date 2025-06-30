"""Minimal FastAPI app"""
import os

from life360 import Life360
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from aiohttp import ClientSession

# Global state
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    app_state["session"] = ClientSession()
    app_state["api"] = Life360(
        session=app_state["session"],
        authorization=f'Bearer {os.getenv("LIFE360_AUTHORIZATION")}',
        max_retries=3
    )
    yield
    # Shutdown
    await app_state["session"].close()


app = FastAPI(title="Life360 API", lifespan=lifespan)


# Dependency
def get_api() -> Life360:
    return app_state["api"]


# Move your routes here
@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/circles")
async def get_circles(api: Life360 = Depends(get_api)) -> List[Dict[str, str]]:
    try:
        return await api.get_circles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}/members")
async def get_members(
    circle_id: str,
    api: Life360 = Depends(get_api)
) -> List[Dict[str, Any]]:
    try:
        return await api.get_circle_members(circle_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/me")
async def get_me(api: Life360 = Depends(get_api)) -> Dict[str, Any]:
    try:
        return await api.get_me()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circles/{circle_id}/members/{member_id}")
async def get_member(
    circle_id: str,
    member_id: str,
    api: Life360 = Depends(get_api)
) -> Dict[str, Any]:
    try:
        return await api.get_circle_member(circle_id, member_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))