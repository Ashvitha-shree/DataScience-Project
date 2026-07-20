"""
bert_classifier.py
Day 5 — BERT Fine-Tuning for Traffic Incident Classification.

STAGE-WISE COMPARISON (explained in report):
  Stage 1: Keyword Matching     (no ML, rule-based baseline)
  Stage 2: spaCy NER            (lightweight NLP model)
  Stage 3: BERT Fine-Tuned      (transformer-based, highest accuracy)

WHY BERT?
BERT (Bidirectional Encoder Representations from Transformers) reads
text in BOTH directions simultaneously, capturing full context.
"signal failed near the road" and "road near the failed signal" have
the same words but different meanings — BERT understands this because
it considers the entire sentence at once, unlike keyword matching which
just looks for individual words.

For traffic incident classification, BERT understands nuanced phrases
like "slow moving vehicles" (congestion, not accident) vs "vehicles
stopped" (possible accident/breakdown) — context that keyword lists miss.

This module uses bert-base-uncased (~110M params) fine-tuned on
our synthetic incident dataset for 7-class classification:
  accident, roadwork, breakdown, flooding, protest, signal_failure, other

DEPENDENCIES: transformers, torch (pip install transformers torch)
Falls back to keyword matching if not installed.
"""
import os
import json
import random

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import (
        BertTokenizer,
        BertForSequenceClassification,
        AdamW,
        get_linear_schedule_with_warmup,
    )
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False

# Label mapping
INCIDENT_LABELS = [
    "accident", "roadwork", "breakdown",
    "flooding", "protest", "signal_failure", "other"
]
LABEL2ID = {l: i for i, l in enumerate(INCIDENT_LABELS)}
ID2LABEL = {i: l for l, i in LABEL2ID.items()}

MODEL_NAME  = "bert-base-uncased"
MODEL_DIR   = "nlp_module/saved_bert_model"
MAX_LENGTH  = 64


# ── Training Dataset ──────────────────────────────────────────────────────────
class IncidentDataset(Dataset):
    """PyTorch Dataset wrapping tokenised incident texts."""

    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels":         self.labels[idx],
        }


# ── Build Fine-Tuning Data from Incident Reports ─────────────────────────────
def load_incidents_for_bert(incidents_path="data/raw/incident_reports.json"):
    """Loads incident reports and converts to (text, label_id) pairs."""
    if not os.path.exists(incidents_path):
        # Fallback: generate synthetic training sentences
        return _generate_synthetic_training_data()

    with open(incidents_path) as f:
        reports = json.load(f)

    texts, labels = [], []
    for r in reports:
        label = r.get("incident_type", "other")
        if label not in LABEL2ID:
            label = "other"
        texts.append(r["report_text"])
        labels.append(LABEL2ID[label])
    return texts, labels


def _generate_synthetic_training_data():
    """Generates synthetic training sentences when no JSON file exists,
    so the module always runs even before data generation."""
    templates = {
        "accident":       [
            "Accident near {road}, lane blocked.",
            "Collision on {road} due to heavy rain.",
            "Multi-vehicle crash on {road}, road blocked.",
            "Minor accident near {road}, slow traffic.",
            "Vehicle crash near {road}, emergency services on site.",
        ],
        "roadwork":       [
            "Road maintenance work on {road}, one lane closed.",
            "Construction crew on {road}, expect delays.",
            "Pothole repair on {road}, traffic slow.",
        ],
        "breakdown":      [
            "Truck breakdown on {road} blocking lane.",
            "Bus broke down near {road}, tow truck en route.",
            "Vehicle stalled on {road}, minor disruption.",
        ],
        "flooding":       [
            "Waterlogging on {road} after heavy rain.",
            "Flooding near {road}, road impassable.",
            "Severe flood on {road} after monsoon.",
        ],
        "protest":        [
            "Rally on {road} causing road closure.",
            "Public protest near {road}, traffic diverted.",
            "Political march on {road}, major delays.",
        ],
        "signal_failure": [
            "Signal malfunction at {road} junction.",
            "Traffic light outage on {road}.",
            "Signal failure near {road}, police managing.",
        ],
        "other":          [
            "Dense fog on {road}, poor visibility.",
            "Strong winds causing disruption on {road}.",
            "Debris on {road} slowing traffic.",
        ],
    }
    roads = ["MG Road", "Anna Salai", "OMR", "ECR", "GST Road",
             "Mount Road", "Velachery Main Road"]
    texts, labels = [], []
    for label, tmpl_list in templates.items():
        for tmpl in tmpl_list:
            for road in roads:
                texts.append(tmpl.format(road=road))
                labels.append(LABEL2ID[label])
    # Shuffle
    combined = list(zip(texts, labels))
    random.seed(42)
    random.shuffle(combined)
    texts, labels = zip(*combined)
    return list(texts), list(labels)


# ── Fine-Tuning ───────────────────────────────────────────────────────────────
def finetune_bert(epochs=3, batch_size=8, out_dir=MODEL_DIR):
    """Fine-tunes BERT for incident type classification.
    Saves tokenizer + model to out_dir for later inference."""

    if not BERT_AVAILABLE:
        print("transformers/torch not installed. "
              "Run: pip install transformers torch")
        return None

    texts, labels = load_incidents_for_bert()
    split = int(len(texts) * 0.85)
    train_texts, val_texts   = texts[:split], texts[split:]
    train_labels, val_labels = labels[:split], labels[split:]

    tokenizer  = BertTokenizer.from_pretrained(MODEL_NAME)
    train_ds   = IncidentDataset(train_texts, train_labels, tokenizer)
    val_ds     = IncidentDataset(val_texts,   val_labels,   tokenizer)
    train_dl   = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_dl     = DataLoader(val_ds,   batch_size=batch_size)

    model = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(INCIDENT_LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    total_steps = len(train_dl) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Training on: {device}")

    history = {"train_loss": [], "val_acc": []}

    for epoch in range(epochs):
        # Training
        model.train()
        total_loss = 0
        for batch in train_dl:
            optimizer.zero_grad()
            outputs = model(
                input_ids      = batch["input_ids"].to(device),
                attention_mask = batch["attention_mask"].to(device),
                labels         = batch["labels"].to(device),
            )
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_dl)
        history["train_loss"].append(avg_loss)

        # Validation
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for batch in val_dl:
                outputs = model(
                    input_ids      = batch["input_ids"].to(device),
                    attention_mask = batch["attention_mask"].to(device),
                )
                preds   = outputs.logits.argmax(dim=-1)
                correct += (preds == batch["labels"].to(device)).sum().item()
                total   += len(batch["labels"])

        val_acc = correct / total
        history["val_acc"].append(val_acc)
        print(f"Epoch {epoch+1}/{epochs} | "
              f"Loss: {avg_loss:.4f} | Val Accuracy: {val_acc:.4f}")

    os.makedirs(out_dir, exist_ok=True)
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    print(f"\nFine-tuned BERT saved → {out_dir}")

    return {"history": history, "val_acc": history["val_acc"][-1]}


# ── Inference ─────────────────────────────────────────────────────────────────
_bert_cache  = None
_token_cache = None


def classify_incident_bert(text):
    """Classifies a single incident report text using the fine-tuned BERT model.
    Falls back to keyword matching if the model is not trained yet."""
    global _bert_cache, _token_cache

    if not BERT_AVAILABLE or not os.path.exists(
            os.path.join(MODEL_DIR, "config.json")):
        # Graceful fallback
        from nlp_module.incident_extractor import extract_incident_type
        return {
            "label":      extract_incident_type(text),
            "confidence": None,
            "method":     "keyword_fallback",
        }

    if _bert_cache is None:
        _token_cache = BertTokenizer.from_pretrained(MODEL_DIR)
        _bert_cache  = BertForSequenceClassification.from_pretrained(MODEL_DIR)
        _bert_cache.eval()

    inputs = _token_cache(
        text, return_tensors="pt",
        truncation=True, max_length=MAX_LENGTH, padding="max_length"
    )
    with torch.no_grad():
        logits = _bert_cache(**inputs).logits
    probs     = torch.softmax(logits, dim=-1)[0]
    label_id  = probs.argmax().item()

    return {
        "label":      ID2LABEL[label_id],
        "confidence": round(float(probs[label_id]), 4),
        "method":     "bert_finetuned",
        "all_scores": {ID2LABEL[i]: round(float(p), 4)
                       for i, p in enumerate(probs)},
    }


# ── Stage-wise Comparison ─────────────────────────────────────────────────────
def stage_wise_comparison(text):
    """Runs the same incident text through all three stages and returns
    a comparison dict — used in the dashboard and viva demonstration."""
    from nlp_module.incident_extractor import (
        extract_incident_type, extract_severity, extract_weather, extract_road
    )

    stage1 = {
        "stage":  "Stage 1 — Keyword Matching",
        "method": "rule_based",
        "label":  extract_incident_type(text),
        "confidence": "N/A",
        "notes":  "Fast, no model needed, but misses context and nuance",
    }

    stage2 = {
        "stage":  "Stage 2 — spaCy NER",
        "method": "spacy",
        "label":  extract_incident_type(text),   # same function, spaCy helps road extraction
        "road":   extract_road(text),
        "confidence": "N/A",
        "notes":  "Adds entity recognition for road names, still keyword-based for type",
    }

    stage3 = classify_incident_bert(text)
    stage3["stage"] = "Stage 3 — BERT Fine-Tuned"
    stage3["notes"] = ("Full contextual understanding, highest accuracy, "
                       "requires transformers/torch")

    return {"text": text, "stages": [stage1, stage2, stage3]}


if __name__ == "__main__":
    sample = "Accident near Anna Salai due to heavy rain, road blocked."
    print("\n=== Stage-wise Comparison ===")
    result = stage_wise_comparison(sample)
    for s in result["stages"]:
        print(f"\n{s['stage']}: {s.get('label','N/A')} "
              f"(confidence: {s.get('confidence','N/A')})")
        print(f"  Notes: {s['notes']}")

    print("\n=== Fine-tuning BERT ===")
    finetune_bert(epochs=2)
