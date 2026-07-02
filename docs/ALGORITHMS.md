# Algorithms Used

## 1. Random Forest (Machine Learning)

**What it is:** an ensemble of many Decision Trees, each trained on a random subset of the data
and a random subset of features; the final prediction is a majority vote across all trees.

**Why chosen:** congestion prediction here is a tabular classification problem (a handful of
numeric/categorical features → 3 classes). Random Forest handles this well without needing
feature scaling, resists overfitting better than a single Decision Tree (because errors from
individual trees average out), and gives `feature_importances_` for free — letting us show
*which factors drove the prediction* (e.g. "vehicle count and hour of day mattered most"),
which is a great thing to demonstrate in a viva.

**Inputs (features):** `vehicle_count, avg_speed, hour, day_of_week_num, is_weekend, is_rainy`
**Output:** `congestion_level ∈ {low, medium, high}`, plus a confidence score (max class probability).

**Evaluation metrics shown:** Accuracy, Precision, Recall, F1 Score (all weighted-average across
classes), Confusion Matrix, ROC Curve (one-vs-rest per class), Feature Importance.

## 2. LSTM (Deep Learning)

**What it is:** a recurrent neural network architecture with memory cells designed to learn
patterns across sequences, while avoiding the vanishing-gradient problem that plain RNNs suffer
from over longer sequences.

**Why chosen (vs Random Forest):** Random Forest looks at a single point in time. Traffic speed
30 minutes from now depends heavily on the trend over the last 30 minutes (is it rising or
falling?), not just the current snapshot — that's a sequential pattern, which is exactly what
LSTM is built to learn. We feed it the last 6 readings (speed + vehicle count) per road and ask
it to predict the next speed value.

**Input:** sequence of shape `(6 time steps, 2 features)` per road.
**Output:** a single forecasted `avg_speed` value (regression, not classification).

**Evaluation:** Training Loss / Validation Loss curves over epochs, Validation MAE (Mean
Absolute Error in km/h), and a predicted-vs-actual comparison.

## 3. spaCy NLP Pipeline (NLP)

**What it is:** spaCy provides tokenization, part-of-speech tagging, and a pretrained Named
Entity Recognition (NER) model out of the box. We combine spaCy's generic NER (for general
location/organization entities) with our own gazetteer (known road name list) and keyword
matching (for traffic-specific concepts like incident type and severity, which a generic NER
model has no concept of).

**Pipeline steps for an incident report:**
1. Match against the known road-name gazetteer (exact substring match).
2. If no match, fall back to spaCy's NER for a generic location/facility entity.
3. Keyword-match the text against curated word lists for incident type (accident, roadwork,
   flooding, etc.), severity (low/medium/high/critical), and weather (rain, fog, storm, clear).

This is intentionally simple and explainable rather than a trained custom NER model — a fair
trade-off for a college project where the goal is to demonstrate NLP techniques clearly.

## 4. FLAN-T5 Small (Small Language Model)

**What it is:** an instruction-tuned, encoder-decoder Transformer model with ~80 million
parameters — small enough to run on CPU, but already trained to follow natural-language
instructions (unlike a base/non-instruction-tuned model of similar size).

**Prompt design:** a direct instruction prompt listing the road, incident type, severity, and
current congestion, asking the model to write a short alert with a suggested action. Because
FLAN-T5 was instruction-tuned, this works reasonably well even without further fine-tuning.

**Why an SLM here, not a big LLM:** alert generation is a narrow, repetitive task. A small,
locally-run model is fast, free, and works offline — important for a city system that must keep
functioning without guaranteed internet access. This is a deliberate contrast with the GenAI
module below, which *does* benefit from a larger general-purpose model.

## 5. Generative AI - Scenario Generator

**What it is:** open-ended text generation for realistic "what-if" traffic scenarios. Uses the
OpenAI API (`gpt-4o-mini`) if `OPENAI_API_KEY` is configured, since this is a creative,
open-ended writing task better suited to a larger general-purpose LLM than a small task-specific
model. Falls back to a built-in template-based procedural generator if no API key is set, so the
project always runs offline.

## 6. Agentic AI - Rule-Based Decision Agent

**What it is:** NOT a machine learning model. It's a sequence of simple, explicit if/else rules
that read the outputs of the other modules and decide what to do.

**Workflow:** read prediction → read incident → generate alert (calls the SLM module) →
recommend signal timing (rule table below) → log the decision.

**Signal timing rules:**
| Condition | Decision |
|---|---|
| `incident.severity == "critical"` | Switch to manual police control |
| `congestion == "high"` | Extend green signal by 20 seconds |
| `congestion == "medium"` | Extend green signal by 10 seconds |
| `congestion == "low"` | No signal change needed |

**Why rule-based, not Reinforcement Learning:** RL would require designing a reward function,
running many training episodes in a simulated traffic environment, and tuning exploration vs
exploitation — significant complexity that doesn't add proportional educational value for a
college project, and per the project brief is explicitly out of scope. A rule-based agent is
100% explainable: every decision can be traced back to one exact `if` condition, which is ideal
for a viva.
