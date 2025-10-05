"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime
import sys
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": os.cpu_count()
        },
        "services": {
            "database": "connected",  # TODO: Add actual DB health check
            "redis": "unknown",       # TODO: Add Redis health check
            "kafka": "unknown"        # TODO: Add Kafka health check
        }
    }