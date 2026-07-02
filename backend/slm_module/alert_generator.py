"""
alert_generator.py
Small Language Model (SLM) module: uses Google's FLAN-T5 Small
(~80M parameters - small enough to run on a laptop CPU, unlike a full LLM)
to turn structured incident + prediction data into a short, human-readable
commuter alert.

WHY A SMALL LANGUAGE MODEL HERE (instead of calling a big LLM API)?
Alert generation is a narrow, repetitive task ("turn these 3-4 fields into
one short sentence") - it doesn't need a huge general-purpose model. A
small, locally-run model is faster, free to run, and works offline, which
matters for a city traffic system that must keep working even without
internet access. This also demonstrates the SLM vs LLM distinction clearly
for a viva: FLAN-T5 Small here is "the right-sized tool for a narrow job",
while genai_module/scenario_generator.py shows where a bigger general LLM
is more appropriate (open-ended scenario writing).

PROMPT DESIGN
We use a simple instruction-style prompt:
  "generate alert: road=<X>; type=<Y>; severity=<Z>; congestion=<W>"
FLAN-T5 was trained on instruction-following data, so this kind of direct
"task: details" prompt works well even without fine-tuning. For better
results in your final project you can fine-tune on a small set of
(prompt -> ideal alert) pairs - see comments below for how.

This module works even without transformers/torch installed - falling
back to the same template logic used to build the model's expected output,
so the system always produces a usable alert.
"""
try:
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

_MODEL_NAME = "google/flan-t5-small"
_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if not TRANSFORMERS_AVAILABLE:
        raise ImportError("transformers/torch not installed.")
    if _model is None:
        _tokenizer = T5Tokenizer.from_pretrained(_MODEL_NAME)
        _model = T5ForConditionalGeneration.from_pretrained(_MODEL_NAME)
    return _tokenizer, _model


ACTION_TEMPLATES = {
    "accident": "Avoid the area, expect delays",
    "roadwork": "Use an alternate route, lane closures in effect",
    "breakdown": "Slow down, a vehicle is on the shoulder",
    "flooding": "Avoid this stretch, road may be impassable",
    "protest": "Expect diversions, plan extra travel time",
    "signal_failure": "Proceed with caution, signal is not working",
    "pothole": "Reduce speed, road surface is damaged",
    "other": "Proceed with caution",
}


def _template_fallback(road_name, incident_type, severity, congestion_level=None):
    action = ACTION_TEMPLATES.get(incident_type, ACTION_TEMPLATES["other"])
    road_disp = road_name or "the reported area"
    delay = {"low": "5", "medium": "15", "high": "25", "critical": "40+"}.get(severity, "15")
    extra = f" Expected delay: {delay} minutes." if incident_type != "other" else ""
    congestion_note = f" Current congestion: {congestion_level}." if congestion_level else ""
    return f"{action} near {road_disp}.{congestion_note}{extra}"


def generate_alert(road_name, incident_type, severity, congestion_level=None):
    """Generates a short commuter alert. Uses FLAN-T5 Small if installed,
    otherwise a clear rule-based template (same information content)."""
    if TRANSFORMERS_AVAILABLE:
        try:
            tokenizer, model = _load_model()
            prompt = (
                f"Write a short traffic alert for commuters. "
                f"Road: {road_name or 'unknown road'}. "
                f"Incident: {incident_type}. Severity: {severity}. "
                f"Current congestion: {congestion_level or 'unknown'}. "
                f"Suggest an alternate action."
            )
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
            output_ids = model.generate(**inputs, max_length=48, num_beams=2)
            text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            if text.strip():
                return text.strip()
        except Exception as e:
            print(f"FLAN-T5 generation failed ({e}); using template fallback.")

    return _template_fallback(road_name, incident_type, severity, congestion_level)


# ------------------------------------------------------------------
# OPTIONAL: fine-tuning sketch (not run automatically - for students who
# want to go further). Build (prompt, target_alert) pairs from your own
# incident data and fine-tune with HuggingFace's Seq2SeqTrainer, the same
# way as in the bigger smart-city-traffic-system project's
# src/slm/finetune.py reference implementation.
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(generate_alert("Anna Salai", "accident", "high", "high"))
