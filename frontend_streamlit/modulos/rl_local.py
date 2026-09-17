"""
Inferencia VRI local cuando FastAPI no está disponible.
Regla basada en humedad 10 cm + temperatura de canopia (proxy de CWSI).
No es el PPO del backend: es un fallback explícito de modo local.
"""
from datetime import datetime, timezone
from uuid import uuid4


def infer_vri_local(zone_id: str, moisture: float, canopy_temp: float) -> dict:
    ambient = 22.0
    cwsi = max(0.0, min(1.0, (canopy_temp - ambient) / 8.0))
    pmp, fc = 25.0, 38.0
    moisture_stress = max(0.0, min(1.0, (fc - moisture) / (fc - pmp)))
    depth = round(2.0 + 6.5 * (0.55 * cwsi + 0.45 * moisture_stress), 2)
    volume = round(depth * 37.6 / 1000, 3)
    confidence = round(0.68 + 0.12 * (1 - abs(0.5 - moisture_stress)), 3)

    return {
        "id": f"local-{uuid4().hex[:8]}",
        "zoneId": zone_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policyId": "LOCAL-CWSI-Rule-v1 (API offline)",
        "recommendedDepthMm": depth,
        "recommendedVolumeM3": volume,
        "confidenceScore": confidence,
        "status": "pending",
        "source": "local",
        "explanation": {
            "dominantFeature": f"CWSI estimado {cwsi:.2f}",
            "shapValues": [
                {"feature": f"Temp. canopia {canopy_temp:.1f} °C", "impact": round(0.4 * cwsi, 2)},
                {"feature": f"Humedad 10 cm {moisture:.1f} %", "impact": round(-0.35 + 0.5 * moisture_stress, 2)},
            ],
            "reasoningText": (
                f"Modo local: CWSI≈{cwsi:.2f}, estrés de humedad≈{moisture_stress:.2f}. "
                f"Dosis sugerida {depth} mm (no es inferencia PPO)."
            ),
            "safeModeTriggered": True,
        },
        "executionWindowHours": {"start": "22:00", "end": "04:00"},
    }
