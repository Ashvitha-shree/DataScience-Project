# Sequence Diagram — Full Incident-to-Decision Flow

```mermaid
sequenceDiagram
    actor Officer as Traffic Officer
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant NLP as nlp_module
    participant DB as MySQL Database
    participant ML as ml_module
    participant SLM as slm_module
    participant Agent as agent_module

    Officer->>FE: Enter incident text "Accident near Anna Salai..."
    FE->>API: POST /incidents { raw_text }
    API->>NLP: analyze_incident(raw_text)
    NLP-->>API: { road, type, severity, weather }
    API->>DB: INSERT INTO Incidents (...)
    DB-->>API: incident_id
    API-->>FE: 201 Created { incident }
    FE-->>Officer: Show extracted incident in table

    Officer->>FE: Click "Predict" on latest traffic record
    FE->>API: GET /prediction?traffic_id=...
    API->>DB: SELECT traffic record
    DB-->>API: vehicle_count, avg_speed, weather...
    API->>ML: predict_congestion(...)
    ML-->>API: predicted_level, confidence
    API->>DB: INSERT INTO Predictions (...)
    API-->>FE: 200 OK { prediction }
    FE-->>Officer: Show predicted congestion level

    Officer->>FE: Click "Run Agent Cycle" for the road
    FE->>API: POST /agent/run?road_id=...&incident_id=...
    API->>DB: Fetch road, latest prediction, incident
    API->>Agent: run_agent_cycle(road, congestion, incident)
    Agent->>SLM: generate_alert(road, type, severity)
    SLM-->>Agent: alert_text
    Agent-->>API: { decision, reason, urgency, alert_text }
    API->>DB: INSERT INTO Alerts (...)
    API->>DB: INSERT INTO AgentLogs (...)
    API-->>FE: 201 Created { agent_log }
    FE-->>Officer: Show new alert + agent decision on dashboard
```

**Explanation:** This trace shows the most representative end-to-end flow in the system: an
officer submits an incident, the NLP module structures it, the ML module predicts congestion
for the same road, and finally the Agentic AI module ties both together — generating an alert
via the SLM module and logging a signal-timing recommendation — all visible back on the
dashboard in real time.
