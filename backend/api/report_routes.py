"""
report_routes.py
Endpoints: GET /reports?type=daily|weekly|monthly  (generates + downloads a PDF)
"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.db_connection import get_db
from database.models import TrafficData, Incident, Alert, AgentLog, Report, Road, User
from auth.deps import get_current_user
from utils.pdf_utils import generate_pdf_report

router = APIRouter()

PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


@router.get("/")
def get_report(report_type: str = "daily", db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    if report_type not in PERIOD_DAYS:
        raise HTTPException(400, "report_type must be daily, weekly, or monthly")

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=PERIOD_DAYS[report_type])

    traffic_records = (
        db.query(TrafficData)
        .filter(TrafficData.record_date >= start_date, TrafficData.record_date <= end_date)
        .all()
    )
    incidents = (
        db.query(Incident)
        .filter(Incident.reported_at >= start_date)
        .all()
    )
    alerts = db.query(Alert).filter(Alert.generated_at >= start_date).all()
    agent_logs = db.query(AgentLog).filter(AgentLog.created_at >= start_date).all()

    avg_speed = round(sum(r.avg_speed for r in traffic_records) / len(traffic_records), 2) if traffic_records else 0
    high_congestion_count = sum(1 for r in traffic_records if r.congestion_level == "high")

    traffic_summary = {
        "Total Traffic Records": len(traffic_records),
        "Average Speed (km/h)": avg_speed,
        "High Congestion Records": high_congestion_count,
        "Total Incidents": len(incidents),
        "Total Alerts Generated": len(alerts),
        "Total Agent Decisions": len(agent_logs),
    }

    incidents_data = [{
        "road_name": i.road.road_name if i.road else "-",
        "incident_type": i.incident_type, "severity": i.severity, "reported_at": i.reported_at,
    } for i in incidents]
    alerts_data = [{"alert_text": a.alert_text} for a in alerts]
    logs_data = [{"decision": l.decision, "reason": l.reason, "urgency": l.urgency} for l in agent_logs]

    filepath = generate_pdf_report(
        report_type, start_date, end_date, traffic_summary,
        incidents_data, alerts_data, logs_data,
    )

    report = Report(
        report_type=report_type, start_date=start_date, end_date=end_date,
        file_path=filepath, generated_by=current_user.user_id,
    )
    db.add(report)
    db.commit()

    return FileResponse(filepath, media_type="application/pdf", filename=f"{report_type}_report.pdf")
