# Architecture Explanation

## Overview

The system follows a standard 3-tier architecture, with the AI modules treated as a distinct
internal layer inside the backend so each can be explained and demoed independently.

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                    │
│  Login → Dashboard → Roads → Traffic → Incidents →       │
│  Alerts/Scenarios → Agent Decisions → Reports             │
└───────────────────────┬───────────────────────────────────┘
                         │ REST API (JWT-authenticated)
┌───────────────────────▼───────────────────────────────────┐
│                  BACKEND (FastAPI)                         │
│  api/  →  auth_routes, road_routes, traffic_routes,        │
│           prediction_routes, incident_routes,               │
│           alert_routes, agent_routes, report_routes          │
└───────┬──────────────┬───────────────┬──────────┬──────────┘
        │              │               │          │
┌───────▼─────┐ ┌──────▼──────┐ ┌──────▼─────┐ ┌──▼─────────┐
│ ml_module    │ │ dl_module    │ │ nlp_module │ │ slm_module │
│ Random Forest│ │ LSTM         │ │ spaCy      │ │ FLAN-T5    │
└──────────────┘ └──────────────┘ └────────────┘ └────────────┘
        │              │               │          │
┌───────▼──────────────▼───────────────▼──────────▼──────────┐
│              genai_module + agent_module                     │
│   Scenario Generator        Rule-based Decision Agent          │
└───────────────────────────────┬───────────────────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────┐
│                          MySQL Database                          │
│  Users, Roads, TrafficData, Predictions, Incidents, Alerts,       │
│  AgentLogs, Reports                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Why This Architecture?

**Separation of concerns.** Each AI technique lives in its own module folder
(`ml_module`, `dl_module`, `nlp_module`, `slm_module`, `genai_module`, `agent_module`). None of
them import each other except `agent_module`, which calls `slm_module` to generate alerts as
part of its decision workflow. This makes it trivial to demo or explain any one piece in
isolation during a viva.

**API layer as the only entry point.** The React frontend never talks to the database or AI
modules directly — everything goes through FastAPI routes in `api/`. This is the standard
pattern for any real web application and makes the system easy to extend (e.g. swap the
frontend for a mobile app later without touching any backend logic).

**Graceful degradation.** TensorFlow, spaCy's language model, and Transformers/Torch are
optional. If they aren't installed, `dl_module` reports a clear message and skips LSTM training,
`nlp_module` falls back to keyword matching, and `slm_module` falls back to templated alert
text. This means the system is always demoable, even on a machine where the heavier ML/DL
libraries failed to install (a common real-world problem worth mentioning in a viva).

**Agent as orchestrator, not a black box.** The Agentic AI module doesn't make decisions using
a trained model — it reads outputs from the other modules (a congestion prediction, an
incident's severity) and applies simple, fully-traceable if/else rules. This was a deliberate
choice per the project brief: a viva examiner can ask "why did the agent decide X?" and you can
point to the exact rule in `agent_module/traffic_agent.py` that produced it.

## Data Flow Example (End-to-End)

1. A traffic officer reports: *"Accident near Anna Salai due to heavy rain."*
2. `POST /incidents` → `nlp_module.analyze_incident()` extracts:
   `{road: "Anna Salai", type: "accident", severity: "high", weather: "rain"}`
   → saved to the `Incidents` table.
3. The dashboard separately calls `GET /prediction?traffic_id=...` for Anna Salai's latest
   reading → `ml_module` returns `congestion_level = "high"` → saved to `Predictions`.
4. `POST /agent/run?road_id=...&incident_id=...` → `agent_module.run_agent_cycle()`:
   - calls `slm_module.generate_alert()` → *"Avoid the area, expect delays near Anna Salai..."*
     → saved to `Alerts`.
   - applies the signal-timing rule for `congestion=high` → *"Extend green signal by 20s"*
     → saved to `AgentLogs`.
5. The dashboard's "Live Incident Feed", "Generated Alerts", and "Agent Decisions" panels
   immediately reflect all of this via their respective `GET` endpoints.
