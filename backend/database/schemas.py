"""
schemas.py
Pydantic models used for request validation and response shaping in the API.
Kept separate from the SQLAlchemy models (database/models.py) - this is a
standard FastAPI pattern: ORM models talk to the DB, Pydantic "schemas"
talk to the outside world (JSON in/out).
"""
from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "officer"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    user_id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Roads ----------
class RoadCreate(BaseModel):
    road_name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    road_type: str = "arterial"
    signal_id: Optional[str] = None


class RoadUpdate(BaseModel):
    road_name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    road_type: Optional[str] = None
    signal_id: Optional[str] = None


class RoadOut(BaseModel):
    road_id: int
    road_name: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    road_type: str
    signal_id: Optional[str]

    class Config:
        from_attributes = True


# ---------- Traffic Data ----------
class TrafficDataCreate(BaseModel):
    road_id: int
    vehicle_count: int
    avg_speed: float
    weather: str = "clear"
    record_date: date
    record_time: time
    day_of_week: Optional[str] = None
    congestion_level: Optional[str] = None


class TrafficDataUpdate(BaseModel):
    vehicle_count: Optional[int] = None
    avg_speed: Optional[float] = None
    weather: Optional[str] = None
    congestion_level: Optional[str] = None


class TrafficDataOut(BaseModel):
    traffic_id: int
    road_id: int
    vehicle_count: int
    avg_speed: float
    weather: str
    record_date: date
    record_time: time
    day_of_week: Optional[str]
    congestion_level: Optional[str]

    class Config:
        from_attributes = True


# ---------- Predictions ----------
class PredictionRequest(BaseModel):
    traffic_id: int
    model_used: str = "random_forest"  # or "lstm"


class PredictionOut(BaseModel):
    prediction_id: int
    traffic_id: int
    model_used: str
    predicted_level: Optional[str]
    predicted_speed: Optional[float]
    confidence: Optional[float]
    predicted_at: datetime

    class Config:
        from_attributes = True


# ---------- Incidents ----------
class IncidentCreate(BaseModel):
    raw_text: str
    road_id: Optional[int] = None
    reported_by: Optional[str] = "citizen"


class IncidentOut(BaseModel):
    incident_id: int
    road_id: Optional[int]
    raw_text: str
    incident_type: Optional[str]
    severity: Optional[str]
    weather: Optional[str]
    reported_by: Optional[str]
    reported_at: datetime

    class Config:
        from_attributes = True


# ---------- Alerts ----------
class AlertGenerateRequest(BaseModel):
    incident_id: int


class AlertOut(BaseModel):
    alert_id: int
    incident_id: Optional[int]
    road_id: Optional[int]
    alert_text: str
    generated_at: datetime

    class Config:
        from_attributes = True


# ---------- Agent ----------
class AgentLogOut(BaseModel):
    log_id: int
    road_id: Optional[int]
    prediction_id: Optional[int]
    incident_id: Optional[int]
    decision: str
    reason: Optional[str]
    urgency: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgentRunResponse(BaseModel):
    logs_created: List[AgentLogOut]


# ---------- GenAI Scenario ----------
class ScenarioRequest(BaseModel):
    scenario_type: Optional[str] = None


class ScenarioOut(BaseModel):
    scenario_type: str
    description: str
    recommended_actions: List[str]
