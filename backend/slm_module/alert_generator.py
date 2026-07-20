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
    "accident": lambda road, severity, congestion:
        f"Accident reported on {road}. {severity.capitalize()} severity. Expect {congestion} congestion. Please use alternate routes.",

    "roadwork": lambda road, severity, congestion:
        f"Roadwork in progress on {road}. Drive carefully and expect minor delays.",

    "breakdown": lambda road, severity, congestion:
        f"Vehicle breakdown on {road}. Traffic is moving slowly. Please proceed with caution.",

    "flooding": lambda road, severity, congestion:
        f"Flooding reported on {road}. Avoid this route and follow traffic diversions.",

    "signal_failure": lambda road, severity, congestion:
        f"Traffic signal failure on {road}. Drive cautiously and obey traffic police instructions.",

    "protest": lambda road, severity, congestion:
        f"Traffic disruption due to a protest on {road}. Use alternate routes and expect delays.",

    "pothole": lambda road, severity, congestion:
        f"Road damage reported on {road}. Reduce speed and drive carefully.",

    "other": lambda road, severity, congestion:
        f"Traffic incident reported on {road}. Please drive carefully."
}


def _template_fallback(road_name, incident_type, severity, congestion_level=None):
    road = road_name or "the reported area"
    congestion = congestion_level or "moderate"

    generator = ACTION_TEMPLATES.get(
        incident_type,
        ACTION_TEMPLATES["other"]
    )

    return generator(
        road,
        severity,
        congestion
    )
def generate_alert(road_name, incident_type, severity, congestion_level=None):
    """Generates a short commuter alert."""
    if TRANSFORMERS_AVAILABLE:
        try:
            tokenizer, model = _load_model()

            prompt = f"""
Generate a traffic alert like the example.

Example:
Road: Anna Salai
Incident: accident
Severity: high
Congestion: heavy

Alert:
Avoid the area, expect delays near Anna Salai. Expected delay: 25 minutes.

Now generate an alert.

Road: {road_name or "Unknown Road"}
Incident: {incident_type}
Severity: {severity}
Congestion: {congestion_level or "moderate"}

Alert:
"""

            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=128
            )

            output_ids = model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=2
            )

            text = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

            road = (road_name or "").lower()

            valid = (
                road in text.lower()
                or incident_type.lower() in text.lower()
                or "delay" in text.lower()
                or "traffic" in text.lower()
            )

            if valid:
                return text

            print("Poor FLAN output, using template.")

        except Exception as e:
            print(f"FLAN-T5 generation failed ({e}); using template fallback.")

    return _template_fallback(
        road_name,
        incident_type,
        severity,
        congestion_level
    )
# ------------------------------------------------------------------
# OPTIONAL: fine-tuning sketch (not run automatically - for students who
# want to go further). Build (prompt, target_alert) pairs from your own
# incident data and fine-tune with HuggingFace's Seq2SeqTrainer, the same
# way as in the bigger smart-city-traffic-system project's
# src/slm/finetune.py reference implementation.
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(generate_alert("Anna Salai", "accident", "high", "high"))
