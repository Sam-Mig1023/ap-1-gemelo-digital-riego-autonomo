"""
FastAPI Main Application Entry Point
Closed-Loop Digital Twin for Autonomous Variable-Rate Irrigation (VRI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vri-digital-twin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("🚀 Initializing VRI Digital Twin API...")
    await init_db()
    logger.info("✅ API Ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API...")
    await close_db()
    logger.info("✅ Goodbye!")


# Create FastAPI application
app = FastAPI(
    title="VRI Closed-Loop Digital Twin API",
    description="Autonomous Variable-Rate Irrigation with Reinforcement Learning & Multi-Sensor Fusion",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VRI Digital Twin API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
