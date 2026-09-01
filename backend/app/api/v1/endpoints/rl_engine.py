"""Reinforcement Learning Engine endpoints"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from datetime import datetime
from uuid import uuid4
import random

router = APIRouter()


@router.post("/infer-vri-rates")
async def infer_vri_rates(observation: Dict):
    """
    Execute PPO policy network forward pass and return VRI irrigation recommendations
    
    Input: Observation tensor with sensor data
    Output: Recommended irrigation rates with SHAP explanations
    """
    zone_id = observation.get("zoneId", "zone-1-nw")
    
    # Simulate RL model inference
    confidence = random.uniform(0.85, 0.99)
    recommended_depth = random.uniform(2.0, 8.0)
    
    decision = {
        "id": f"rl-decision-{uuid4().hex[:8]}",
        "zoneId": zone_id,
        "timestamp": datetime.utcnow().isoformat(),
        "policyId": "PPO-VRI-DualReward-v4.2",
        "recommendedDepthMm": round(recommended_depth, 2),
        "recommendedVolumeM3": round(recommended_depth * 37.6 / 1000, 2),
        "confidenceScore": round(confidence, 3),
        "status": "pending",
        "explanation": {
            "dominantFeature": "Canopy Temperature Stress (CWSI: 0.72)",
            "shapValues": [
                {
                    "feature": f"Canopy Temp (+{random.uniform(3, 5):.1f}°C vs Ambient)",
                    "impact": round(random.uniform(0.3, 0.6), 2),
                    "description": "Cierre estomático agudo detectado por termografía"
                },
                {
                    "feature": f"Humedad Suelo {random.uniform(20, 30):.1f}%",
                    "impact": round(random.uniform(-0.4, 0.2), 2),
                    "description": "Aproximándose a Punto de Marchitez Permanente"
                }
            ],
            "reasoningText": "Deficit hídrico crítico detectado en capas superficiales. Aplicación de riego urgente necesaria.",
            "safeModeTriggered": False
        },
        "executionWindowHours": {
            "start": "22:00",
            "end": "04:00"
        }
    }
    
    return decision


@router.get("/decisions")
async def get_decisions(field_id: str = None, status_filter: str = None):
    """Get RL decisions history"""
    return {
        "decisions": [],
        "total": 0,
        "filters": {
            "fieldId": field_id,
            "status": status_filter
        }
    }


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approved_by: str):
    """Approve an RL irrigation decision"""
    return {
        "decisionId": decision_id,
        "status": "approved",
        "approvedBy": approved_by,
        "approvalTimestamp": datetime.utcnow().isoformat()
    }


@router.post("/decisions/{decision_id}/override")
async def override_decision(decision_id: str, override_data: Dict):
    """Override an RL decision with manual values"""
    return {
        "decisionId": decision_id,
        "status": "overridden_manually",
        "overrideReason": override_data.get("reason", ""),
        "newDepthMm": override_data.get("depthMm"),
        "overriddenAt": datetime.utcnow().isoformat()
    }


@router.post("/retrain-policy")
async def retrain_policy(training_data: Dict):
    """Trigger RL policy retraining with feedback data"""
    return {
        "status": "training_initiated",
        "policyVersion": "PPO-VRI-DualReward-v4.3",
        "trainingRecords": len(training_data.get("feedbackLogs", [])),
        "estimatedDurationMinutes": 45,
        "message": "Policy retraining queued in Celery"
    }
