import os
from dotenv import load_dotenv
import uvicorn

if __name__ == "__main__":
    load_dotenv()

    # Grab with defaults and proper types
    host = os.getenv("FASTAPI_HOST", "127.0.0.1")
    port = int(os.getenv("FASTAPI_PORT", 8000))

    # Pass the app as an import string to enable reload
    uvicorn.run(
        "app.main:app",  # Import string format: "module:app"
        host=host,
        port=port,
        reload=True,
    )