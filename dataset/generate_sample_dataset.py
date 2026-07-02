"""
generate_sample_dataset.py
Generates a realistic, labelled sample traffic dataset for training the
Random Forest model and seeding the database. Run this once before
training: `python generate_sample_dataset.py`

NOTE: road_id values here (1-10) match the order roads are inserted in
database/schema.sql, so the generated CSV lines up correctly once you've
run the schema against MySQL.
"""
import csv
import random
import datetime

random.seed(42)

ROAD_IDS = list(range(1, 11))  # matches the 10 roads seeded in schema.sql
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEATHER_OPTIONS = ["clear", "clear", "clear", "rain", "fog", "storm"]


def label_congestion(vehicle_count, avg_speed):
    """Simple rule used ONLY to label the synthetic training data -
    the actual ML model learns to approximate this kind of relationship
    from the features, it doesn't see this rule directly."""
    if avg_speed > 45 and vehicle_count < 200:
        return "low"
    elif avg_speed > 25 and vehicle_count < 350:
        return "medium"
    else:
        return "high"


def generate_dataset(n_days=45, rows_per_day_per_road=3, out_path="sample_traffic_data.csv"):
    start_date = datetime.date.today() - datetime.timedelta(days=n_days)
    rows = []

    for day_offset in range(n_days):
        current_date = start_date + datetime.timedelta(days=day_offset)
        day_name = DAYS[current_date.weekday()]
        is_weekend = current_date.weekday() >= 5

        for road_id in ROAD_IDS:
            for _ in range(rows_per_day_per_road):
                hour = random.randint(0, 23)
                minute = random.choice([0, 15, 30, 45])

                # Rush-hour effect on weekdays
                rush = 1.0
                if not is_weekend:
                    if 8 <= hour <= 10 or 17 <= hour <= 20:
                        rush = 2.0
                    elif 0 <= hour <= 5:
                        rush = 0.4
                else:
                    if 11 <= hour <= 21:
                        rush = 1.3

                weather = random.choice(WEATHER_OPTIONS)
                weather_penalty = 1.4 if weather in ("rain", "storm") else 1.0

                vehicle_count = max(10, int(random.gauss(180, 60) * rush * weather_penalty))
                avg_speed = max(3, round(random.gauss(40, 12) / (rush * weather_penalty), 1))

                rows.append({
                    "road_id": road_id,
                    "vehicle_count": vehicle_count,
                    "avg_speed": avg_speed,
                    "weather": weather,
                    "record_date": current_date.isoformat(),
                    "record_time": f"{hour:02d}:{minute:02d}:00",
                    "day_of_week": day_name,
                    "congestion_level": label_congestion(vehicle_count, avg_speed),
                })

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {out_path}")
    return rows


if __name__ == "__main__":
    generate_dataset()
