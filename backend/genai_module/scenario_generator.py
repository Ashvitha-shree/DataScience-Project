"""
scenario_generator.py
Generative AI module: generates realistic "what-if" traffic scenarios
(Flood, Festival, Road Closure, Political Rally, Accident, Emergency) for
testing the system and for demo purposes on the dashboard.

WHY GENERATIVE AI HERE?
Unlike the SLM module (narrow task: structured data -> one short alert),
scenario generation is open-ended creative writing - "describe a realistic
situation and its impact". This is exactly the kind of task a general
large language model is good at. If an OPENAI_API_KEY is configured, this
module calls OpenAI's API for richer, more varied scenarios; otherwise it
falls back to a built-in procedural generator so the project always works,
even with no internet access or API key (important for a viva demo where
you can't rely on network access).
"""
import os
import json
import random
import urllib.request

SCENARIO_TYPES = ["flood", "festival", "road_closure", "political_rally", "accident", "emergency"]

ROADS = [
    "MG Road", "Anna Salai", "OMR", "ECR", "GST Road", "Mount Road",
    "Poonamallee High Road", "Velachery Main Road",
]

_TEMPLATES = {
    "flood": (
        "Heavy rainfall has caused waterlogging on {road}. Vehicles are advised to avoid "
        "the stretch near {road2} until water recedes. Average speed expected to drop by {pct}%."
    ),
    "festival": (
        "A city festival near {road} is drawing large crowds, with heavy footfall and parking "
        "overflow expected to affect {road2}. Plan for {pct}% higher travel time during evening hours."
    ),
    "road_closure": (
        "{road} will be partially closed for maintenance work between {start} and {end}. "
        "Traffic is being diverted via {road2}, causing secondary congestion."
    ),
    "political_rally": (
        "A political rally is scheduled along {road}, requiring full road closure from {start} "
        "to {end}. Commuters should use {road2} as an alternate route."
    ),
    "accident": (
        "A multi-vehicle accident has been reported on {road}, blocking one lane. Emergency "
        "services are on site; expect delays of {delay} minutes near the junction with {road2}."
    ),
    "emergency": (
        "An emergency vehicle corridor is being enforced on {road} for ambulance/fire access. "
        "All traffic must yield; {road2} is recommended as the alternate route."
    ),
}

_ACTIONS = {
    "flood": ["Deploy water pumps at low-lying junctions", "Issue waterlogging alerts to commuters",
               "Lower speed advisory on affected roads"],
    "festival": ["Open additional parking zones", "Increase public transport frequency",
                  "Deploy traffic police at key junctions"],
    "road_closure": ["Publish diversion routes in advance", "Retime signals on alternate roads",
                       "Notify commuters via SLM-generated alerts"],
    "political_rally": ["Coordinate road closure with police", "Activate diversion signage",
                          "Increase patrol presence along alternate routes"],
    "accident": ["Dispatch traffic police to the scene", "Reroute traffic via agent recommendation",
                  "Issue an immediate commuter alert"],
    "emergency": ["Clear the emergency corridor immediately", "Hold cross traffic at signals",
                   "Notify nearby roads of the diversion"],
}


def _procedural_scenario(scenario_type: str) -> dict:
    template = _TEMPLATES[scenario_type]
    text = template.format(
        road=random.choice(ROADS), road2=random.choice(ROADS),
        pct=random.choice([20, 35, 50, 70]),
        start=f"{random.randint(6,20)}:00", end=f"{random.randint(20,23)}:00",
        delay=random.choice([10, 20, 30, 45]),
    )
    return {"scenario_type": scenario_type, "description": text,
            "recommended_actions": _ACTIONS[scenario_type]}


def _openai_scenario(scenario_type: str, api_key: str) -> dict:
    prompt = (f"Write a realistic 2-3 sentence traffic scenario of type '{scenario_type}' "
              f"for an Indian city road network. Be specific about impact on traffic flow.")
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    text = data["choices"][0]["message"]["content"]
    return {"scenario_type": scenario_type, "description": text, "recommended_actions": _ACTIONS[scenario_type]}


def generate_scenario(scenario_type: str = None) -> dict:
    scenario_type = scenario_type or random.choice(SCENARIO_TYPES)
    if scenario_type not in SCENARIO_TYPES:
        raise ValueError(f"scenario_type must be one of {SCENARIO_TYPES}")

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            return _openai_scenario(scenario_type, api_key)
        except Exception as e:
            print(f"OpenAI call failed ({e}); using procedural generator.")
    return _procedural_scenario(scenario_type)


def generate_synthetic_traffic_row(road_id: int):
    """Generates one synthetic TrafficData-like row, useful for quickly
    populating test data tied to a generated scenario."""
    import datetime
    return {
        "road_id": road_id,
        "vehicle_count": random.randint(50, 500),
        "avg_speed": round(random.uniform(5, 60), 1),
        "weather": random.choice(["clear", "rain", "fog", "storm"]),
        "record_date": datetime.date.today().isoformat(),
        "record_time": f"{random.randint(0,23):02d}:{random.choice([0,15,30,45]):02d}:00",
        "day_of_week": datetime.date.today().strftime("%A"),
    }


if __name__ == "__main__":
    for st in SCENARIO_TYPES:
        s = generate_scenario(st)
        print(f"\n[{st}] {s['description']}")
