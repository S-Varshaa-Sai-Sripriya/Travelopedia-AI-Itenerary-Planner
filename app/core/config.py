"""
Core configuration settings for the AI Travel Planner application.
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Core Configuration
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    DATABASE_URL: str = "sqlite:///./travel_planner.db"
    
    # AI/LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Travel APIs
    OPENWEATHER_API_KEY: Optional[str] = None
    AVIATIONSTACK_API_KEY: Optional[str] = None
    FIXER_API_KEY: Optional[str] = None
    BOOKING_API_KEY: Optional[str] = None
    
    # Infrastructure
    REDIS_URL: str = "redis://localhost:6379"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Rate Limiting
    API_RATE_LIMIT: int = 100
    CACHE_TTL: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Calendar Integration
    CALENDAR_WEBHOOK_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()