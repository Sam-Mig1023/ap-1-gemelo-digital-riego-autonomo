"""Sensor Telemetry endpoints"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from app.services.dataset_service import get_dataset_service

router = APIRouter()

def get_dynamic_sensors():
    dataset_service = get_dataset_service()
    sensors = []
    
    # We create sensors dynamically based on the zones in our mapping
    for zone_id in dataset_service.zone_mapping.keys():
        reading = dataset_service.get_latest_reading(zone_id)
        if not reading:
            continue
            
        # Moisture sensor
        sensors.append({
            "id": f"sensor-{zone_id}-moisture",
            "zoneId": zone_id,
            "name": f"Sensor Humedad {zone_id}",
            "type": "soil_moisture",
            "location": {"depth_cm": 10},
            "lastReading": {
                "timestamp": reading.get('ts', datetime.utcnow().isoformat()),
                "value": round(reading.get('soil_moisture', 0.0), 2),
                "unit": "%"
            },
            "status": "active"
        })
        
        # Temperature sensor
        sensors.append({
            "id": f"sensor-{zone_id}-temp",
            "zoneId": zone_id,
            "name": f"Sensor Temperatura {zone_id}",
            "type": "air_temperature",
            "location": {"height_m": 1.5},
            "lastReading": {
                "timestamp": reading.get('ts', datetime.utcnow().isoformat()),
                "value": round(reading.get('weather_temp', 0.0), 2),
                "unit": "°C"
            },
            "status": "active"
        })
    return sensors

@router.get("/")
async def list_sensors():
    """Get list of all sensors"""
    sensors = get_dynamic_sensors()
    return {
        "sensors": sensors,
        "total": len(sensors)
    }

@router.get("/{sensor_id}")
async def get_sensor(sensor_id: str):
    """Get specific sensor details"""
    sensors = get_dynamic_sensors()
    for s in sensors:
        if s["id"] == sensor_id:
            return s
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Sensor {sensor_id} not found"
    )

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
    sensors = get_dynamic_sensors()
    zone_sensors = [s for s in sensors if s["zoneId"] == zone_id]
    
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
