"""
incident_extractor.py
NLP module: reads a free-text traffic incident report (e.g. "Accident near
Anna Salai due to heavy rain") and extracts structured fields:
  - road name      (matched against a gazetteer/list of known roads)
  - incident type  (accident, roadwork, breakdown, flooding, protest, etc.)
  - severity       (low / medium / high / critical, from keyword cues)
  - weather        (rain, fog, clear, etc., from keyword cues)

WHY spaCy?
spaCy gives us a ready-made NLP pipeline (tokenization, part-of-speech
tagging, and Named Entity Recognition) without training our own model from
scratch - perfect for a college project where the goal is to demonstrate
NLP techniques, not build a production NER system. We combine spaCy's
generic NER with a simple keyword/gazetteer approach for the
traffic-specific fields (road names, severity, incident type), since
spaCy's default model doesn't know about local road names out of the box.

This module works even if spaCy / the "en_core_web_sm" model are not
installed - it then falls back to a pure keyword-matching approach so the
project still runs end-to-end (clearly explainable in a viva as "graceful
degradation").
"""
import re

try:
    import spacy
    try:
        _NLP = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        SPACY_AVAILABLE = False
        _NLP = None
except ImportError:
    SPACY_AVAILABLE = False
    _NLP = None

KNOWN_ROADS = [
    "MG Road", "Anna Salai", "OMR", "ECR", "GST Road", "Mount Road",
    "Poonamallee High Road", "Velachery Main Road", "Sardar Patel Road",
    "Rajiv Gandhi Salai", "Cathedral Road",
]

INCIDENT_KEYWORDS = {
    "accident": ["accident", "collision", "crash"],
    "roadwork": ["roadwork", "construction", "maintenance", "repair"],
    "breakdown": ["breakdown", "broke down", "stalled"],
    "flooding": ["flood", "waterlog", "water logging"],
    "protest": ["protest", "rally", "march", "gathering", "political rally"],
    "signal_failure": ["signal failure", "signal malfunction", "signal outage"],
    "pothole": ["pothole", "road damage", "surface damage"],
}

SEVERITY_KEYWORDS = {
    "critical": ["severe", "major", "critical", "emergency", "impassable"],
    "high": ["heavy", "blocked", "long delays"],
    "medium": ["moderate", "slow", "delays"],
    "low": ["minor", "small"],
}

WEATHER_KEYWORDS = {
    "rain": ["rain", "rainy", "downpour", "monsoon"],
    "fog": ["fog", "foggy", "mist"],
    "storm": ["storm", "cyclone", "wind"],
    "clear": ["clear", "sunny"],
}


def extract_road(text: str):
    for road in KNOWN_ROADS:
        if road.lower() in text.lower():
            return road
    if SPACY_AVAILABLE:
        doc = _NLP(text)
        for ent in doc.ents:
            if ent.label_ in ("FAC", "LOC", "GPE", "ORG"):
                return ent.text
    return None


def _match_keywords(text: str, keyword_map: dict, default="unknown"):
    text_low = text.lower()
    for label, keywords in keyword_map.items():
        if any(kw in text_low for kw in keywords):
            return label
    return default


def extract_incident_type(text: str) -> str:
    return _match_keywords(text, INCIDENT_KEYWORDS, default="other")


def extract_severity(text: str) -> str:
    return _match_keywords(text, SEVERITY_KEYWORDS, default="medium")


def extract_weather(text: str) -> str:
    return _match_keywords(text, WEATHER_KEYWORDS, default="clear")


def analyze_incident(text: str) -> dict:
    """Main entry point: returns the four structured fields extracted from
    a raw incident report, ready to be stored in the Incidents table."""
    return {
        "road_name": extract_road(text),
        "incident_type": extract_incident_type(text),
        "severity": extract_severity(text),
        "weather": extract_weather(text),
    }


if __name__ == "__main__":
    sample = "Accident near Anna Salai due to heavy rain."
    print(analyze_incident(sample))
