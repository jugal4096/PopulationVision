
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

FEATURE_DATASET = os.path.join(
    DATASET_DIR,
    "india_features_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# OUTPUT FILES
# ============================================================

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "population_forecast_model.pkl"
)

FEATURE_FILE = os.path.join(
    MODEL_DIR,
    "forecast_model_features.csv"
)

RESULTS_FILE = os.path.join(
    MODEL_DIR,
    "time_series_model_results.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    if not os.path.exists(FEATURE_DATASET):
        raise FileNotFoundError(
            f"\nFeature dataset not found:\n"
            f"{FEATURE_DATASET}"
        )

    df = pd.read_csv(
        FEATURE_DATASET
    )

    df = df.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    print("=" * 70)
    print("INDIA POPULATION FORECASTING")
    print("=" * 70)

    print("\nFeature dataset loaded successfully.")
    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print(
        f"Year range: "
        f"{int(df['Year'].min())} - "
        f"{int(df['Year'].max())}"
    )

    return df


# ============================================================
# CREATE TARGET
# ============================================================

def create_target(df):

    # Population change from previous year
    df["Population_Diff"] = (
        df["Population"].diff()
    )

    # First row cannot have a previous year
    df = df.dropna(
        subset=["Population_Diff"]
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# FORECAST-SAFE FEATURES
# ============================================================

def get_features(df):

    """
    These features are allowed because they represent
    information known before predicting the next population.

    IMPORTANT:
    Current-year population-derived target information is
    deliberately excluded.
    """

    features = [

        # Time trend
        "Year",

        # Previous population information
        "Prev_Population",
        "Population_Lag_2",
        "Population_Lag_3",
        "Population_MA3",

        # Previous demographic information
        "Birth_Rate_Lag_1",
        "Death_Rate_Lag_1",
        "Fertility_Rate_Lag_1",
        "Life_Expectancy_Lag_1",

        # Previous economic information
        "GDP_Growth_Lag_1",

        # Previous migration
        "Net_Migration_Lag_1",

        # Previous literacy
        "Literacy_Rate_Lag_1",

        # Previous urbanization
        "Urban_Population_Lag_1",

        # Previous mortality
        "Infant_Mortality_Lag_1",

        # Previous population density
        "Population_Density_Lag_1"
    ]

    # Keep only columns that actually exist
    features = [
        feature
        for feature in features
        if feature in df.columns
    ]

    if not features:
        raise ValueError(
            "No valid forecast-safe features were found."
        )

    print("\n" + "=" * 70)
    print("FORECAST-SAFE FEATURES")
    print("=" * 70)

    print(
        f"\nNumber of model features: "
        f"{len(features)}"
    )

    for feature in features:
        print(f"✓ {feature}")

    return features


# ============================================================
# VALIDATE FEATURES
# ============================================================

def validate_features(df, features):

    X = df[features].copy()

    # Replace infinite values
    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # We do NOT silently fabricate missing historical data.
    if X.isnull().any().any():

        missing = X.columns[
            X.isnull().any()
        ].tolist()

        raise ValueError(
            "\nMissing values detected in model features:\n"
            + "\n".join(
                f" - {column}"
                for column in missing
            )
            + "\n\nFix the feature-generation pipeline "
              "before training."
        )

    return X


# ============================================================
# MODELS
# ============================================================

def get_models():

    return {

        "Linear Regression":
            LinearRegression(),

        "Random Forest":
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1
            ),

        "Gradient Boosting":
            GradientBoostingRegressor(
                n_estimators=150,
                random_state=42
            )
    }


# ============================================================
# TIME-SERIES EVALUATION
# ============================================================

def evaluate_model(
    model_name,
    model,
    X,
    y,
    population,
    years
):

    tscv = TimeSeriesSplit(
        n_splits=5
    )

    mae_scores = []
    rmse_scores = []
    r2_scores = []
    percentage_errors = []

    print("\n" + "-" * 70)
    print(f"Evaluating: {model_name}")
    print("-" * 70)

    for fold, (
        train_idx,
        test_idx
    ) in enumerate(
        tscv.split(X),
        start=1
    ):

        X_train = X.iloc[
            train_idx
        ]

        X_test = X.iloc[
            test_idx
        ]

        y_train = y.iloc[
            train_idx
        ]

        y_test = y.iloc[
            test_idx
        ]

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        model.fit(
            X_train,
            y_train
        )

        # ----------------------------------------------------
        # Predict yearly population change
        # ----------------------------------------------------

        predicted_change = model.predict(
            X_test
        )

        # ----------------------------------------------------
        # Reconstruct population
        #
        # Population(t) =
        # Population(t-1) + predicted_change
        # ----------------------------------------------------

        previous_population = (
            X_test["Prev_Population"]
            .to_numpy()
        )

        actual_population = (
            population.iloc[test_idx]
            .to_numpy()
        )

        predicted_population = (
            previous_population
            + predicted_change
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        mae = mean_absolute_error(
            actual_population,
            predicted_population
        )

        rmse = np.sqrt(
            mean_squared_error(
                actual_population,
                predicted_population
            )
        )

        r2 = r2_score(
            actual_population,
            predicted_population
        )

        percentage_error = np.mean(
            np.abs(
                (
                    actual_population
                    - predicted_population
                )
                / actual_population
            )
        ) * 100

        mae_scores.append(mae)
        rmse_scores.append(rmse)
        r2_scores.append(r2)
        percentage_errors.append(
            percentage_error
        )

        start_year = int(
            years.iloc[test_idx].min()
        )

        end_year = int(
            years.iloc[test_idx].max()
        )

        print(
            f"\nFold {fold}: "
            f"{start_year}-{end_year}"
        )

        print(
            f"MAE  : {mae:,.2f}"
        )

        print(
            f"RMSE : {rmse:,.2f}"
        )

        print(
            f"R²   : {r2:.5f}"
        )

        print(
            f"MPE  : {percentage_error:.4f}%"
        )

    # --------------------------------------------------------
    # Average performance
    # --------------------------------------------------------

    mean_mae = np.mean(
        mae_scores
    )

    mean_rmse = np.mean(
        rmse_scores
    )

    mean_r2 = np.mean(
        r2_scores
    )

    mean_percentage_error = np.mean(
        percentage_errors
    )

    print(
        f"\nAverage {model_name} Performance"
    )

    print(
        f"Mean MAE  : {mean_mae:,.2f}"
    )

    print(
        f"Mean RMSE : {mean_rmse:,.2f}"
    )

    print(
        f"Mean R²   : {mean_r2:.5f}"
    )

    print(
        f"Mean MPE  : "
        f"{mean_percentage_error:.4f}%"
    )

    return {
        "Model": model_name,
        "MAE": mean_mae,
        "RMSE": mean_rmse,
        "R2": mean_r2,
        "Mean_Percentage_Error":
            mean_percentage_error
    }


# ============================================================
# TRAIN FINAL MODEL
# ============================================================

def train_final_model(
    model_name,
    X,
    y
):

    models = get_models()

    model = models[
        model_name
    ]

    print("\n" + "=" * 70)
    print("FINAL MODEL TRAINING")
    print("=" * 70)

    print(
        f"\nSelected model: "
        f"{model_name}"
    )

    print(
        f"Training observations: "
        f"{len(X)}"
    )

    model.fit(
        X,
        y
    )

    return model


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    model_name,
    features
):

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_FILE
    )

    # --------------------------------------------------------
    # Save exact feature list
    # --------------------------------------------------------

    feature_df = pd.DataFrame({
        "Feature": features
    })

    feature_df.to_csv(
        FEATURE_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata_file = os.path.join(
        MODEL_DIR,
        "selected_model.txt"
    )

    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            f"Model: {model_name}\n"
        )

        file.write(
            f"Features: {len(features)}\n"
        )

        file.write(
            "Feature leakage protection: ENABLED\n"
        )

    print(
        "\nFinal model saved:"
    )

    print(
        MODEL_FILE
    )

    print(
        "\nModel feature list saved:"
    )

    print(
        FEATURE_FILE
    )

    print(
        "\nModel metadata saved:"
    )

    print(
        metadata_file
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_data()

    # --------------------------------------------------------
    # Target
    # --------------------------------------------------------

    df = create_target(
        df
    )

    print(
        "\nTarget:"
    )

    print(
        "Population_Diff"
    )

    print(
        "\nThe model predicts:"
    )

    print(
        "Population change from one year "
        "to the next."
    )

    print(
        "\nPopulation_Diff = "
        "Population(t) - Population(t-1)"
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    features = get_features(
        df
    )

    X = validate_features(
        df,
        features
    )

    y = df[
        "Population_Diff"
    ]

    population = df[
        "Population"
    ]

    years = df[
        "Year"
    ]

    print(
        f"\nYears available: "
        f"{int(years.min())} - "
        f"{int(years.max())}"
    )

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------

    models = get_models()

    results = []

    for model_name, model in models.items():

        result = evaluate_model(
            model_name=model_name,
            model=model,
            X=X,
            y=y,
            population=population,
            years=years
        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # Results table
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    # Select using lowest MAE
    results_df.sort_values(
        by="MAE",
        ascending=True,
        inplace=True
    )

    results_df.reset_index(
        drop=True,
        inplace=True
    )

    results_df.to_csv(
        RESULTS_FILE,
        index=False
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "MODEL COMPARISON"
    )

    print(
        "=" * 70
    )

    print(
        results_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Best model
    # --------------------------------------------------------

    best_model_name = (
        results_df.iloc[0]["Model"]
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "BEST MODEL"
    )

    print(
        "=" * 70
    )

    print(
        f"Model: {best_model_name}"
    )

    print(
        f"MAE: "
        f"{results_df.iloc[0]['MAE']:,.2f}"
    )

    print(
        f"RMSE: "
        f"{results_df.iloc[0]['RMSE']:,.2f}"
    )

    print(
        f"R²: "
        f"{results_df.iloc[0]['R2']:.5f}"
    )

    print(
        f"Mean Percentage Error: "
        f"{results_df.iloc[0]['Mean_Percentage_Error']:.4f}%"
    )

    # --------------------------------------------------------
    # Final training
    # --------------------------------------------------------

    final_model = train_final_model(
        model_name=best_model_name,
        X=X,
        y=y
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_model(
        model=final_model,
        model_name=best_model_name,
        features=features
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "TRAINING COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        "\nOfficial datasets were NOT modified."
    )

    print(
        "Target leakage features were excluded."
    )

    print(
        "Chronological time-series validation was used."
    )

    print(
        "The final model was trained only after "
        "model comparison."
    )

    print(
        "\nNext step:"
    )

    print(
        "Use the saved model in forecast.py."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()