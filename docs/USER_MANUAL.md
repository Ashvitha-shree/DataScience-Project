# User Manual

## Logging In

Open the frontend URL and sign in with your email and password. A default admin account is
created automatically: `admin@smarttraffic.local` / `Admin@123`. You can register additional
Traffic Officer accounts via the `POST /auth/register` API endpoint (no public sign-up page is
exposed in the UI by design, since this is an internal city operations tool).

## Dashboard

The landing page after login. Shows:
- **Stat cards** — recent traffic record count, active incidents, alerts generated, agent decisions.
- **Average Speed Trend** chart — recent readings plotted over time.
- **Congestion Breakdown** doughnut chart — proportion of low/medium/high congestion records.
- **Live Incident Feed**, **Generated Alerts**, and **Agent Decisions** panels — the three most
  recent items from each, refreshed every time you load the page.

## Roads

Manage the list of monitored roads.
- **Add Road** — opens a form for name, location, road type, latitude/longitude, and signal ID.
- **Map** — every road with coordinates appears as a pin (powered by Leaflet/OpenStreetMap);
  click a pin to see its details.
- **Edit/Delete** — available as icon buttons on each table row. Deleting a road also deletes
  its associated traffic data (cascading delete).

## Traffic Data

- **Add Record** — manually log a new sensor reading for a road.
- **Upload CSV** — bulk-import traffic data; the CSV must include the columns: `road_id,
  vehicle_count, avg_speed, weather, record_date, record_time, day_of_week` (and optionally
  `congestion_level` for labelled training data). Malformed rows are reported back, not silently
  dropped.
- **Download CSV** — exports all current traffic data.
- **Train ML Model** — retrains the Random Forest classifier on `dataset/sample_traffic_data.csv`
  and shows the resulting accuracy/F1 score.
- **Predict** — click next to any record to run the trained model on that specific reading and
  see the predicted congestion level with a confidence percentage.

## Incidents

Submit a free-text incident report (e.g. *"Accident near Anna Salai due to heavy rain."*) and the
NLP module automatically extracts the road, incident type, severity, and weather — shown
immediately in the table below the form.

## Alerts & Scenarios

Two independent tools on one page:
- **Generate Commuter Alert** — pick an existing incident from the dropdown and generate a short,
  FLAN-T5-powered alert message for it.
- **Generative AI Scenario Generator** — pick a scenario type (or leave it random) and generate a
  realistic hypothetical situation (flood, festival, road closure, political rally, accident,
  emergency) along with recommended actions — useful for testing and planning discussions.

## Agent Decisions

Select a road and click **Run Agent Cycle**. The agent reads the road's latest prediction and any
related incident, generates an alert if warranted, recommends a signal-timing change, and logs
the decision with its reasoning — visible immediately in the table below.

## Reports

Download a Daily, Weekly, or Monthly PDF report summarizing traffic volume, incidents, alerts,
and agent decisions for that period.
