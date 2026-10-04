"""
Crop Calendar API Endpoints with LangChain Agent Integration
Provides phenological stage calculation based on planting dates
Enhanced with AI-powered reasoning and recommendations
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import os
from pydantic import BaseModel

from app.services.phenology_agent_service import get_phenology_agent

router = APIRouter()

# Data models
class CropCalendarEntry(BaseModel):
    zona: str
    cultivo: str
    fecha_siembra: str
    fecha_floracion_esperada: str
    fecha_cosecha: str
    
class PhenologicalStage(BaseModel):
    zone_id: str
    crop_name: str
    current_stage: str
    stage_name: str
    days_since_planting: int
    days_to_flowering: int
    days_to_harvest: int
    kc: float
    planting_date: str
    flowering_date: str
    harvest_date: str
    progress_pct: float

# Kc values by phenological stage (FAO-56 standards)
KC_VALUES = {
    "Tomate": {
        "initial": 0.60,      # 0-20 days
        "vegetative": 0.90,   # 21-45 days
        "flowering": 1.15,    # 46-75 days
        "yield_formation": 1.20,  # 76-100 days
        "ripening": 0.80      # 101+ days
    },
    "Calabacin": {
        "initial": 0.50,
        "vegetative": 0.80,
        "flowering": 0.95,
        "yield_formation": 0.90,
        "ripening": 0.75
    },
    "Arandano": {
        "initial": 0.50,
        "vegetative": 0.65,
        "flowering": 0.95,
        "yield_formation": 1.05,
        "ripening": 0.85
    }
}

def load_crop_calendar() -> List[CropCalendarEntry]:
    """Load crop calendar from CSV"""
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', '..', 'data', 'crop_calendar.csv'
    )
    
    entries = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(CropCalendarEntry(**row))
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Crop calendar file not found: {csv_path}")
    
    return entries

def calculate_stage_from_dates(
    planting_date: str, 
    flowering_date: str, 
    harvest_date: str,
    today: datetime
) -> tuple[str, str, int]:
    """
    Calculate phenological stage based on dates
    Returns: (stage_id, stage_name, days_since_planting)
    """
    planting = datetime.fromisoformat(planting_date)
    flowering = datetime.fromisoformat(flowering_date)
    harvest = datetime.fromisoformat(harvest_date)
    
    days_since_planting = (today - planting).days
    days_to_flowering = (flowering - planting).days
    days_to_harvest = (harvest - planting).days
    
    # Calculate stage based on progress
    if days_since_planting < 0:
        return "initial", "Pre-Siembra", days_since_planting
    
    progress_pct = (days_since_planting / days_to_harvest) * 100
    
    if progress_pct < 20:
        return "initial", "Inicial", days_since_planting
    elif progress_pct < 40:
        return "vegetative", "Vegetativo", days_since_planting
    elif progress_pct < 65:
        return "flowering", "Floración", days_since_planting
    elif progress_pct < 85:
        return "yield_formation", "Formación", days_since_planting
    else:
        return "ripening", "Maduración", days_since_planting

def get_kc_for_stage(crop_name: str, stage: str) -> float:
    """Get Kc value for crop and stage"""
    crop_kc = KC_VALUES.get(crop_name, KC_VALUES["Tomate"])
    return crop_kc.get(stage, 1.0)

@router.get("/calendar", response_model=List[PhenologicalStage])
async def get_crop_calendar(zone_id: Optional[str] = None):
    """
    Get current phenological stage for all zones or specific zone
    """
    entries = load_crop_calendar()
    today = datetime.now()
    
    results = []
    for entry in entries:
        # Skip if zone filter specified and doesn't match
        if zone_id and entry.zona != zone_id:
            continue
        
        stage_id, stage_name, days_since = calculate_stage_from_dates(
            entry.fecha_siembra,
            entry.fecha_floracion_esperada,
            entry.fecha_cosecha,
            today
        )
        
        planting = datetime.fromisoformat(entry.fecha_siembra)
        flowering = datetime.fromisoformat(entry.fecha_floracion_esperada)
        harvest = datetime.fromisoformat(entry.fecha_cosecha)
        
        days_to_flowering = max(0, (flowering - today).days)
        days_to_harvest = max(0, (harvest - today).days)
        days_total = (harvest - planting).days
        progress_pct = min(100, max(0, (days_since / days_total) * 100))
        
        kc = get_kc_for_stage(entry.cultivo, stage_id)
        
        results.append(PhenologicalStage(
            zone_id=entry.zona,
            crop_name=entry.cultivo,
            current_stage=stage_id,
            stage_name=stage_name,
            days_since_planting=days_since,
            days_to_flowering=days_to_flowering,
            days_to_harvest=days_to_harvest,
            kc=kc,
            planting_date=entry.fecha_siembra,
            flowering_date=entry.fecha_floracion_esperada,
            harvest_date=entry.fecha_cosecha,
            progress_pct=round(progress_pct, 1)
        ))
    
    return results

@router.get("/calendar/{zone_id}", response_model=PhenologicalStage)
async def get_zone_phenology(zone_id: str):
    """
    Get phenological stage for a specific zone
    """
    results = await get_crop_calendar(zone_id=zone_id)
    
    if not results:
        raise HTTPException(
            status_code=404, 
            detail=f"No crop calendar found for zone: {zone_id}"
        )
    
    return results[0]

@router.get("/kc/{zone_id}")
async def get_zone_kc(zone_id: str):
    """
    Get current Kc value for a specific zone based on phenological stage
    """
    stage = await get_zone_phenology(zone_id)
    
    return {
        "zone_id": zone_id,
        "kc": stage.kc,
        "stage": stage.current_stage,
        "stage_name": stage.stage_name,
        "crop": stage.crop_name
    }

@router.get("/ai/phenology/{zone_id}")
async def get_ai_phenology_analysis(zone_id: str):
    """
    🤖 AI-Powered Phenology Analysis with LangChain Agent
    
    Uses ReAct agent with multiple tools:
    - Phenology calculation
    - Growing Degree Days (GDD)
    - RAG knowledge retrieval
    - Kc database lookup
    - Water requirement calculation
    
    Returns comprehensive analysis with AI reasoning
    """
    try:
        agent_service = get_phenology_agent()
        result = agent_service.get_phenology_with_reasoning(zone_id)
        return {
            "success": True,
            "data": result,
            "agent_type": "LangChain ReAct Agent",
            "model": "llama-3.3-70b-versatile"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/irrigation-recommendation/{zone_id}")
async def get_ai_irrigation_recommendation(
    zone_id: str,
    current_moisture: float = Query(..., description="Current soil moisture (%)"),
    et0: float = Query(5.5, description="Reference evapotranspiration (mm/day)"),
    rain_forecast: float = Query(0.0, description="Forecasted rain (mm)")
):
    """
    🚀 AI-Generated Irrigation Recommendation
    
    Uses LangChain LLM Chain to generate precise irrigation prescriptions
    considering:
    - Phenological stage and Kc
    - Current soil moisture
    - Atmospheric demand (ET0)
    - Rain forecast
    
    Returns:
    - Recommended irrigation depth (mm)
    - Technical reasoning
    - Confidence score
    - Risk factors
    - Optimization tips
    """
    try:
        agent_service = get_phenology_agent()
        recommendation = agent_service.get_irrigation_recommendation(
            zone_id=zone_id,
            current_moisture=current_moisture,
            et0=et0,
            rain_forecast=rain_forecast
        )
        return {
            "success": True,
            "recommendation": recommendation.dict(),
            "method": "LangChain LLM Chain + FAO-56"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/tools")
async def list_agent_tools():
    """
    List all available tools in the Phenology Agent
    """
    agent_service = get_phenology_agent()
    tools_info = [
        {
            "name": tool.name,
            "description": tool.description
        }
        for tool in agent_service.tools
    ]
    return {
        "total_tools": len(tools_info),
        "tools": tools_info
    }
