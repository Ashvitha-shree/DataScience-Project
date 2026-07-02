# AI-Based Smart City Traffic Management and Optimization System

A final-year engineering project that predicts traffic congestion, analyzes incident reports,
generates commuter alerts, simulates traffic scenarios, and recommends signal timing — combining
Machine Learning, Deep Learning, NLP, a Small Language Model, Generative AI, and a simple
Agentic AI decision layer.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Tailwind CSS, Chart.js, Leaflet.js |
| Backend | Python, FastAPI |
| Database | MySQL |
| Machine Learning | Scikit-learn (Random Forest) |
| Deep Learning | TensorFlow/Keras (LSTM) |
| NLP | spaCy |
| Small Language Model | FLAN-T5 Small (HuggingFace Transformers) |
| Generative AI | OpenAI API (optional) with an offline procedural fallback |
| Reports | ReportLab (PDF) |

## What Each AI Module Does (Quick Summary)

1. **ML (Random Forest)** — predicts congestion level (low/medium/high) from a single traffic
   reading (vehicle count, speed, time, weather).
2. **DL (LSTM)** — predicts traffic speed ~30 minutes ahead using a sequence of recent readings
   (handles the *time* dimension that Random Forest can't).
3. **NLP (spaCy)** — reads free-text incident reports and extracts road name, incident type,
   severity, and weather.
4. **SLM (FLAN-T5 Small)** — turns structured incident/prediction data into a short commuter
   alert message.
5. **GenAI** — generates realistic hypothetical scenarios (flood, festival, road closure,
   political rally, accident, emergency) for testing and planning.
6. **Agentic AI** — a simple rule-based agent that reads predictions + incidents, generates an
   alert, recommends signal timing, and logs its decision. No reinforcement learning — every
   decision is a traceable if/else rule, by design, so it's easy to explain in a viva.

Every module is intentionally independent: removing any one of them still leaves a working
system, which makes it easy to explain "what does X module actually contribute?" in a viva.

## Quick Start

### 1. Database

```bash
mysql -u root -p < database/schema.sql
```

This creates the `smart_traffic_db` database, all 8 tables, and seeds 10 sample roads.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit DB_PASSWORD etc.

# Generate / refresh the sample dataset used to train the ML model
cd ../dataset && python generate_sample_dataset.py && cd ../backend
cp ../dataset/sample_traffic_data.csv dataset/sample_traffic_data.csv

# Train the Random Forest model (also produces evaluation plots)
python -m ml_module.evaluate_model

uvicorn main:app --reload --port 8000
```

The backend automatically creates a default admin account on first run:
**admin@smarttraffic.local / Admin@123**

API docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173` and log in with the default admin account above.

## Optional Heavy Dependencies

`requirements.txt` includes TensorFlow, spaCy, and Transformers/Torch for the LSTM, NLP, and
SLM modules. These are large installs; every module that uses them has a graceful fallback
(keyword matching for NLP, templated text for SLM) so the system still runs end-to-end without
them. If you do install spaCy, also run:

```bash
python -m spacy download en_core_web_sm
```

## Documentation

See the `docs/` folder for:
- `ARCHITECTURE.md` — system architecture explanation
- `INSTALLATION.md` — detailed setup guide
- `USER_MANUAL.md` — how to use each screen
- `DEVELOPER_GUIDE.md` — codebase walkthrough
- `API_DOCUMENTATION.md` — every endpoint documented
- `ALGORITHMS.md` — algorithms used and why
- `PROJECT_REPORT.md` — full report-style writeup (purpose, advantages, limitations, future scope)
- `VIVA_QUESTIONS.md` — likely viva questions with model answers
- `diagrams/` — Use Case, Class, Sequence, ER, Component, and Deployment diagrams (Mermaid source,
  viewable directly on GitHub or in VS Code with a Mermaid preview extension)

## Project Structure

```
smart-traffic-system/
├── frontend/        React + Tailwind dashboard
├── backend/         FastAPI app, all AI modules, database layer
├── dataset/          sample dataset + generator script
├── database/         SQL schema
├── docs/             documentation + diagrams
└── models/            (trained model artifacts land in backend/ml_module/saved_model etc.)
```
