"""Dataset endpoints for exposing public real-world telemetry"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import Dict, Any
from pathlib import Path
import os
from app.services.dataset_service import get_dataset_service

router = APIRouter()

@router.get("/metadata")
async def get_dataset_metadata():
    """Get metadata about the loaded real-world datasets"""
    dataset_service = get_dataset_service()
    metadata = dataset_service.get_metadata()
    
    return {
        "status": "success",
        "description": "Real-world telemetry dataset from Arnesano, Italy (2025)",
        "license": "CC BY 4.0",
        "total_zones_loaded": metadata["total_zones"],
        "zones": metadata["zones"]
    }

@router.get("/export")
async def export_dataset(zone: str = "zone-1-nw", format: str = "csv"):
    """Export the dataset for a specific zone"""
    if format != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV format is supported currently"
        )
        
    dataset_service = get_dataset_service()
    
    if zone not in dataset_service.zone_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone} not found or no dataset available"
        )
        
    filename = dataset_service.zone_mapping[zone]
    file_path = dataset_service.data_dir / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset file {filename} not found"
        )
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/csv"
    )
