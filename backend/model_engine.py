import os
import pandas as pd
import joblib

# Import the class from our core module
from backend.core_model import HybridPopulationForecaster

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURE_DATASET = os.path.join(BASE_DIR, "dataset", "india_features_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

def main():
    if not os.path.exists(FEATURE_DATASET):
        raise FileNotFoundError(f"Run preprocess.py first.")
        
    df = pd.read_csv(FEATURE_DATASET)
    
    forecaster = HybridPopulationForecaster()
    
    # Extract training logic inline
    X_years = df[["Year"]].values
    y_pop = df["Population"].values
    forecaster.feature_cols = [
        'Birth_Rate', 'Death_Rate', 'Fertility_Rate', 'GDP_Growth', 
        'Life_Expectancy', 'Urban_Population', 'Rural_Population', 'Birth_Death_Ratio'
    ]
    
    forecaster.trend_model.fit(X_years, y_pop)
    trend_preds = forecaster.trend_model.predict(X_years)
    residuals = y_pop - trend_preds
    
    X_features_scaled = forecaster.scaler.fit_transform(df[forecaster.feature_cols])
    forecaster.residual_model.fit(X_features_scaled, residuals)
    
    # Export clean serialized structure 
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_checkpoint_path = os.path.join(MODEL_DIR, "hybrid_population_model.pkl")
    joblib.dump(forecaster, model_checkpoint_path)
    print(f"✅ Model re-exported cleanly via module namespaces to: {model_checkpoint_path}")

if __name__ == "__main__":
    main()