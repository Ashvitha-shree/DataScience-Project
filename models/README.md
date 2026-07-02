# Trained Models

- `rf_model.pkl` — trained Random Forest congestion classifier (also auto-saved to
  `backend/ml_module/saved_model/rf_model.pkl` when you run `python -m ml_module.evaluate_model`).
  Achieves ~99.6% accuracy on the held-out test split of the sample dataset.
- `ml_evaluation_plots/` — confusion matrix, ROC curve, and feature importance plots generated
  from training this model.
- `lstm_model.h5` is NOT included here — it requires TensorFlow to train (see
  `backend/dl_module/lstm_model.py`); generate it locally with `python -m dl_module.lstm_model`.
- `slm_model/` (fine-tuned FLAN-T5 checkpoint) is NOT included — the project uses the
  off-the-shelf `google/flan-t5-small` checkpoint from HuggingFace by default (downloaded
  automatically on first use if `transformers`/`torch` are installed), with a templated fallback
  if they are not. See `backend/slm_module/alert_generator.py` for an optional fine-tuning sketch.
