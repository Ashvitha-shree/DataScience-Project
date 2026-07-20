"""
lstm_model.py
Deep Learning module: an LSTM (Long Short-Term Memory) neural network that
predicts traffic conditions ~30 minutes into the future from a sequence of
recent readings.

WHY LSTM (vs Random Forest)?
Random Forest looks at ONE row of data at a time - it has no memory of
what happened 10 minutes ago. Traffic is sequential: speed 10 minutes ago
strongly affects speed now. LSTM is built specifically to remember
patterns across a sequence of past steps, which is what makes it better
suited to short-term traffic forecasting than a plain classifier.
"""
import os
import numpy as np
import pandas as pd

from config import settings

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

SEQ_LEN = 6  # use last 6 readings (e.g. 6 x 5-min intervals = 30 minutes of history)


def build_sequences(df: pd.DataFrame, seq_len=SEQ_LEN):
    """Builds (X, y) sliding-window sequences per road, predicting the next
    avg_speed value from the previous `seq_len` readings."""
    sequences, targets = [], []
    df = df.sort_values(["road_id", "record_date", "record_time"])
    for road_id, group in df.groupby("road_id"):
        speeds = group["avg_speed"].values
        counts = group["vehicle_count"].values
        feats = np.stack([speeds, counts], axis=1)
        for i in range(len(feats) - seq_len):
            sequences.append(feats[i:i + seq_len])
            targets.append(speeds[i + seq_len])
    return np.array(sequences, dtype=np.float32), np.array(targets, dtype=np.float32)


def build_lstm_model(seq_len=SEQ_LEN, n_features=2, units=32):
    if not TF_AVAILABLE:
        raise ImportError("TensorFlow is required. Install with `pip install tensorflow`.")
    model = models.Sequential([
        layers.Input(shape=(seq_len, n_features)),
        layers.LSTM(units, return_sequences=False),
        layers.Dense(16, activation="relu"),
        layers.Dense(1, activation="linear"),
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


def train_lstm(csv_path="dataset/sample_traffic_data.csv", model_path=None, epochs=20):
    """Trains the LSTM and saves it. Returns training history + validation MAE,
    used for the 'Training Loss / Validation Loss' chart on the dashboard."""
    if not TF_AVAILABLE:
        print("TensorFlow not installed - skipping LSTM training.")
        return None

    model_path = model_path or settings.LSTM_MODEL_PATH
    df = pd.read_csv(csv_path)
    X, y = build_sequences(df)

    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    model = build_lstm_model()
    history = model.fit(
        X_train, y_train, validation_data=(X_val, y_val),
        epochs=epochs, batch_size=16, verbose=2,
    )

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model_path = model_path.replace(".h5", ".keras")
    model.save(model_path)
    print(f"LSTM model saved -> {model_path}")
  

    y_pred = model.predict(X_val).flatten()
    val_mae = float(np.mean(np.abs(y_pred - y_val)))

    return {
        "train_loss": history.history["loss"],
        "val_loss": history.history["val_loss"],
        "val_mae": val_mae,
    }


_lstm_cache = None


def load_lstm(model_path=None):
    global _lstm_cache
    if not TF_AVAILABLE:
        raise ImportError("TensorFlow not installed.")
    model_path = model_path or settings.LSTM_MODEL_PATH
    # Support both .keras (new) and .h5 (old) formats
    keras_path = model_path.replace(".h5", ".keras")
    if _lstm_cache is None:
        import os
        if os.path.exists(keras_path):
            _lstm_cache = tf.keras.models.load_model(keras_path)
        elif os.path.exists(model_path):
            _lstm_cache = tf.keras.models.load_model(
                model_path, compile=False
            )
        else:
            raise FileNotFoundError(
                f"No trained LSTM model found. Run: python -m dl_module.lstm_model"
            )
    return _lstm_cache

def predict_next_speed(recent_readings):
    """recent_readings: list of [avg_speed, vehicle_count] for the last
    SEQ_LEN time steps. Returns the predicted speed ~30 minutes ahead."""
    model = load_lstm()
    X = np.array([recent_readings], dtype=np.float32)
    pred = model.predict(X, verbose=0)
    return float(pred[0][0])


if __name__ == "__main__":
    result = train_lstm()
    if result:
        print("Validation MAE:", result["val_mae"])
