"""
Life360 FastAPI Application - Main entry point.

This module initializes the FastAPI application, configures middleware,
and includes all routers. Business logic is separated into other modules.
"""
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aiohttp import ClientSession

# Import routers
from .routers import auth, circles, members, locations, analytics

# Import models for documentation
from .models.responses import ErrorResponse

# Global state for session management
app_state: Dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Creates an aiohttp session on startup and closes it on shutdown.
    """
    # Startup: Create shared session
    app_state["default_session"] = ClientSession()
    
    yield
    
    # Shutdown: Clean up session
    if "default_session" in app_state:
        await app_state["default_session"].close()


# Create FastAPI application
app = FastAPI(
    title="Life360 Tracker API",
    description="""
    ## 🚀 Overview
    
    This API provides comprehensive access to Life360 location tracking data.
    Built with FastAPI for high performance and automatic documentation.
    
    ## 🔐 Authentication
    
    All endpoints (except health check) require a Life360 Bearer token:
    
    **Option 1 - Authorization Header (Recommended):**
    ```
    Authorization: Bearer YOUR_TOKEN_HERE
    ```
    
    **Option 2 - Environment Variable (Fallback):**
    ```bash
    export LIFE360_AUTHORIZATION="Bearer YOUR_TOKEN_HERE"
    ```
    
    ## 📚 Features
    
    - **📍 Location Tracking**: Real-time member locations with address resolution
    - **👥 Circle Management**: View circles and their members
    - **📊 Analytics**: Statistics about circles and member activity
    - **🔍 Member Search**: Find members across all your circles
    - **🔋 Battery Monitoring**: Track device battery levels
    - **🚗 Driving Detection**: See who's currently driving
    
    ## ⚡ Rate Limiting
    
    Please be mindful of Life360's rate limits. This API includes retry logic
    but excessive requests may result in temporary blocks.
    
    ## 🛠️ Error Handling
    
    All errors follow a consistent format with status codes and detailed messages.
    Check the response models for each endpoint.
    """,
    version="2.0.0",
    lifespan=lifespan,
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authentication failed - Invalid or missing token"
        },
        404: {
            "model": ErrorResponse,
            "description": "Resource not found"
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error"
        }
    }
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React development
        "http://localhost:3001",      # Alternative port
        "http://localhost:5173",      # Vite development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(circles.router)
app.include_router(members.router)
app.include_router(locations.router)
app.include_router(analytics.router)


# Root endpoint - no authentication required
@app.get(
    "/",
    tags=["System"],
    summary="API Health Check",
    description="Check if the API is running and healthy. No authentication required."
)
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "Life360 Tracker API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Global exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors with consistent format."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": f"The requested resource was not found: {request.url.path}",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Handle 500 errors with consistent format."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )


# For development/debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)