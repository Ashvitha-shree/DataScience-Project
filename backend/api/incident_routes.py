"""
incident_routes.py
Endpoints: GET /incidents, POST /incident
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import Incident, Road, User
from database.schemas import IncidentCreate, IncidentOut
from auth.deps import get_current_user
from nlp_module.incident_extractor import analyze_incident

router = APIRouter()


@router.get("/", response_model=List[IncidentOut])
def list_incidents(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Incident).order_by(Incident.incident_id.desc()).limit(limit).all()


@router.post("/", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    extracted = analyze_incident(payload.raw_text)

    road_id = payload.road_id
    if road_id is None and extracted["road_name"]:
        road = db.query(Road).filter(Road.road_name == extracted["road_name"]).first()
        road_id = road.road_id if road else None

    incident = Incident(
        road_id=road_id,
        raw_text=payload.raw_text,
        incident_type=extracted["incident_type"],
        severity=extracted["severity"],
        weather=extracted["weather"],
        reported_by=payload.reported_by,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
