"""
road_routes.py
Endpoints: GET/POST /roads, PUT/DELETE /roads/{id}
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import Road, User
from database.schemas import RoadCreate, RoadUpdate, RoadOut
from auth.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[RoadOut])
def list_roads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Road).all()


@router.get("/{road_id}", response_model=RoadOut)
def get_road(road_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    road = db.query(Road).filter(Road.road_id == road_id).first()
    if not road:
        raise HTTPException(404, "Road not found")
    return road


@router.post("/", response_model=RoadOut, status_code=201)
def create_road(payload: RoadCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    road = Road(**payload.dict())
    db.add(road)
    db.commit()
    db.refresh(road)
    return road


@router.put("/{road_id}", response_model=RoadOut)
def update_road(road_id: int, payload: RoadUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    road = db.query(Road).filter(Road.road_id == road_id).first()
    if not road:
        raise HTTPException(404, "Road not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(road, field, value)
    db.commit()
    db.refresh(road)
    return road


@router.delete("/{road_id}", status_code=204)
def delete_road(road_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    road = db.query(Road).filter(Road.road_id == road_id).first()
    if not road:
        raise HTTPException(404, "Road not found")
    db.delete(road)
    db.commit()
    return None
