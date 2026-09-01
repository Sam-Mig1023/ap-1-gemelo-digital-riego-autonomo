"""Agricultural Fields endpoints"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# Mock data for fields
MOCK_FIELDS = {
    "field-001": {
        "id": "field-001",
        "name": "Campo San Pablo Sector A",
        "cropName": "Maíz Amarillo Duro",
        "cropVariety": "Dekalb DK7088",
        "cropStage": "VT (Flowering)",
        "areaHectares": 150.5,
        "soilType": "Franco Limosa",
        "location": {"latitude": -9.1795, "longitude": -75.2268},
        "irrigationMethod": "Central Pivot",
        "createdAt": "2024-01-15T10:00:00Z"
    }
}

MOCK_ZONES = {
    "zone-1-nw": {
        "id": "zone-1-nw",
        "fieldId": "field-001",
        "name": "Zona 1 (Noroeste)",
        "sector": "NW",
        "areaHectares": 37.6,
        "soilType": "Franco Limosa",
        "currentMoisture10cm": 28.5,
        "currentMoisture30cm": 32.1,
        "currentMoisture60cm": 35.8,
        "canopyTemperature": 24.3,
        "recommendedRateMm": 3.5
    },
    "zone-2-ne": {
        "id": "zone-2-ne",
        "fieldId": "field-001",
        "name": "Zona 2 (Noreste)",
        "sector": "NE",
        "areaHectares": 37.6,
        "soilType": "Franco Limosa",
        "currentMoisture10cm": 26.9,
        "currentMoisture30cm": 29.5,
        "currentMoisture60cm": 33.2,
        "canopyTemperature": 23.1,
        "recommendedRateMm": 5.2
    }
}


@router.get("/")
async def list_fields():
    """Get list of agricultural fields"""
    return {
        "fields": list(MOCK_FIELDS.values()),
        "total": len(MOCK_FIELDS)
    }


@router.get("/{field_id}")
async def get_field(field_id: str):
    """Get specific field details"""
    if field_id not in MOCK_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found"
        )
    return MOCK_FIELDS[field_id]


@router.get("/{field_id}/zones")
async def get_field_zones(field_id: str):
    """Get zones for a specific field"""
    if field_id not in MOCK_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found"
        )
    
    field_zones = [z for z in MOCK_ZONES.values() if z["fieldId"] == field_id]
    return {
        "fieldId": field_id,
        "zones": field_zones,
        "total": len(field_zones)
    }


@router.get("/{field_id}/zones/{zone_id}")
async def get_zone(field_id: str, zone_id: str):
    """Get specific zone details"""
    if field_id not in MOCK_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {field_id} not found"
        )
    
    if zone_id not in MOCK_ZONES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found"
        )
    
    zone = MOCK_ZONES[zone_id]
    if zone["fieldId"] != field_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found in field {field_id}"
        )
    
    return zone
