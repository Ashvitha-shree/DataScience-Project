"""
traffic_agent.py
Agentic AI module: a simple, fully explainable rule-based agent that ties
together everything else in the system.

WORKFLOW (matches the project spec exactly):
  1. Read traffic prediction      (from ml_module / dl_module output)
  2. Read incident analysis       (from nlp_module output)
  3. Generate alert                (calls slm_module)
  4. Recommend signal timing       (simple rule-based logic, see below)
  5. Store decision log            (AgentLogs table)

WHY RULE-BASED, NOT REINFORCEMENT LEARNING?
The project spec explicitly asks for simple reasoning, not RL - and that's
the right call for a college project: rule-based logic is 100% explainable
("if congestion is high AND there's an active incident, recommend +20s
green time") which is exactly what you want to be able to defend clearly
in a viva. RL would add huge complexity (reward design, training loops,
exploration/exploitation) without adding educational value here.

SIGNAL TIMING RECOMMENDATION LOGIC (simple, explainable rules):
  - congestion = high    -> extend green signal by 20 seconds
  - congestion = medium  -> extend green signal by 10 seconds
  - congestion = low     -> no change needed
  - severity = critical (incident) -> recommend manual police control instead
"""
from slm_module.alert_generator import generate_alert

SIGNAL_RULES = {
    "high": ("Extend green signal by 20 seconds", "High congestion detected"),
    "medium": ("Extend green signal by 10 seconds", "Moderate congestion detected"),
    "low": ("No signal change needed", "Traffic flow is normal"),
}


def recommend_signal_timing(congestion_level: str, incident_severity: str = None):
    """Pure rule-based decision - easy to trace and explain step by step."""
    if incident_severity == "critical":
        return "Switch to manual police control", "Critical incident reported - automated signals insufficient"
    return SIGNAL_RULES.get(congestion_level, SIGNAL_RULES["low"])


def run_agent_cycle(road_name, congestion_level=None, incident=None):
    """Runs one full perceive -> decide -> act cycle for a single road.

    Parameters
    ----------
    road_name : str
    congestion_level : str, optional   - output of ml_module prediction
    incident : dict, optional          - output of nlp_module.analyze_incident,
                                          plus 'raw_text' if available

    Returns a dict ready to be saved into AgentLogs, plus the generated
    alert text (saved separately into Alerts).
    """
    incident_type = incident["incident_type"] if incident else None
    severity = incident["severity"] if incident else None

    # Step 3: generate alert (only if there's something alert-worthy)
    alert_text = None
    if incident or (congestion_level in ("medium", "high")):
        alert_text = generate_alert(
            road_name=road_name,
            incident_type=incident_type or "congestion",
            severity=severity or congestion_level or "medium",
            congestion_level=congestion_level,
        )

    # Step 4: recommend signal timing
    decision, reason = recommend_signal_timing(congestion_level or "low", severity)

    # Step 5: build the log entry (caller is responsible for writing to DB,
    # keeping this module DB-agnostic and easy to unit test)
    urgency = "critical" if severity == "critical" else (
        "high" if congestion_level == "high" else
        "medium" if congestion_level == "medium" else "low"
    )

    return {
        "road_name": road_name,
        "decision": decision,
        "reason": reason,
        "urgency": urgency,
        "alert_text": alert_text,
    }


if __name__ == "__main__":
    result = run_agent_cycle(
        road_name="Anna Salai",
        congestion_level="high",
        incident={"incident_type": "accident", "severity": "high"},
    )
    print(result)
