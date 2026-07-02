# Project Report

## Title
AI-Based Smart City Traffic Management and Optimization System

## Abstract

Urban traffic congestion is a growing problem in fast-growing cities, leading to wasted time,
fuel, and increased pollution. This project presents a Smart City Traffic Management System
that combines six AI/ML techniques — classical Machine Learning, Deep Learning, Natural
Language Processing, a Small Language Model, Generative AI, and a rule-based Agentic AI layer —
into a single, full-stack web application. The system predicts road congestion levels, analyzes
free-text incident reports, generates commuter alerts automatically, simulates realistic traffic
scenarios for planning, and recommends signal-timing adjustments, all surfaced through a modern
React dashboard backed by a FastAPI service and a MySQL database.

## Purpose

To demonstrate, in a single coherent project, how multiple categories of AI techniques can be
combined to solve a real-world urban problem — while keeping every individual technique simple
enough to implement, test, and explain within the scope of a final-year engineering project.

## Working (System Summary)

1. Traffic sensor data (vehicle count, average speed, weather, time) is collected per road and
   stored in MySQL.
2. A Random Forest classifier, trained on this historical data, predicts whether a given
   reading represents low, medium, or high congestion.
3. An LSTM neural network looks at a short sequence of recent readings to forecast traffic speed
   roughly 30 minutes ahead.
4. Citizens/officers submit free-text incident reports; spaCy-based NLP extracts the road name,
   incident type, severity, and weather automatically.
5. A small fine-tunable language model (FLAN-T5 Small) converts structured incident/prediction
   data into a short, human-readable commuter alert.
6. A Generative AI module produces realistic hypothetical traffic scenarios (flood, festival,
   road closure, political rally, accident, emergency) for testing and city planning.
7. A simple rule-based agent ties all of the above together: it reads predictions and incidents,
   triggers alert generation, recommends a signal-timing change, and logs every decision with
   its reasoning for accountability.
8. Admins/officers interact with all of this through a responsive React dashboard, and can
   export Daily/Weekly/Monthly PDF reports summarizing system activity.

## Algorithms Used

See `ALGORITHMS.md` for full detail. Summary: Random Forest (ML), LSTM (DL), spaCy NER +
keyword matching (NLP), FLAN-T5 Small (SLM), LLM-based or procedural generation (GenAI), and
explicit rule tables (Agentic AI).

## Advantages

- **Modular design** — every AI technique is isolated in its own module, making the system easy
  to extend, test, or explain piece by piece.
- **Works offline** — every optional heavy dependency (TensorFlow, spaCy's model, Transformers,
  an LLM API key) has a graceful fallback, so the system is always demoable.
- **End-to-end and full-stack** — covers data storage, ML/DL training and inference, NLP, text
  generation, decision automation, a REST API, and a modern frontend — a complete demonstration
  of full-stack + AI engineering skills.
- **Explainable by design** — especially the Agentic AI layer, which uses transparent rules
  rather than a black-box model, making every automated decision traceable and defensible.

## Limitations

- The Random Forest and LSTM models are trained on synthetically generated sample data, not
  real sensor data from an actual city — predictions are realistic in pattern but not validated
  against ground truth.
- The Agentic AI module uses fixed rule thresholds rather than learning optimal thresholds from
  outcomes (a deliberate simplification — see `ALGORITHMS.md` for the reasoning).
- The NLP module's road-name recognition relies on a fixed gazetteer list, so it will not
  recognize roads outside the seeded dataset without manual updates.
- The system is built for demonstration/college-project scale, not production-scale traffic
  volumes (no load testing, caching layer, or horizontal scaling has been implemented).

## Future Scope

- Replace synthetic training data with real traffic sensor / GPS probe data from an actual
  traffic authority, if available.
- Fine-tune FLAN-T5 Small on a larger set of (incident → ideal alert) pairs for more natural
  alert phrasing.
- Extend the Agentic AI module with a learning component (e.g. adjust signal-timing thresholds
  based on observed outcomes over time) while keeping a human-in-the-loop approval step for any
  high-impact action.
- Add SMS/push notification delivery for generated alerts.
- Add a heatmap visualization layer on the map for live congestion intensity across the city.
- Expand the spaCy NLP pipeline with a custom-trained NER model for broader road-name coverage.

## Conclusion

This project demonstrates a practical, explainable, and fully working application of six
different AI/ML paradigms to a single real-world problem domain, built with a production-style
tech stack (React, FastAPI, MySQL) while remaining appropriately scoped and explainable for a
final-year college submission.
