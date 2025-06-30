"""Minimal FastAPI app"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any
import os
from aiohttp import ClientSession
from life360 import Life360

# Global state
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    app_state["session"] = ClientSession()
    app_state["api"] = Life360(
        session=app_state["session"],
        authorization=f'Bearer {os.getenv("LIFE360_AUTHORIZATION")}'
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