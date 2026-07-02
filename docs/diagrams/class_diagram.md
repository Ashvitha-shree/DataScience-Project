# Class Diagram

```mermaid
classDiagram
    class User {
        +int user_id
        +str name
        +str email
        +str password_hash
        +str role
        +datetime created_at
    }

    class Road {
        +int road_id
        +str road_name
        +str location
        +float latitude
        +float longitude
        +str road_type
        +str signal_id
    }

    class TrafficData {
        +int traffic_id
        +int road_id
        +int vehicle_count
        +float avg_speed
        +str weather
        +date record_date
        +time record_time
        +str day_of_week
        +str congestion_level
    }

    class Prediction {
        +int prediction_id
        +int traffic_id
        +str model_used
        +str predicted_level
        +float predicted_speed
        +float confidence
        +datetime predicted_at
    }

    class Incident {
        +int incident_id
        +int road_id
        +str raw_text
        +str incident_type
        +str severity
        +str weather
        +str reported_by
        +datetime reported_at
    }

    class Alert {
        +int alert_id
        +int incident_id
        +int road_id
        +str alert_text
        +datetime generated_at
    }

    class AgentLog {
        +int log_id
        +int road_id
        +int prediction_id
        +int incident_id
        +str decision
        +str reason
        +str urgency
        +datetime created_at
    }

    class Report {
        +int report_id
        +str report_type
        +date start_date
        +date end_date
        +str file_path
        +int generated_by
    }

    class RandomForestModel {
        +train_random_forest()
        +predict_congestion()
        +engineer_features()
    }

    class LSTMModel {
        +build_sequences()
        +train_lstm()
        +predict_next_speed()
    }

    class IncidentExtractor {
        +analyze_incident(text)
        +extract_road(text)
        +extract_severity(text)
    }

    class AlertGenerator {
        +generate_alert(road, type, severity)
    }

    class ScenarioGenerator {
        +generate_scenario(type)
    }

    class TrafficAgent {
        +run_agent_cycle(road, congestion, incident)
        +recommend_signal_timing()
    }

    Road "1" --> "many" TrafficData
    TrafficData "1" --> "many" Prediction
    Road "1" --> "many" Incident
    Incident "1" --> "many" Alert
    Road "1" --> "many" AgentLog
    Prediction "0..1" --> "many" AgentLog
    Incident "0..1" --> "many" AgentLog
    User "1" --> "many" Report

    TrafficAgent ..> AlertGenerator : uses
    TrafficAgent ..> AgentLog : creates
    IncidentExtractor ..> Incident : populates
    RandomForestModel ..> Prediction : populates
    LSTMModel ..> Prediction : populates
    AlertGenerator ..> Alert : populates
```

**Explanation:** The top section shows the persistent entity classes (mirroring the database
tables). The bottom section shows the key service/logic classes (one per AI module) and how
they relate to those entities — e.g. `TrafficAgent` uses `AlertGenerator` and creates `AgentLog`
records, `RandomForestModel` produces `Prediction` records.
