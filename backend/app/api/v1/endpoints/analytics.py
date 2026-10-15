"""Analytics endpoints backed by the loaded public irrigation dataset."""
from fastapi import APIRouter, HTTPException, Query

from app.services.dataset_service import get_dataset_service

router = APIRouter()


@router.get("")
async def get_analytics(zone: str = Query("zone-1-nw", description="Dataset zone to analyze")):
    """Return the 24 latest available moisture and irrigation-volume readings."""
    dataset_service = get_dataset_service()
    if zone not in dataset_service.zone_mapping:
        raise HTTPException(status_code=404, detail=f"Unknown dataset zone: {zone}")

    if not dataset_service._initialized:
        dataset_service.initialize()
    dataframe = dataset_service.datasets.get(zone)
    if dataframe is None or dataframe.empty:
        raise HTTPException(status_code=503, detail=f"No telemetry dataset is available for {zone}")

    required_columns = {"ts", "soil_moisture", "water_vol_past_4h"}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise HTTPException(
            status_code=503,
            detail=f"Dataset for {zone} is missing columns: {', '.join(sorted(missing_columns))}",
        )

    recent = dataframe.tail(24)
    timestamps = recent["ts"].astype(str).tolist()
    return {
        "zona": zone,
        "fecha_hora": timestamps,
        "humedad": recent["soil_moisture"].astype(float).round(2).tolist(),
        # The dataset field is a rolling four-hour water volume, not a flow rate.
        "volumen_agua_4h": recent["water_vol_past_4h"].astype(float).round(2).tolist(),
    }
