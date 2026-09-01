"""
Configuration settings for VRI Digital Twin API
"""
import os
from typing import List


class Settings:
    """Application settings - Simple config without external dependencies"""
    
    # API Settings
    API_TITLE: str = "VRI Digital Twin API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database Settings (not required for this demo)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://vri_admin:vri_secure_pass_2026@localhost:5432/vri_digital_twin"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Redis Settings (not required for this demo)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ML/RL Model Settings
    RL_MODEL_VERSION: str = "PPO-VRI-DualReward-v4.2"
    ANOMALY_DETECTION_THRESHOLD: float = 0.85
    ANOMALY_DETECTION_METHOD: str = "isolation_forest"
    
    # Irrigation Control
    MAX_IRRIGATION_DEPTH_MM: float = 100.0
    MIN_IRRIGATION_DEPTH_MM: float = 0.5
    EXECUTION_WINDOW_BUFFER_HOURS: int = 1
    
    # Telemetry Settings
    TELEMETRY_BATCH_SIZE: int = 100
    TELEMETRY_RETENTION_DAYS: int = 90
    
    # Report Generation
    REPORT_OUTPUT_DIR: str = os.getenv("REPORT_OUTPUT_DIR", "./reports")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Create global settings instance
settings = Settings()
