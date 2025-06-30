import os
from dotenv import load_dotenv
import uvicorn

if __name__ == "__main__":
    load_dotenv()

    # Grab with defaults and proper types
    host = os.getenv("FASTAPI_HOST", "127.0.0.1")
    port = int(os.getenv("FASTAPI_PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )
