# Installation Guide

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Node.js 18+ and npm
- MySQL 8.0+
- (Optional, for full DL/NLP/SLM features) ~6 GB free disk space for TensorFlow + Transformers + Torch

## Step 1 — Clone / Extract the Project

Extract the ZIP, then confirm the folder structure:

```bash
cd smart-traffic-system
ls
# Should show: backend/ frontend/ database/ dataset/ docs/ README.md
```

## Step 2 — Set Up MySQL

```bash
mysql -u root -p
```

Inside the MySQL shell:
```sql
SOURCE database/schema.sql;
EXIT;
```

This creates the `smart_traffic_db` database, all tables, and seeds 10 sample roads.

## Step 3 — Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If installing TensorFlow/spaCy/Transformers together causes a slow dependency resolution on
your machine, install the core packages first and add the rest afterward:

```bash
pip install fastapi uvicorn[standard] pydantic[email] python-dotenv python-multipart \
            sqlalchemy pymysql cryptography pyjwt scikit-learn joblib numpy pandas \
            matplotlib reportlab requests

# Then, optionally:
pip install tensorflow
pip install spacy && python -m spacy download en_core_web_sm
pip install transformers torch
```

Configure environment variables:
```bash
cp .env.example .env
# Edit .env: set DB_PASSWORD to your MySQL password, and JWT_SECRET_KEY to a random string
```

Generate the sample dataset and copy it where the backend expects it:
```bash
cd ../dataset
python generate_sample_dataset.py
cd ../backend
mkdir -p dataset
cp ../dataset/sample_traffic_data.csv dataset/sample_traffic_data.csv
```

Train the Random Forest model (also produces confusion matrix / ROC / feature importance plots
in `ml_module/evaluation_plots/`):
```bash
python -m ml_module.evaluate_model
```

(Optional) Train the LSTM model:
```bash
python -m dl_module.lstm_model
```

Start the API server:
```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to confirm the API is running and explore every endpoint.

A default admin account is created automatically on first startup:
**Email:** `admin@smarttraffic.local` **Password:** `Admin@123`

## Step 4 — Frontend Setup

In a new terminal:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173` and log in with the default admin account.

## Step 5 — Verify Everything Works

1. Log in.
2. Go to **Roads** — you should see the 10 seeded roads on the map.
3. Go to **Traffic Data** — click **Train ML Model** and confirm an accuracy is displayed.
4. Add a traffic record, then click **Predict** next to it.
5. Go to **Incidents** — submit `"Accident near Anna Salai due to heavy rain."` and confirm the
   extracted fields appear correctly.
6. Go to **Alerts & Scenarios** — generate an alert from the incident you just created, and
   generate a GenAI scenario.
7. Go to **Agent Decisions** — select a road and click **Run Agent Cycle**.
8. Go to **Reports** — download a Daily PDF report.

If all of the above work, the full project is running end-to-end.

## Troubleshooting

- **`Could not open requirements file`** — you're in the wrong folder; `cd` into the folder that
  actually contains `requirements.txt` (run `ls`/`dir` to check) before running `pip install`.
- **MySQL connection refused** — confirm MySQL is running (`mysqladmin status` or check your OS
  service manager) and that `DB_HOST`/`DB_PORT`/`DB_USER`/`DB_PASSWORD` in `.env` are correct.
- **TensorFlow/spaCy/Transformers fail to install** — skip them; the project still runs fully
  with the core dependencies, using fallback logic in `dl_module`, `nlp_module`, `slm_module`.
- **CORS errors in the browser console** — make sure `ALLOWED_ORIGINS` in backend `.env` includes
  `http://localhost:5173` (the default Vite dev server port).
