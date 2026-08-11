import os
import joblib
import pandas as pd

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "saved_models",
    "population_predictor.pkl"
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "india_features_dataset.csv"
)

# ==========================================================
# LOAD MODEL
# ==========================================================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found:\n{MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print("=" * 70)
print("INDIA POPULATION PREDICTOR")
print("=" * 70)

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(DATASET_PATH)

latest = df.iloc[-1].copy()

print("\nLatest Available Year :", int(latest["Year"]))

# ==========================================================
# USER INPUT
# ==========================================================

year = int(input("\nEnter Prediction Year (2026-2050): "))

if year < 2026 or year > 2050:
    print("\nVersion 1 supports predictions only from 2026 to 2050.")
    exit()

# ==========================================================
# PREPARE FEATURES
# ==========================================================

features = latest.copy()

features["Year"] = year

features = features.drop(labels=["Population"])

X = pd.DataFrame([features])

# ==========================================================
# PREDICT
# ==========================================================

prediction = model.predict(X)[0]

print("\n" + "=" * 70)
print("PREDICTION RESULT")
print("=" * 70)

print(f"Prediction Year : {year}")
print(f"Estimated Population : {int(prediction):,}")

print("\nPrediction Completed Successfully!")