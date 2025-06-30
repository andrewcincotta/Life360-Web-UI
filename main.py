"""
Main application that combines v1 and v2 APIs with versioned routing
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiohttp import ClientSession
from life360 import Life360
from app.shared_state import shared_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup shared resources"""
    # Startup: Create shared resources
    session = ClientSession()
    life360_client = Life360(
        session=session,
        authorization=f'Bearer {os.getenv("LIFE360_AUTHORIZATION")}',
        max_retries=3
    )
    
    # Store in shared state
    shared_state["session"] = session
    shared_state["life360_client"] = life360_client
    
    yield
    
    # Shutdown: Cleanup resources
    await session.close()


# Create main application with lifespan
app = FastAPI(
    title="Life360 API Gateway",
    description="Life360 API with multiple versions",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Life360 API Gateway",
        "versions": {
            "v1": {
                "docs": "/v1/docs",
                "openapi": "/v1/openapi.json",
                "base_url": "/v1",
                "description": "Minimal API version"
            },
            "v2": {
                "docs": "/v2/docs",
                "openapi": "/v2/openapi.json",
                "base_url": "/v2",
                "description": "Pydantic-enhanced API version with WebSocket support"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "life360_initialized": shared_state.get("life360_client") is not None
    }

# Import and mount sub-applications
from app.minimal import app as v1_app
from app.pydantic_api import app as v2_app

# Mount versioned APIs
app.mount("/v1", v1_app)
app.mount("/v2", v2_app)