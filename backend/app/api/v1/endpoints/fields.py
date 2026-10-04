"""Agricultural Fields endpoints"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from uuid import uuid4
from app.services.dataset_service import get_dataset_service

router = APIRouter()

# Mock data for fields
MOCK_FIELDS = {
    "field-001": {
        "id": "field-001",
        "name": "Campo San Pablo Sector A",
        "cropName": "Tomate / Calabacín / Arándano",
        "cropVariety": "Multi-Crop",
        "cropStage": "Flowering",
        "areaHectares": 150.5,
        "soilType": "Franco Limosa",
        "location": {"latitude": -9.1795, "longitude": -75.2268},
        "irrigationMethod": "Central Pivot",
        "createdAt": "2024-01-15T10:00:00Z"
    }
}

import os
import csv
from datetime import datetime

def get_dynamic_zones():
    dataset_service = get_dataset_service()
    zones = {}
    
    zone_info = {
        "zone-1-nw": {"name": "Zona 1 (Tomate)", "sector": "NW", "area": 37.6},
        "zone-2-ne": {"name": "Zona 2 (Tomate)", "sector": "NE", "area": 37.6},
        "zone-4": {"name": "Zona 4 (Calabacín)", "sector": "SW", "area": 37.6},
        "zone-5": {"name": "Zona 5 (Arándano)", "sector": "SE", "area": 37.6},
    }
    
    # Read crop calendar
    calendar_path = os.path.join(dataset_service.data_dir.parent, "crop_calendar.csv")
    crop_data = {}
    if os.path.exists(calendar_path):
        with open(calendar_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                crop_data[row["zona"]] = row
                
    today = datetime.utcnow().date()
    
    for zone_id, info in zone_info.items():
        reading = dataset_service.get_latest_reading(zone_id)
        if not reading:
            continue
            
        # Calculate dynamic phenological stage and Kc
        crop_stage = "Desconocida"
        kc = 0.8
        crop_name = "Desconocido"
        
        if zone_id in crop_data:
            cdata = crop_data[zone_id]
            crop_name = cdata["cultivo"]
            try:
                planting_date_str = cdata["fecha_siembra"]
                flowering_date_str = cdata["fecha_floracion_esperada"]
                harvest_date_str = cdata["fecha_cosecha"]
                
                f_siembra = datetime.strptime(planting_date_str, "%Y-%m-%d").date()
                f_floracion = datetime.strptime(flowering_date_str, "%Y-%m-%d").date()
                f_cosecha = datetime.strptime(harvest_date_str, "%Y-%m-%d").date()
                
                if today < f_siembra:
                    crop_stage = "Pre-siembra"
                    kc = 0.3
                elif today < f_floracion:
                    crop_stage = "Desarrollo Vegetativo"
                    days_total = (f_floracion - f_siembra).days
                    days_passed = (today - f_siembra).days
                    kc = 0.4 + (0.75 * (days_passed / max(1, days_total)))
                elif today <= f_cosecha:
                    crop_stage = "Floracion / Fructificacion"
                    kc = 1.15
                else:
                    crop_stage = "Cosecha / Post-cosecha"
                    kc = 0.6
            except ValueError:
                pass
            
        zones[zone_id] = {
            "id": zone_id,
            "fieldId": "field-001",
            "name": info["name"],
            "sector": info["sector"],
            "areaHectares": info["area"],
            "soilType": "Franco Limosa",
            "cropName": crop_name,
            "cropStage": crop_stage,
            "kc": round(kc, 2),
            "plantingDate": planting_date_str if 'planting_date_str' in locals() else None,
            "floweringDate": flowering_date_str if 'flowering_date_str' in locals() else None,
            "harvestDate": harvest_date_str if 'harvest_date_str' in locals() else None,
            "currentMoisture10cm": round(reading.get('soil_moisture', 0.0), 2),
            "currentMoisture30cm": round(reading.get('soil_moisture', 0.0) + 2.1, 2),
            "currentMoisture60cm": round(reading.get('soil_moisture', 0.0) + 3.5, 2),
            "canopyTemperature": round(reading.get('weather_temp', 0.0), 2),
            "recommendedRateMm": round(reading.get('water_vol_to_24h', 0.0) / 1000, 2) if 'water_vol_to_24h' in reading else 0.0
        }
        
    return zones

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
    
    zones = get_dynamic_zones()
    field_zones = [z for z in zones.values() if z["fieldId"] == field_id]
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
    
    zones = get_dynamic_zones()
    if zone_id not in zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found"
        )
    
    zone = zones[zone_id]
    if zone["fieldId"] != field_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found in field {field_id}"
        )
    
    return zone
