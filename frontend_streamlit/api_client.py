"""
Cliente HTTP para la API FastAPI.
Mapea IDs locales (zone-nw) a IDs del backend (zone-1-nw).
Expone last_error / is_online para el banner de modo local.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("API_TIMEOUT", "4"))

ZONE_TO_API = {
    "zone-nw": "zone-1-nw",
    "zone-ne": "zone-2-ne",
    "zone-sw": "zone-3-sw",
    "zone-se": "zone-4-se",
}

_last_error: str | None = None
_online: bool | None = None


def last_error() -> str | None:
    return _last_error


def is_online() -> bool:
    global _online
    if _online is None:
        get_health()
    return bool(_online)


def to_api_zone(zone_id: str) -> str:
    return ZONE_TO_API.get(zone_id, zone_id)


def _fail(exc: Exception):
    global _last_error, _online
    _last_error = str(exc)
    _online = False
    return None


def _ok(payload):
    global _last_error, _online
    _last_error = None
    _online = True
    return payload


def _get(endpoint: str, params: dict = None) -> dict | None:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return _ok(response.json())
    except Exception as e:
        return _fail(e)


def _post(endpoint: str, payload: dict) -> dict | None:
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return _ok(response.json())
    except Exception as e:
        return _fail(e)


def get_health() -> dict | None:
    return _get("/health")


def get_fields() -> dict | None:
    return _get("/api/v1/fields/")


def get_field(field_id: str) -> dict | None:
    return _get(f"/api/v1/fields/{field_id}")


def get_field_zones(field_id: str) -> dict | None:
    return _get(f"/api/v1/fields/{field_id}/zones")


def get_sensors() -> dict | None:
    return _get("/api/v1/sensors/")


def get_zone_sensors(zone_id: str) -> dict | None:
    return _get(f"/api/v1/sensors/zone/{to_api_zone(zone_id)}")


def ingest_telemetry(readings: list) -> dict | None:
    return _post("/api/v1/sensors/telemetry/ingest", {"readings": readings})


def infer_vri_rates(zone_id: str, moisture: float, canopy_temp: float) -> dict | None:
    payload = {
        "zoneId": to_api_zone(zone_id),
        "soilMoisture10cm": moisture,
        "canopyTemperature": canopy_temp,
    }
    return _post("/api/v1/rl-engine/infer-vri-rates", payload)


def approve_decision(decision_id: str, approved_by: str) -> dict | None:
    return _post(
        f"/api/v1/rl-engine/decisions/{decision_id}/approve",
        {"approved_by": approved_by},
    )


def override_decision(decision_id: str, depth_mm: float, reason: str) -> dict | None:
    return _post(
        f"/api/v1/rl-engine/decisions/{decision_id}/override",
        {"depthMm": depth_mm, "reason": reason},
    )


def get_irrigation_status(field_id: str = "field-001") -> dict | None:
    return _get("/api/v1/irrigation/status", params={"field_id": field_id})


def get_irrigation_schedule(field_id: str = "field-001") -> dict | None:
    return _get("/api/v1/irrigation/schedule", params={"field_id": field_id})


def execute_irrigation(decision_id: str, zone_id: str, depth_mm: float) -> dict | None:
    payload = {
        "decisionId": decision_id,
        "zoneId": to_api_zone(zone_id) if zone_id else zone_id,
        "depthMm": depth_mm,
    }
    return _post("/api/v1/irrigation/execute-decision", payload)


def manual_trigger(zone_id: str, depth_mm: float, triggered_by: str = "Operador") -> dict | None:
    payload = {
        "zoneId": to_api_zone(zone_id),
        "depthMm": depth_mm,
        "triggeredBy": triggered_by,
    }
    return _post("/api/v1/irrigation/manual-trigger", payload)


def emergency_stop(field_id: str = "field-001") -> dict | None:
    return _post("/api/v1/irrigation/emergency-stop", {"field_id": field_id})


def generate_report(title: str, fmt: str, field_id: str) -> dict | None:
    payload = {"title": title, "format": fmt, "fieldId": field_id}
    return _post("/api/v1/reports/generate", payload)


def get_report_history(field_id: str = "field-001") -> dict | None:
    return _get("/api/v1/reports/history", params={"field_id": field_id})
