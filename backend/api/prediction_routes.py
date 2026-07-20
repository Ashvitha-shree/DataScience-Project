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
from dl_module.lstm_model import predict_next_speed, build_sequences, TF_AVAILABLE
import pandas as pd
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


@router.get("/lstm-forecast")
def get_lstm_forecast(
    road_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uses the LSTM model to predict traffic speed ~30 minutes ahead
    for a given road, based on its 6 most recent sensor readings."""

    if not TF_AVAILABLE:
        raise HTTPException(503, "TensorFlow not installed. Run: pip install tensorflow")

    # Fetch the 6 most recent records for this road
    records = (
        db.query(TrafficData)
        .filter(TrafficData.road_id == road_id)
        .order_by(TrafficData.traffic_id.desc())
        .limit(6)
        .all()
    )

    if len(records) < 6:
        raise HTTPException(400,
            f"Not enough data. Need 6 records for road {road_id}, found {len(records)}. "
            "Please upload more traffic data for this road first.")

    # Build the input sequence [avg_speed, vehicle_count] for last 6 readings
    # Reverse so oldest is first (chronological order)
    recent = list(reversed(records))
    sequence = [[float(r.avg_speed), float(r.vehicle_count)] for r in recent]

    try:
        predicted_speed = predict_next_speed(sequence)
    except FileNotFoundError:
        raise HTTPException(503,
            "LSTM model not trained yet. Run: python -m dl_module.lstm_model")

    # Determine what the forecast means
    current_speed = float(recent[-1].avg_speed)
    change = predicted_speed - current_speed

    if change < -5:
        trend = "worsening"
        advice = "Congestion expected to increase. Consider alternate routes."
    elif change > 5:
        trend = "improving"
        advice = "Traffic expected to ease in 30 minutes."
    else:
        trend = "stable"
        advice = "Traffic conditions expected to remain similar."

    return {
        "road_id": road_id,
        "current_speed_kmph": round(current_speed, 1),
        "predicted_speed_30min_kmph": round(predicted_speed, 1),
        "trend": trend,
        "advice": advice,
        "based_on_last_n_readings": len(sequence),
    }
