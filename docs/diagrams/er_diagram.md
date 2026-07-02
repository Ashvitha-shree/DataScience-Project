# ER Diagram

```mermaid
erDiagram
    USERS ||--o{ REPORTS : generates
    ROADS ||--o{ TRAFFICDATA : has
    ROADS ||--o{ INCIDENTS : occurs_on
    ROADS ||--o{ AGENTLOGS : relates_to
    TRAFFICDATA ||--o{ PREDICTIONS : produces
    INCIDENTS ||--o{ ALERTS : triggers
    PREDICTIONS |o--o{ AGENTLOGS : informs
    INCIDENTS |o--o{ AGENTLOGS : informs

    USERS {
        int user_id PK
        string name
        string email UK
        string password_hash
        enum role
        datetime created_at
    }

    ROADS {
        int road_id PK
        string road_name UK
        string location
        decimal latitude
        decimal longitude
        enum road_type
        string signal_id
    }

    TRAFFICDATA {
        int traffic_id PK
        int road_id FK
        int vehicle_count
        float avg_speed
        string weather
        date record_date
        time record_time
        string day_of_week
        enum congestion_level
    }

    PREDICTIONS {
        int prediction_id PK
        int traffic_id FK
        enum model_used
        string predicted_level
        float predicted_speed
        float confidence
        datetime predicted_at
    }

    INCIDENTS {
        int incident_id PK
        int road_id FK
        text raw_text
        string incident_type
        string severity
        string weather
        string reported_by
        datetime reported_at
    }

    ALERTS {
        int alert_id PK
        int incident_id FK
        int road_id FK
        text alert_text
        datetime generated_at
    }

    AGENTLOGS {
        int log_id PK
        int road_id FK
        int prediction_id FK
        int incident_id FK
        string decision
        string reason
        enum urgency
        datetime created_at
    }

    REPORTS {
        int report_id PK
        enum report_type
        date start_date
        date end_date
        string file_path
        int generated_by FK
    }
```

**Explanation:** `Roads` is the central entity, referenced by `TrafficData`, `Incidents`, and
`AgentLogs`. `TrafficData` produces `Predictions`. `Incidents` trigger `Alerts`. `AgentLogs` ties
together a road, an optional prediction, and an optional incident, reflecting the agent's
"perceive both, then decide" workflow. All foreign keys to `Roads`/`Predictions`/`Incidents` from
`AgentLogs`/`Alerts` are nullable, since an agent decision or alert might stem from only a
prediction, only an incident, or both.
