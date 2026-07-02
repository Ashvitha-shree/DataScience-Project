"""
models.py
SQLAlchemy ORM models mirroring database/schema.sql exactly. Using ORM
models (instead of raw SQL everywhere) keeps the API code clean and
makes relationships between tables explicit and easy to explain in a viva.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, Time, DateTime,
    Enum, ForeignKey, DECIMAL, func
)
from sqlalchemy.orm import relationship

from database.db_connection import Base


class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "officer", name="role_enum"), default="officer")
    created_at = Column(DateTime, server_default=func.now())


class Road(Base):
    __tablename__ = "Roads"

    road_id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String(150), unique=True, nullable=False)
    location = Column(String(150))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    road_type = Column(Enum("highway", "arterial", "residential", "collector", name="road_type_enum"),
                        default="arterial")
    signal_id = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    traffic_records = relationship("TrafficData", back_populates="road", cascade="all, delete")
    incidents = relationship("Incident", back_populates="road")


class TrafficData(Base):
    __tablename__ = "TrafficData"

    traffic_id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("Roads.road_id", ondelete="CASCADE"), nullable=False)
    vehicle_count = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=False)
    weather = Column(String(50), default="clear")
    record_date = Column(Date, nullable=False)
    record_time = Column(Time, nullable=False)
    day_of_week = Column(String(15))
    congestion_level = Column(Enum("low", "medium", "high", name="congestion_enum"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    road = relationship("Road", back_populates="traffic_records")
    predictions = relationship("Prediction", back_populates="traffic", cascade="all, delete")


class Prediction(Base):
    __tablename__ = "Predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    traffic_id = Column(Integer, ForeignKey("TrafficData.traffic_id", ondelete="CASCADE"), nullable=False)
    model_used = Column(Enum("random_forest", "lstm", name="model_enum"), nullable=False)
    predicted_level = Column(String(20))
    predicted_speed = Column(Float, nullable=True)
    confidence = Column(Float)
    predicted_at = Column(DateTime, server_default=func.now())

    traffic = relationship("TrafficData", back_populates="predictions")


class Incident(Base):
    __tablename__ = "Incidents"

    incident_id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("Roads.road_id", ondelete="SET NULL"), nullable=True)
    raw_text = Column(Text, nullable=False)
    incident_type = Column(String(50))
    severity = Column(String(20))
    weather = Column(String(50))
    reported_by = Column(String(100))
    reported_at = Column(DateTime, server_default=func.now())

    road = relationship("Road", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")


class Alert(Base):
    __tablename__ = "Alerts"

    alert_id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("Incidents.incident_id", ondelete="SET NULL"), nullable=True)
    road_id = Column(Integer, ForeignKey("Roads.road_id", ondelete="SET NULL"), nullable=True)
    alert_text = Column(Text, nullable=False)
    generated_at = Column(DateTime, server_default=func.now())

    incident = relationship("Incident", back_populates="alerts")


class AgentLog(Base):
    __tablename__ = "AgentLogs"

    log_id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("Roads.road_id", ondelete="SET NULL"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("Predictions.prediction_id", ondelete="SET NULL"), nullable=True)
    incident_id = Column(Integer, ForeignKey("Incidents.incident_id", ondelete="SET NULL"), nullable=True)
    decision = Column(String(255), nullable=False)
    reason = Column(String(255))
    urgency = Column(Enum("low", "medium", "high", "critical", name="urgency_enum"), default="low")
    created_at = Column(DateTime, server_default=func.now())


class Report(Base):
    __tablename__ = "Reports"

    report_id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum("daily", "weekly", "monthly", name="report_type_enum"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    file_path = Column(String(255))
    generated_by = Column(Integer, ForeignKey("Users.user_id", ondelete="SET NULL"), nullable=True)
    generated_at = Column(DateTime, server_default=func.now())
