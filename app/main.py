"""
AI Travel Planner - Main FastAPI Application

This is the entry point for the AI Travel Planner application.
It sets up the FastAPI app with all routers and middleware.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.api.routes import auth, itinerary, agents, health
from app.core.database import init_db

# Setup logging
setup_logging()
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Travel Planner application")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Travel Planner application")


# Create FastAPI application
app = FastAPI(
    title="AI Travel Planner",
    description="Intelligent automated itinerary planning system with multi-agent AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com", "api.yourdomain.com"]
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(itinerary.router, prefix="/api/v1/itinerary", tags=["Itinerary"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Travel Planner API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "healthy"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", exc_info=exc, path=str(request.url))
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )