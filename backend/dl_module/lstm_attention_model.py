"""
lstm_attention_model.py
Day 4 — LSTM with Attention Mechanism for Traffic Speed Forecasting.

WHY ATTENTION ON TOP OF LSTM?
A plain LSTM gives equal weight to all 6 time steps in the sequence.
But in traffic forecasting, the most recent readings matter MORE than
older ones — the speed 5 minutes ago is more relevant than the speed
25 minutes ago. The Attention mechanism learns WHICH time steps to focus
on, producing a weighted context vector before making the final prediction.

ARCHITECTURE:
  Input(6, 2)
     │
  LSTM(64, return_sequences=True)   ← keeps ALL 6 step outputs
     │
  Attention Layer                    ← learns which steps matter most
  (dot-product self-attention)
     │
  Context Vector (weighted sum)
     │
  Dense(32, relu)
     │
  Dense(1, linear)                   ← predicted speed
"""
import os
import numpy as np
import pandas as pd

from config import settings

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, Model
    from tensorflow.keras.callbacks import EarlyStopping
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

SEQ_LEN = 6


# ── Attention Layer ───────────────────────────────────────────────────────────
class BahdanauAttention(layers.Layer):
    """Simple additive (Bahdanau-style) attention.
    Computes a context vector as a weighted sum of LSTM step outputs,
    where weights are learned based on each step's relevance."""

    def __init__(self, units=32, **kwargs):
        super().__init__(**kwargs)
        self.W = layers.Dense(units)
        self.V = layers.Dense(1)

    def call(self, lstm_output):
        # lstm_output: (batch, seq_len, hidden_size)
        score = self.V(tf.nn.tanh(self.W(lstm_output)))  # (batch, seq_len, 1)
        weights = tf.nn.softmax(score, axis=1)           # (batch, seq_len, 1)
        context = weights * lstm_output                  # (batch, seq_len, hidden)
        context = tf.reduce_sum(context, axis=1)         # (batch, hidden)
        return context, weights


# ── Model Builder ─────────────────────────────────────────────────────────────
def build_lstm_attention_model(seq_len=SEQ_LEN, n_features=2,
                                lstm_units=64, attention_units=32):
    """Builds the LSTM + Attention model using the Keras Functional API."""
    if not TF_AVAILABLE:
        raise ImportError("TensorFlow required. pip install tensorflow")

    inputs = tf.keras.Input(shape=(seq_len, n_features), name="sequence_input")

    # LSTM returns all step outputs (return_sequences=True)
    lstm_out = layers.LSTM(lstm_units, return_sequences=True,
                            name="lstm_layer")(inputs)
    lstm_out = layers.Dropout(0.2)(lstm_out)

    # Attention: learn which time steps matter most
    attention = BahdanauAttention(units=attention_units, name="attention")
    context, attention_weights = attention(lstm_out)

    # Prediction head
    dense = layers.Dense(32, activation="relu", name="dense_1")(context)
    output = layers.Dense(1, activation="linear", name="speed_output")(dense)

    model = Model(inputs=inputs, outputs=output,
                  name="LSTM_Attention_Traffic_Forecaster")
    model.compile(optimizer="adam", loss="mse")
    return model


# ── Sequence Builder (same as lstm_model.py) ─────────────────────────────────
def build_sequences(df, seq_len=SEQ_LEN):
    sequences, targets = [], []
    df = df.sort_values(["road_id", "record_date", "record_time"])
    for road_id, group in df.groupby("road_id"):
        speeds  = group["avg_speed"].values
        counts  = group["vehicle_count"].values
        feats   = np.stack([speeds, counts], axis=1)
        for i in range(len(feats) - seq_len):
            sequences.append(feats[i:i + seq_len])
            targets.append(speeds[i + seq_len])
    return (np.array(sequences, dtype=np.float32),
            np.array(targets,   dtype=np.float32))


# ── Training ──────────────────────────────────────────────────────────────────
def train_lstm_attention(csv_path="dataset/sample_traffic_data.csv",
                          model_path=None, epochs=25):
    if not TF_AVAILABLE:
        print("TensorFlow not installed — skipping LSTM+Attention training.")
        return None

    model_path = model_path or os.path.join(
        settings.LSTM_MODEL_PATH.replace("lstm_model.h5", ""),
        "lstm_attention_model.keras"
    )

    df  = pd.read_csv(csv_path)
    X, y = build_sequences(df)

    split    = int(len(X) * 0.8)
    X_train  = X[:split];  X_val  = X[split:]
    y_train  = y[:split];  y_val  = y[split:]

    model = build_lstm_attention_model()
    model.summary()

    early_stop = EarlyStopping(patience=5, restore_best_weights=True,
                                monitor="val_loss")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=16,
        callbacks=[early_stop],
        verbose=2,
    )

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)

    y_pred    = model.predict(X_val, verbose=0).flatten()
    val_mae   = float(np.mean(np.abs(y_pred - y_val)))
    base_mae  = float(np.mean(np.abs(y_val - np.mean(y_train))))

    print(f"\nLSTM+Attention Validation MAE : {val_mae:.3f} km/h")
    print(f"Baseline (mean) MAE           : {base_mae:.3f} km/h")
    print(f"Model saved → {model_path}")

    return {
        "train_loss" : history.history["loss"],
        "val_loss"   : history.history["val_loss"],
        "val_mae"    : val_mae,
        "baseline_mae": base_mae,
        "model_path" : model_path,
    }


# ── Single Prediction ─────────────────────────────────────────────────────────
_attn_cache = None


def predict_with_attention(recent_readings, model_path=None):
    """Predicts next speed AND returns per-step attention weights
    so we can show WHICH past reading the model focused on most."""
    global _attn_cache
    if not TF_AVAILABLE:
        raise ImportError("TensorFlow not installed.")

    model_path = model_path or os.path.join(
        os.path.dirname(settings.LSTM_MODEL_PATH),
        "lstm_attention_model.keras"
    )
    if _attn_cache is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Attention model not found at {model_path}. "
                "Run train_lstm_attention() first."
            )
        _attn_cache = tf.keras.models.load_model(
            model_path,
            custom_objects={"BahdanauAttention": BahdanauAttention}
        )

    X = np.array([recent_readings], dtype=np.float32)

    # Build an intermediate model to also expose attention weights
    attn_layer  = _attn_cache.get_layer("attention")
    lstm_layer  = _attn_cache.get_layer("lstm_layer")

    intermediate = Model(
        inputs=_attn_cache.input,
        outputs=[_attn_cache.output,
                 attn_layer(lstm_layer(_attn_cache.input))[1]]
    )
    predicted_speed, attn_weights = intermediate.predict(X, verbose=0)

    return {
        "predicted_speed": float(predicted_speed[0][0]),
        "attention_weights": attn_weights[0, :, 0].tolist(),
        "most_attended_step": int(np.argmax(attn_weights[0, :, 0])),
    }


if __name__ == "__main__":
    result = train_lstm_attention()
    if result:
        print(f"Final VAL MAE: {result['val_mae']:.3f} km/h")
