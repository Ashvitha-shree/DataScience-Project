"""
prediction_routes.py
Endpoints: GET /prediction?traffic_id=, POST /prediction/train
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import TrafficData, Prediction, Road, User
from database.schemas import PredictionOut
from auth.deps import get_current_user
from ml_module.random_forest_model import predict_congestion, train_random_forest

router = APIRouter()


@router.get("/", response_model=PredictionOut)
def get_prediction(traffic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(TrafficData).filter(TrafficData.traffic_id == traffic_id).first()
    if not record:
        raise HTTPException(404, "Traffic record not found")

    try:
        level, confidence = predict_congestion(
            vehicle_count=record.vehicle_count, avg_speed=record.avg_speed,
            record_time=record.record_time, day_of_week=record.day_of_week,
            weather=record.weather,
        )
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))

    prediction = Prediction(
        traffic_id=traffic_id, model_used="random_forest",
        predicted_level=level, confidence=confidence,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.post("/train")
def train_model(current_user: User = Depends(get_current_user)):
    """Re-trains the Random Forest model on the current dataset CSV and
    returns evaluation metrics. Restricted conceptually to admin use in the
    frontend (Train Model button on the ML dashboard page)."""
    metrics = train_random_forest()
    return metrics
