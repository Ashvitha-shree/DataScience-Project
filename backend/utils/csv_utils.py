"""
csv_utils.py
Helpers for bulk CSV upload (traffic data) and CSV export.
"""
import csv
import io
from datetime import datetime


REQUIRED_COLUMNS = ["road_id", "vehicle_count", "avg_speed", "weather",
                    "record_date", "record_time", "day_of_week"]


def parse_traffic_csv(file_bytes: bytes):
    """Parses an uploaded CSV file into a list of dicts ready for bulk insert.
    Validates required columns and skips/reports malformed rows."""
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    rows, errors = [], []
    for i, row in enumerate(reader, start=2):  # row 1 is header
        try:
            rows.append({
                "road_id": int(row["road_id"]),
                "vehicle_count": int(row["vehicle_count"]),
                "avg_speed": float(row["avg_speed"]),
                "weather": row.get("weather", "clear") or "clear",
                "record_date": row["record_date"],
                "record_time": row["record_time"],
                "day_of_week": row.get("day_of_week") or "",
                "congestion_level": row.get("congestion_level") or None,
            })
        except (ValueError, KeyError) as e:
            errors.append(f"Row {i}: {e}")

    return rows, errors


def export_traffic_to_csv(records: list) -> str:
    """records: list of dict-like TrafficData rows. Returns CSV text."""
    output = io.StringIO()
    fieldnames = ["traffic_id", "road_id", "vehicle_count", "avg_speed", "weather",
                  "record_date", "record_time", "day_of_week", "congestion_level"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
        writer.writerow({k: r.get(k) for k in fieldnames})
    return output.getvalue()
