"""
API v1 Router - Main entry point for all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, fields, sensors, rl_engine, irrigation, reports, chat, dataset, crop_calendar, langflow_router

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(fields.router, prefix="/fields", tags=["Agricultural Fields"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry"])
api_router.include_router(rl_engine.router, prefix="/rl-engine", tags=["RL Agent"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Irrigation Control"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(chat.router, tags=["Chat & RAG"])
api_router.include_router(langflow_router.router, prefix="/langflow", tags=["Visual Flow Engine"])
api_router.include_router(dataset.router, prefix="/dataset", tags=["Dataset Export"])
api_router.include_router(crop_calendar.router, prefix="/crop-calendar", tags=["🌱 Crop Calendar & Phenology AI"])

__all__ = ["api_router"]
