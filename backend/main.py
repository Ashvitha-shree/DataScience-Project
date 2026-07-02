"""
main.py
FastAPI application entrypoint. Wires together all routers, sets up CORS
for the React frontend, and creates database tables on startup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database.db_connection import Base, engine, SessionLocal
from database import models  # noqa: F401  (ensures models are registered with Base)
from utils.security import hash_password

from api import (
    auth_routes, road_routes, traffic_routes, prediction_routes,
    incident_routes, alert_routes, agent_routes, report_routes,
)

app = FastAPI(
    title="Smart City Traffic Management and Optimization System",
    description="Final-year engineering project: ML + DL + NLP + SLM + GenAI + Agentic AI traffic system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(road_routes.router, prefix="/roads", tags=["Roads"])
app.include_router(traffic_routes.router, prefix="/traffic", tags=["Traffic Data"])
app.include_router(prediction_routes.router, prefix="/prediction", tags=["ML Prediction"])
app.include_router(incident_routes.router, prefix="/incidents", tags=["Incidents (NLP)"])
app.include_router(alert_routes.router, prefix="/alerts", tags=["Alerts (SLM) & Scenarios (GenAI)"])
app.include_router(agent_routes.router, prefix="/agent", tags=["Agentic AI"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])


@app.on_event("startup")
def on_startup():
    # Creates all tables if they don't exist yet (in addition to running
    # database/schema.sql manually, this acts as a safety net).
    Base.metadata.create_all(bind=engine)

    # Seed a default admin account if none exists, so the project is
    # immediately usable after first run (email/password printed once).
    db = SessionLocal()
    try:
        existing_admin = db.query(models.User).filter(models.User.role == "admin").first()
        if not existing_admin:
            admin = models.User(
                name="Default Admin",
                email="admin@smarttraffic.local",
                password_hash=hash_password("Admin@123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("Created default admin user -> admin@smarttraffic.local / Admin@123")
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Smart City Traffic Management API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
