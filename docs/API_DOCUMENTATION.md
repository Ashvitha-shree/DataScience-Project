# API Documentation

Base URL (local): `http://localhost:8000`
Interactive Swagger/OpenAPI docs: `http://localhost:8000/docs`

All endpoints except `/auth/login` and `/auth/register` require a JWT bearer token:
`Authorization: Bearer <access_token>` (obtained from `/auth/login`).

## Authentication

### POST `/auth/register`
Creates a new user. Body:
```json
{ "name": "Jane Officer", "email": "jane@city.gov", "password": "secret123", "role": "officer" }
```

### POST `/auth/login`
Body: `{ "email": "...", "password": "..." }`
Response:
```json
{ "access_token": "...", "token_type": "bearer", "user": { "user_id": 1, "name": "...", "email": "...", "role": "admin" } }
```

### GET `/auth/me`
Returns the currently logged-in user.

## Roads

| Method | Path | Description |
|---|---|---|
| GET | `/roads/` | List all roads |
| GET | `/roads/{road_id}` | Get one road |
| POST | `/roads/` | Create a road |
| PUT | `/roads/{road_id}` | Update a road |
| DELETE | `/roads/{road_id}` | Delete a road |

Create body:
```json
{ "road_name": "Anna Salai", "location": "Chennai", "latitude": 13.06, "longitude": 80.25, "road_type": "arterial", "signal_id": "SIG-002" }
```

## Traffic Data

| Method | Path | Description |
|---|---|---|
| GET | `/traffic/?road_id=&limit=` | List traffic records |
| GET | `/traffic/{traffic_id}` | Get one record |
| POST | `/traffic/` | Create a record |
| PUT | `/traffic/{traffic_id}` | Update a record |
| DELETE | `/traffic/{traffic_id}` | Delete a record |
| POST | `/traffic/upload-csv` | Bulk upload (multipart file) |
| GET | `/traffic/export/download-csv?road_id=` | Download CSV export |

Create body:
```json
{
  "road_id": 2, "vehicle_count": 320, "avg_speed": 18.5, "weather": "rain",
  "record_date": "2026-06-30", "record_time": "18:30:00", "day_of_week": "Tuesday",
  "congestion_level": "high"
}
```

## Predictions (ML)

| Method | Path | Description |
|---|---|---|
| GET | `/prediction/?traffic_id=` | Predict congestion for a traffic record (Random Forest) |
| POST | `/prediction/train` | Re-train the Random Forest model, returns evaluation metrics |

## Incidents (NLP)

| Method | Path | Description |
|---|---|---|
| GET | `/incidents/?limit=` | List incidents |
| POST | `/incidents/` | Submit a raw incident report; NLP extracts structured fields |

Create body:
```json
{ "raw_text": "Accident near Anna Salai due to heavy rain.", "reported_by": "citizen" }
```

## Alerts (SLM) & Scenarios (GenAI)

| Method | Path | Description |
|---|---|---|
| GET | `/alerts/?limit=` | List generated alerts |
| POST | `/alerts/generate` | Generate an alert for an incident (`{"incident_id": 5}`) |
| GET | `/alerts/scenario?scenario_type=` | Generate a GenAI scenario (type optional) |
| GET | `/alerts/scenario/types` | List available scenario types |

## Agentic AI

| Method | Path | Description |
|---|---|---|
| GET | `/agent/?limit=` | List recent agent decisions |
| POST | `/agent/run?road_id=&traffic_id=&incident_id=` | Run one perceive→reason→act→log cycle |

## Reports

| Method | Path | Description |
|---|---|---|
| GET | `/reports/?report_type=daily\|weekly\|monthly` | Generates and downloads a PDF report |

## Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/` | API root info |
