"""
agent_routes.py
Endpoints: GET /agent (recent decisions), POST /agent/run (trigger a cycle)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import AgentLog, TrafficData, Incident, Road, Prediction, Alert, User
from database.schemas import AgentLogOut
from auth.deps import get_current_user
from agent_module.traffic_agent import run_agent_cycle

router = APIRouter()


@router.get("/", response_model=List[AgentLogOut])
def list_agent_logs(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AgentLog).order_by(AgentLog.log_id.desc()).limit(limit).all()


@router.post("/run", response_model=AgentLogOut, status_code=201)
def run_agent(road_id: int, traffic_id: Optional[int] = None, incident_id: Optional[int] = None,
              db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Runs one perceive -> reason -> act -> log cycle for a given road,
    optionally tied to a specific traffic reading and/or incident."""
    road = db.query(Road).filter(Road.road_id == road_id).first()
    if not road:
        raise HTTPException(404, "Road not found")

    congestion_level = None
    prediction_id = None
    if traffic_id:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.traffic_id == traffic_id)
            .order_by(Prediction.prediction_id.desc())
            .first()
        )
        if latest_pred:
            congestion_level = latest_pred.predicted_level
            prediction_id = latest_pred.prediction_id

    incident_dict = None
    if incident_id:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if incident:
            incident_dict = {"incident_type": incident.incident_type, "severity": incident.severity}

    result = run_agent_cycle(road_name=road.road_name, congestion_level=congestion_level, incident=incident_dict)

    # Save the generated alert (if any)
    if result["alert_text"]:
        db.add(Alert(incident_id=incident_id, road_id=road_id, alert_text=result["alert_text"]))

    log = AgentLog(
        road_id=road_id, prediction_id=prediction_id, incident_id=incident_id,
        decision=result["decision"], reason=result["reason"], urgency=result["urgency"],
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
