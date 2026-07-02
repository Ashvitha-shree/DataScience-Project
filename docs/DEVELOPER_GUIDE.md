# Developer Guide

## Backend Codebase Walkthrough

```
backend/
├── main.py                  # FastAPI app, router registration, startup hook (creates tables + default admin)
├── config.py                # All settings loaded from .env via the Settings class
├── auth/
│   └── deps.py               # get_current_user / require_admin FastAPI dependencies (JWT validation)
├── database/
│   ├── db_connection.py      # SQLAlchemy engine/session + get_db() dependency
│   ├── models.py              # ORM models (one class per table, mirrors schema.sql)
│   └── schemas.py             # Pydantic request/response models (separate from ORM by design)
├── api/                      # One router file per resource; each mounted in main.py with a prefix
│   ├── auth_routes.py
│   ├── road_routes.py
│   ├── traffic_routes.py
│   ├── prediction_routes.py
│   ├── incident_routes.py
│   ├── alert_routes.py
│   ├── agent_routes.py
│   └── report_routes.py
├── ml_module/                 # Random Forest: training, evaluation, single-record prediction
├── dl_module/                  # LSTM: sequence building, training, forecasting
├── nlp_module/                  # spaCy + keyword-based incident field extraction
├── slm_module/                   # FLAN-T5 Small alert generation (+ templated fallback)
├── genai_module/                  # Scenario generator (OpenAI API or offline procedural fallback)
├── agent_module/                   # Rule-based decision agent
└── utils/
    ├── security.py                 # Password hashing (PBKDF2) + JWT encode/decode
    ├── csv_utils.py                 # CSV parse/export helpers for bulk traffic data
    └── pdf_utils.py                  # ReportLab-based PDF report builder
```

## Adding a New API Endpoint

1. Add/extend a Pydantic schema in `database/schemas.py` if needed.
2. Add the route function to the relevant file in `api/`, using `Depends(get_db)` for DB access
   and `Depends(get_current_user)` to require login.
3. If it's a new resource area, create a new `api/<name>_routes.py`, then register it in
   `main.py` with `app.include_router(...)`.
4. Add the corresponding call in `frontend/src/api/client.js` and wire it into the relevant page.

## Adding a New AI Module

Each AI module follows the same shape: a plain Python module with functions that take simple
inputs and return plain dicts/values — no FastAPI or SQLAlchemy imports inside the module files
themselves (that coupling happens only in `api/`). This keeps every module:
- independently testable (just call the function directly, see each module's `if __name__ ==
  "__main__":` block for a runnable example),
- explainable in isolation in a viva, without needing the whole stack running,
- swappable (e.g. replace `slm_module` with a different model without touching anything else).

## Database Migrations

This project uses `Base.metadata.create_all()` on startup as a simple safety net, but the
source of truth for the schema is `database/schema.sql`. If you change a table, update
`schema.sql` AND the matching class in `database/models.py` together, and re-run the schema
against a fresh database (or apply an `ALTER TABLE` manually) — there's no Alembic
migration tooling configured, by design, to keep the project simple for a college submission.

## Frontend Codebase Walkthrough

```
frontend/src/
├── main.jsx                 # ReactDOM root, wraps App in BrowserRouter + AuthProvider
├── App.jsx                  # All routes; ProtectedRoute wrapper redirects to /login if not authenticated
├── context/AuthContext.jsx  # Holds the logged-in user + JWT token (stored in localStorage)
├── api/client.js             # Single axios instance; every backend call lives here as a named export
├── components/
│   ├── Layout.jsx              # Sidebar + Navbar + <Outlet/> shell for all protected pages
│   ├── Sidebar.jsx, Navbar.jsx
│   ├── Card.jsx                 # StatCard, Badge
│   ├── TrafficChart.jsx          # Chart.js wrappers (line/bar/doughnut)
│   └── MapView.jsx                # Leaflet map for the Roads page
└── pages/                    # One file per sidebar item: Dashboard, Roads, TrafficData,
                               # Incidents, Alerts, AgentLogs, Reports, plus Login
```

State is kept simple and local to each page (`useState`/`useEffect` + direct API calls) rather
than a global store like Redux — appropriate for a project of this size, and easy to explain.

## Testing the AI Modules Directly (No Server Needed)

Every module under `backend/*_module/` can be run directly to sanity-check it in isolation:

```bash
cd backend
python -m ml_module.random_forest_model
python -m nlp_module.incident_extractor
python -m slm_module.alert_generator
python -m genai_module.scenario_generator
python -m agent_module.traffic_agent
```

Each prints a small example result, useful for a live viva demo without needing MySQL or the
frontend running at all.
