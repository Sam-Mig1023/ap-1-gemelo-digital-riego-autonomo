"""Irrigation Control endpoints"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Dict
from uuid import uuid4

router = APIRouter()


@router.post("/execute-decision")
async def execute_irrigation_decision(decision: Dict):
    """
    Execute an approved RL irrigation decision
    Sends PWM commands to VRI hardware controller
    """
    decision_id = decision.get("decisionId")
    zone_id = decision.get("zoneId")
    depth_mm = decision.get("depthMm", 0)
    
    # Simulate hardware command dispatch
    execution_result = {
        "decisionId": decision_id,
        "zoneId": zone_id,
        "status": "executed",
        "executedAt": datetime.utcnow().isoformat(),
        "irrigationDepthMm": depth_mm,
        "volumeDispatchedM3": round(depth_mm * 37.6 / 1000, 2),
        "executionTime": "00:45:30",
        "hardwareStatus": "success",
        "pwmSignal": "active",
        "message": "VRI system executed variable-rate dosing"
    }
    
    return execution_result


@router.post("/manual-trigger")
async def manual_irrigation_trigger(trigger_data: Dict):
    """Manually trigger irrigation on a specific zone"""
    return {
        "triggerId": f"trigger-{uuid4().hex[:8]}",
        "zoneId": trigger_data.get("zoneId"),
        "status": "triggered",
        "depthMm": trigger_data.get("depthMm", 5.0),
        "triggeredAt": datetime.utcnow().isoformat(),
        "triggeredBy": trigger_data.get("triggeredBy", "system"),
        "message": "Manual irrigation trigger sent to hardware controller"
    }


@router.get("/status")
async def get_irrigation_status(field_id: str = None):
    """Get current irrigation system status"""
    return {
        "fieldId": field_id,
        "systemOperational": True,
        "zoneStatuses": [
            {
                "zoneId": "zone-1-nw",
                "status": "idle",
                "lastExecution": "2026-08-31T04:15:00Z",
                "nextScheduled": "2026-09-01T22:00:00Z"
            },
            {
                "zoneId": "zone-2-ne",
                "status": "idle",
                "lastExecution": "2026-08-31T03:45:00Z",
                "nextScheduled": "2026-09-01T23:30:00Z"
            }
        ],
        "hardwareConnected": True,
        "waterPressureBar": 3.2,
        "flowRateLpm": 0.0
    }


@router.post("/emergency-stop")
async def emergency_stop(field_id: str):
    """Activate emergency stop on irrigation system"""
    return {
        "fieldId": field_id,
        "status": "stopped",
        "allValvesClosed": True,
        "stoppedAt": datetime.utcnow().isoformat(),
        "message": "Emergency stop activated - all irrigation valves closed"
    }


@router.get("/schedule")
async def get_irrigation_schedule(field_id: str = None):
    """Get scheduled irrigation tasks"""
    return {
        "fieldId": field_id,
        "schedule": [
            {
                "zoneId": "zone-1-nw",
                "scheduledTime": "2026-09-01T22:00:00Z",
                "estimatedDepthMm": 3.5,
                "status": "scheduled"
            },
            {
                "zoneId": "zone-2-ne",
                "scheduledTime": "2026-09-01T23:30:00Z",
                "estimatedDepthMm": 5.2,
                "status": "scheduled"
            }
        ],
        "nextExecution": "2026-09-01T22:00:00Z"
    }
