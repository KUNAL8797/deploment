"""
Production configuration for the AI Innovation Incubator API
"""
import os
import secrets
from typing import List


class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # Application
        self.app_name = "AI Innovation Idea Incubator"
        self.app_version = "1.0.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./ai_incubator.db")
        
        # Redis Cache
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # AI Service
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Parse CORS origins from environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]
        else:
            # Default CORS origins for development
            self.cors_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        
        # Fix PostgreSQL URL for SQLAlchemy compatibility
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()