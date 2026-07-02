# Possible Viva Questions and Model Answers

## General / Architecture

**Q: Walk me through what happens when a traffic officer submits an incident report.**
A: The frontend sends `POST /incidents` with the raw text. The route calls
`nlp_module.analyze_incident()`, which matches the text against a known-road gazetteer and
keyword lists to extract road name, incident type, severity, and weather. The extracted fields
plus the original text are saved to the `Incidents` table and returned to the frontend, which
immediately shows them in the incidents table.

**Q: Why did you split this into so many modules instead of one big script?**
A: Each AI technique solves a different kind of problem (tabular classification, sequence
forecasting, text understanding, text generation, decision logic), so keeping them in separate
modules with clear inputs/outputs makes each one independently testable, explainable, and
replaceable without affecting the others.

**Q: What happens if MySQL isn't running?**
A: The FastAPI routes that need the database will fail with a connection error returned as an
HTTP 500. The AI modules themselves (`ml_module`, `nlp_module`, etc.) don't depend on the
database directly — they can be run and tested standalone via their `if __name__ == "__main__":`
blocks even without MySQL running.

## Machine Learning

**Q: Why Random Forest instead of Logistic Regression or SVM?**
A: Random Forest handles non-linear relationships between features (e.g. the interaction between
rush hour and rainfall) without manual feature engineering, doesn't require feature scaling, and
gives feature importance scores — useful both for debugging and for explaining results.
Logistic Regression assumes a more linear decision boundary, which may underfit this data.

**Q: What is the confusion matrix telling you?**
A: It shows how many records of each true class were predicted as each class — the diagonal is
correct predictions, off-diagonal cells show specific types of mistakes (e.g. "medium" predicted
as "high"). It's a more detailed view than accuracy alone.

**Q: What's the difference between precision and recall here?**
A: Precision for "high congestion" = of all the times the model predicted high congestion, how
often was it actually high? Recall = of all the actually high-congestion records, how many did
the model correctly catch? In a traffic system, recall on "high" congestion matters more (you'd
rather over-warn than miss a real jam), which is why we used `class_weight="balanced"` during
training.

**Q: How would you improve this model's accuracy further?**
A: Add more historical features (e.g. recent trend, nearby road congestion, public holidays),
tune hyperparameters (`n_estimators`, `max_depth`) via cross-validation, or try gradient
boosting (XGBoost/LightGBM) as a stronger alternative ensemble method.

## Deep Learning

**Q: Why LSTM and not a simple moving average for forecasting?**
A: A moving average just extrapolates a single trend and ignores other recent context (like
vehicle count alongside speed). LSTM can learn more complex, non-linear temporal patterns from
multiple input features simultaneously.

**Q: What does "sequence length 6" mean here?**
A: The model looks at the 6 most recent traffic readings for a road (vehicle count + speed) to
predict the next speed value — effectively using the recent trend, not just the latest snapshot.

**Q: Why not use LSTM for the classification task instead of Random Forest?**
A: LSTM is suited to sequential/temporal prediction; for a single-point-in-time classification
task with no sequence dependency, a simpler tabular model like Random Forest is faster to train,
easier to explain, and performs just as well or better, with the added benefit of feature
importance.

## NLP

**Q: How does the system know "Anna Salai" is a road and not just random text?**
A: We maintain a gazetteer (a fixed list of known road names) and check whether any of them
appear as a substring in the report text. If spaCy is installed, we additionally fall back to
its generic Named Entity Recognition for location-like entities not in our list.

**Q: What if spaCy isn't installed on the demo machine?**
A: The module checks for spaCy at import time; if unavailable, it silently skips that fallback
step and still works using gazetteer + keyword matching alone — output quality is slightly
reduced (less robust to unknown road names) but the system doesn't crash.

**Q: Could you train a custom NER model instead?**
A: Yes — you'd label a dataset of incident reports with road-name spans and fine-tune spaCy's
NER component on it. We chose the simpler gazetteer approach for this project given the limited
and known set of roads being monitored.

## SLM

**Q: Why FLAN-T5 Small specifically?**
A: It's instruction-tuned (responds well to natural-language task prompts without needing
fine-tuning first), small enough (~80M parameters) to run on a laptop CPU quickly, and free/open
to use locally without API costs — appropriate for a task this narrow.

**Q: What's the difference between an SLM and an LLM in this project?**
A: The SLM (FLAN-T5 Small) handles one narrow, repetitive task: turning structured fields into a
short alert. The GenAI module instead uses a full LLM (via OpenAI API) for open-ended creative
scenario writing, which benefits from a larger model's broader knowledge and fluency. Using the
right-sized model for each job is a deliberate design decision.

**Q: How would you fine-tune the SLM for better results?**
A: Collect a set of (incident details → ideal human-written alert) pairs, then fine-tune using
HuggingFace's `Seq2SeqTrainer` with a sequence-to-sequence loss, similar to the sketch left as a
comment in `slm_module/alert_generator.py`.

## Generative AI

**Q: What happens if there's no OpenAI API key configured?**
A: The module checks for `OPENAI_API_KEY` in the environment; if absent (or if the API call
fails for any reason), it falls back to a built-in procedural generator that fills in sentence
templates with randomized road names, percentages, and time windows — still produces a
reasonably realistic scenario, just less varied than an LLM's output.

**Q: Why not use FLAN-T5 Small for scenario generation too?**
A: Scenario generation is open-ended creative writing requiring broader world knowledge and
fluency than a small instruction-tuned model typically provides; a larger general-purpose LLM
produces noticeably more varied and realistic scenarios for this kind of task.

## Agentic AI

**Q: Is this "agent" actually AI, since it's just if/else rules?**
A: It fits the basic definition of an agent — it perceives its environment (reads predictions
and incidents), reasons about what to do (applies decision rules), and acts (generates alerts,
recommends signal changes, logs decisions) — without needing a human to manually trigger each
step. The "intelligence" here is in how it orchestrates the other AI modules, not in the
decision rule complexity itself, which is intentionally kept simple and explainable per the
project brief.

**Q: Why didn't you use Reinforcement Learning for the agent?**
A: RL would require a simulated environment, a carefully designed reward function, and many
training episodes — significant added complexity without proportional benefit for a college
project where transparency and explainability of every decision matters more than optimality.

**Q: How would you extend this to actually learn over time?**
A: You could log outcomes after each agent decision (e.g. did congestion improve in the next
reading?) and periodically adjust the rule thresholds based on a simple moving-average of
recent outcomes — a lightweight "adaptive" layer short of full RL, keeping the core logic
explainable while still improving over time.

## Database / Backend

**Q: Why MySQL instead of a NoSQL database?**
A: The data here is naturally relational — roads have many traffic records, incidents relate to
roads and produce alerts, agent logs reference predictions and incidents. Foreign keys and joins
map cleanly onto this structure, and MySQL is a standard, well-understood choice for this kind
of structured, relationship-heavy data.

**Q: How is authentication handled?**
A: Passwords are hashed with PBKDF2-HMAC-SHA256 with a random salt (never stored in plain text).
On login, the server issues a JWT access token containing the user ID and role, which the
frontend stores and sends in the `Authorization` header on every subsequent request; the
`get_current_user` FastAPI dependency validates and decodes it on each protected route.

**Q: What would you change before deploying this to production?**
A: Add HTTPS, move secrets out of `.env` into a proper secrets manager, add rate limiting,
restrict CORS to the real frontend domain, add database connection pooling tuning, add
structured logging/monitoring, and add automated tests (none are included here, kept out of
scope for this project's submission).
