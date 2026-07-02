"""
random_forest_model.py
Machine Learning module: trains and serves a Random Forest classifier that
predicts congestion_level (low/medium/high) from traffic features.

WHY RANDOM FOREST?
- Works well on small/medium tabular datasets (typical for a college project).
- Handles a mix of numeric features without needing heavy scaling.
- Gives feature_importances_ for free, which is great for explaining
  "what factors matter most" during a viva.
- Much less prone to overfitting than a single Decision Tree, because it
  averages many trees trained on random subsets of data/features.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc,
)
from sklearn.preprocessing import label_binarize

from config import settings

FEATURE_COLUMNS = [
    "vehicle_count", "avg_speed", "hour", "day_of_week_num", "is_weekend", "is_rainy",
]
LABELS = ["low", "medium", "high"]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Turns raw TrafficData rows into model-ready numeric features."""
    df = df.copy()
    df["hour"] = pd.to_datetime(df["record_time"].astype(str), format="%H:%M:%S").dt.hour
    dow_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
               "friday": 4, "saturday": 5, "sunday": 6}
    df["day_of_week_num"] = df["day_of_week"].str.lower().map(dow_map).fillna(0).astype(int)
    df["is_weekend"] = df["day_of_week_num"].isin([5, 6]).astype(int)
    df["is_rainy"] = df["weather"].str.lower().str.contains("rain", na=False).astype(int)
    return df


def train_random_forest(csv_path="dataset/sample_traffic_data.csv",
                         model_path=None, test_size=0.2):
    """Trains the Random Forest model on labelled traffic data and saves it.
    Returns a dict of evaluation metrics for the dashboard / viva report."""
    model_path = model_path or settings.RF_MODEL_PATH
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["congestion_level"])  # need labels to train
    df = engineer_features(df)

    X = df[FEATURE_COLUMNS]
    y = df["congestion_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=10, min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=model.classes_).tolist(),
        "classes": model.classes_.tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "feature_importance": dict(zip(FEATURE_COLUMNS, model.feature_importances_.round(4).tolist())),
        "roc_curve": _compute_roc(y_test, y_proba, model.classes_),
    }

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"model": model, "feature_columns": FEATURE_COLUMNS}, model_path)

    return metrics


def _compute_roc(y_test, y_proba, classes):
    """One-vs-rest ROC curve per class - simple to explain: 'for each class,
    treat it as positive vs all others, then plot true positive rate vs
    false positive rate as the decision threshold changes'."""
    y_bin = label_binarize(y_test, classes=classes)
    roc_data = {}
    for i, cls in enumerate(classes):
        if y_bin.shape[1] == 1:  # binary edge case
            fpr, tpr, _ = roc_curve(y_bin[:, 0], y_proba[:, i])
        else:
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
        roc_data[cls] = {
            "fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": round(float(auc(fpr, tpr)), 4)
        }
    return roc_data


_loaded_model_cache = None


def load_model(model_path=None):
    global _loaded_model_cache
    model_path = model_path or settings.RF_MODEL_PATH
    if _loaded_model_cache is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"No trained model found at {model_path}. Run train_random_forest() first."
            )
        _loaded_model_cache = joblib.load(model_path)
    return _loaded_model_cache


def predict_congestion(vehicle_count, avg_speed, record_time, day_of_week, weather):
    """Predicts congestion level for a single traffic record. Used by the
    /prediction API endpoint."""
    bundle = load_model()
    model, feature_columns = bundle["model"], bundle["feature_columns"]

    df = pd.DataFrame([{
        "vehicle_count": vehicle_count, "avg_speed": avg_speed,
        "record_time": record_time, "day_of_week": day_of_week, "weather": weather,
    }])
    df = engineer_features(df)
    X = df[feature_columns]

    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    confidence = float(max(proba))
    return pred, confidence


if __name__ == "__main__":
    metrics = train_random_forest()
    print("Accuracy:", metrics["accuracy"])
    print("F1 Score:", metrics["f1_score"])
