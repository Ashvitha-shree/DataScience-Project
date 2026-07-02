"""
alert_routes.py
Endpoints: GET /alerts, POST /generate-alert, GET/POST /alerts/scenario (GenAI)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import Alert, Incident, User
from database.schemas import AlertGenerateRequest, AlertOut, ScenarioRequest, ScenarioOut
from auth.deps import get_current_user
from slm_module.alert_generator import generate_alert
from genai_module.scenario_generator import generate_scenario, SCENARIO_TYPES

router = APIRouter()


@router.get("/", response_model=List[AlertOut])
def list_alerts(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Alert).order_by(Alert.alert_id.desc()).limit(limit).all()


@router.post("/generate", response_model=AlertOut, status_code=201)
def generate_alert_for_incident(payload: AlertGenerateRequest, db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.incident_id == payload.incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")

    road_name = incident.road.road_name if incident.road else None
    alert_text = generate_alert(
        road_name=road_name, incident_type=incident.incident_type,
        severity=incident.severity,
    )

    alert = Alert(incident_id=incident.incident_id, road_id=incident.road_id, alert_text=alert_text)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/scenario", response_model=ScenarioOut)
def get_scenario(scenario_type: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if scenario_type and scenario_type not in SCENARIO_TYPES:
        raise HTTPException(400, f"scenario_type must be one of {SCENARIO_TYPES}")
    return generate_scenario(scenario_type)


@router.get("/scenario/types")
def list_scenario_types(current_user: User = Depends(get_current_user)):
    return {"scenario_types": SCENARIO_TYPES}
