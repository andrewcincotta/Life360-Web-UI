"""
Main application that combines v1 and v2 APIs with versioned routing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import both API applications
from app.minimal import app as v1_app
from app.pydantic_api import app as v2_app

# Create main application
app = FastAPI(
    title="Life360 API - All Versions",
    description="Life360 API with multiple versions",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount v1 and v2 as sub-applications
app.mount("/v1", v1_app)
app.mount("/v2", v2_app)

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Life360 API Gateway",
        "versions": {
            "v1": {
                "docs": "/v1/docs",
                "base_url": "/v1",
                "description": "Minimal API version"
            },
            "v2": {
                "docs": "/v2/docs",
                "base_url": "/v2",
                "description": "Pydantic-enhanced API version with WebSocket support"
            }
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}