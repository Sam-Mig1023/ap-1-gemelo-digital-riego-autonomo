"""
API v1 Router - Main entry point for all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, fields, sensors, rl_engine, irrigation, reports

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(fields.router, prefix="/fields", tags=["Agricultural Fields"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry"])
api_router.include_router(rl_engine.router, prefix="/rl-engine", tags=["RL Agent"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Irrigation Control"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

__all__ = ["api_router"]
