import uvicorn
from fastapi import FastAPI

from src.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, PORT, HOST, LOG_LEVEL, DATA_DIR, WEBHOOK_SECRET, BROKERAGE_NAME
from src.routes import webhook_router, api_router


def create_app() -> FastAPI:
    """Set up FastAPI app with routes"""
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION
    )
    
    # Include routers
    app.include_router(webhook_router)
    app.include_router(api_router)
    
    return app


# Create app instance
app = create_app()


def main():
    """Start the server"""
    print("\n" + "=" * 60)
    print(f"Starting {BROKERAGE_NAME} Webhook Server")
    print("=" * 60)
    print(f"Port: {PORT}")
    print(f"Data Directory: {DATA_DIR.absolute()}")
    print(f"Webhook Secret: {'Configured' if WEBHOOK_SECRET != 'your-webhook-secret-key' else 'Using default (change this!)'}")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL,
        reload=True
    )


if __name__ == "__main__":
    main()
