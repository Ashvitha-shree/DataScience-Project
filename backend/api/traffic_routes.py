"""
traffic_routes.py
Endpoints: GET/POST /traffic, PUT/DELETE /traffic/{id},
           POST /traffic/upload-csv, GET /traffic/download-csv
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from database.db_connection import get_db
from database.models import TrafficData, User
from database.schemas import TrafficDataCreate, TrafficDataUpdate, TrafficDataOut
from auth.deps import get_current_user
from utils.csv_utils import parse_traffic_csv, export_traffic_to_csv

router = APIRouter()


@router.get("/", response_model=List[TrafficDataOut])
def list_traffic(road_id: Optional[int] = None, limit: int = 100,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(TrafficData)
    if road_id:
        query = query.filter(TrafficData.road_id == road_id)
    return query.order_by(TrafficData.traffic_id.desc()).limit(limit).all()


@router.get("/{traffic_id}", response_model=TrafficDataOut)
def get_traffic(traffic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(TrafficData).filter(TrafficData.traffic_id == traffic_id).first()
    if not record:
        raise HTTPException(404, "Traffic record not found")
    return record


@router.post("/", response_model=TrafficDataOut, status_code=201)
def create_traffic(payload: TrafficDataCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    record = TrafficData(**payload.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{traffic_id}", response_model=TrafficDataOut)
def update_traffic(traffic_id: int, payload: TrafficDataUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    record = db.query(TrafficData).filter(TrafficData.traffic_id == traffic_id).first()
    if not record:
        raise HTTPException(404, "Traffic record not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{traffic_id}", status_code=204)
def delete_traffic(traffic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(TrafficData).filter(TrafficData.traffic_id == traffic_id).first()
    if not record:
        raise HTTPException(404, "Traffic record not found")
    db.delete(record)
    db.commit()
    return None


@router.post("/upload-csv")
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    content = file.file.read()
    rows, errors = parse_traffic_csv(content)

    inserted = 0
    for row in rows:
        db.add(TrafficData(**row))
        inserted += 1
    db.commit()

    return {"inserted": inserted, "errors": errors}


@router.get("/export/download-csv")
def download_csv(road_id: Optional[int] = None, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    query = db.query(TrafficData)
    if road_id:
        query = query.filter(TrafficData.road_id == road_id)
    records = query.all()
    rows = [{
        "traffic_id": r.traffic_id, "road_id": r.road_id, "vehicle_count": r.vehicle_count,
        "avg_speed": r.avg_speed, "weather": r.weather, "record_date": r.record_date,
        "record_time": r.record_time, "day_of_week": r.day_of_week,
        "congestion_level": r.congestion_level,
    } for r in records]
    csv_text = export_traffic_to_csv(rows)
    return StreamingResponse(
        io.StringIO(csv_text), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic_data_export.csv"},
    )
