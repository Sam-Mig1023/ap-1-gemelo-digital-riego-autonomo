"""Sensor Telemetry endpoints"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

router = APIRouter()

# Mock sensor data
MOCK_SENSORS = {
    "sensor-z1-001": {
        "id": "sensor-z1-001",
        "zoneId": "zone-1-nw",
        "name": "Sensor Humedad Zona 1",
        "type": "soil_moisture",
        "location": {"depth_cm": 10},
        "lastReading": {
            "timestamp": "2026-08-31T14:25:00Z",
            "value": 28.5,
            "unit": "%"
        },
        "status": "active"
    },
    "sensor-z1-002": {
        "id": "sensor-z1-002",
        "zoneId": "zone-1-nw",
        "name": "Sensor Temperatura Canopia Zona 1",
        "type": "canopy_temperature",
        "location": {"height_m": 1.5},
        "lastReading": {
            "timestamp": "2026-08-31T14:25:00Z",
            "value": 24.3,
            "unit": "°C"
        },
        "status": "active"
    }
}


@router.get("/")
async def list_sensors():
    """Get list of all sensors"""
    return {
        "sensors": list(MOCK_SENSORS.values()),
        "total": len(MOCK_SENSORS)
    }


@router.get("/{sensor_id}")
async def get_sensor(sensor_id: str):
    """Get specific sensor details"""
    if sensor_id not in MOCK_SENSORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor {sensor_id} not found"
        )
    return MOCK_SENSORS[sensor_id]


@router.post("/telemetry/ingest")
async def ingest_telemetry(data: dict):
    """Ingest sensor telemetry data"""
    return {
        "status": "success",
        "message": "Telemetry data ingested",
        "recordsProcessed": len(data.get("readings", [])),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/zone/{zone_id}")
async def get_zone_sensors(zone_id: str):
    """Get all sensors for a specific zone"""
    zone_sensors = [s for s in MOCK_SENSORS.values() if s["zoneId"] == zone_id]
    
    if not zone_sensors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sensors found for zone {zone_id}"
        )
    
    return {
        "zoneId": zone_id,
        "sensors": zone_sensors,
        "total": len(zone_sensors)
    }
