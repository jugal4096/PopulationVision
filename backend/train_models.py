
import os
import math
import joblib
import pandas as pd

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
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
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
# LOAD DATASET
# ============================================================

def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"\nDataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    print("=" * 80)
    print("INDIA POPULATION FORECASTING")
    print("=" * 80)

    print("\nDataset Loaded Successfully")
    print(f"Dataset Shape : {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 Rows:")
    print(df.head())

    return df


# ============================================================
# SPLIT DATASET
# ============================================================

def split_dataset(df):

    print("\n" + "=" * 80)
    print("TRAIN / TEST SPLIT")
    print("=" * 80)

    # Historical data for training
    train = df[df["Year"] <= 2015].copy()

    # Future period used for testing
    test = df[df["Year"] > 2015].copy()

    # Remove target from input features
    X_train = train.drop(
        columns=["Population"]
    )

    y_train = train["Population"]

    X_test = test.drop(
        columns=["Population"]
    )

    y_test = test["Population"]

    print(
        f"\nTraining period : "
        f"{train['Year'].min()} - {train['Year'].max()}"
    )

    print(
        f"Training rows   : {len(train)}"
    )

    print(
        f"\nTesting period  : "
        f"{test['Year'].min()} - {test['Year'].max()}"
    )

    print(
        f"Testing rows    : {len(test)}"
    )

    print(
        f"\nNumber of features : {X_train.shape[1]}"
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        test["Year"].reset_index(drop=True)
    )


# ============================================================
# MODELS
# ============================================================

def get_models():

    models = {

        "Linear Regression":
            LinearRegression(),

        "Random Forest":
            RandomForestRegressor(
                n_estimators=300,
                random_state=42
            ),

        "Gradient Boosting":
            GradientBoostingRegressor(
                random_state=42
            )
    }

    return models


# ============================================================
# TRAIN AND EVALUATE MODELS
# ============================================================

def train_models(
    models,
    X_train,
    X_test,
    y_train,
    y_test,
    test_years
):

    best_model = None
    best_name = None
    best_r2 = float("-inf")

    results = []

    prediction_tables = {}

    for name, model in models.items():

        print("\n" + "-" * 80)
        print(f"Training {name}")
        print("-" * 80)

        # ----------------------------------------------------
        # TRAIN
        # ----------------------------------------------------

        model.fit(
            X_train,
            y_train
        )

        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        prediction = model.predict(
            X_test
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        mae = mean_absolute_error(
            y_test,
            prediction
        )

        mse = mean_squared_error(
            y_test,
            prediction
        )

        rmse = math.sqrt(mse)

        r2 = r2_score(
            y_test,
            prediction
        )

        # ----------------------------------------------------
        # YEAR-BY-YEAR ERROR
        # ----------------------------------------------------

        absolute_error = abs(
            y_test.reset_index(drop=True)
            - prediction
        )

        percentage_error = (
            absolute_error
            / y_test.reset_index(drop=True)
        ) * 100

        prediction_df = pd.DataFrame({

            "Year":
                test_years,

            "Actual_Population":
                y_test.reset_index(drop=True),

            "Predicted_Population":
                prediction,

            "Absolute_Error":
                absolute_error,

            "Percentage_Error":
                percentage_error
        })

        prediction_tables[name] = prediction_df

        # ----------------------------------------------------
        # PRINT METRICS
        # ----------------------------------------------------

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
            f"Mean Percentage Error : "
            f"{percentage_error.mean():.4f}%"
        )

        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        results.append({

            "Model":
                name,

            "MAE":
                mae,

            "RMSE":
                rmse,

            "R2":
                r2,

            "Mean_Percentage_Error":
                percentage_error.mean()
        })

        # ----------------------------------------------------
        # SAVE EACH MODEL PREDICTIONS
        # ----------------------------------------------------

        safe_name = (
            name
            .lower()
            .replace(" ", "_")
        )

        prediction_path = os.path.join(
            MODEL_DIR,
            f"{safe_name}_predictions.csv"
        )

        prediction_df.to_csv(
            prediction_path,
            index=False
        )

        print(
            f"\nPredictions saved:"
        )

        print(
            prediction_path
        )

        # ----------------------------------------------------
        # BEST MODEL
        # ----------------------------------------------------

        if r2 > best_r2:

            best_r2 = r2

            best_model = model

            best_name = name

    return (
        best_model,
        best_name,
        results,
        prediction_tables
    )


# ============================================================
# PRINT DETAILED PREDICTIONS
# ============================================================

def print_prediction_analysis(
    prediction_tables,
    best_name
):

    print("\n" + "=" * 80)
    print("YEAR-BY-YEAR PREDICTION ANALYSIS")
    print("=" * 80)

    best_predictions = (
        prediction_tables[best_name]
    )

    print(
        f"\nBest Model: {best_name}"
    )

    print("\nPredictions:")

    print(
        best_predictions.to_string(
            index=False
        )
    )

    print("\nLargest Prediction Errors:")

    largest_errors = (
        best_predictions
        .sort_values(
            by="Absolute_Error",
            ascending=False
        )
        .head(5)
    )

    print(
        largest_errors.to_string(
            index=False
        )
    )


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    best_model,
    best_name,
    results
):

    # --------------------------------------------------------
    # SAVE BEST MODEL
    # --------------------------------------------------------

    model_path = os.path.join(
        MODEL_DIR,
        "population_predictor.pkl"
    )

    joblib.dump(
        best_model,
        model_path
    )

    # --------------------------------------------------------
    # SAVE MODEL COMPARISON
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    results_df.sort_values(
        by="R2",
        ascending=False,
        inplace=True
    )

    results_path = os.path.join(
        MODEL_DIR,
        "model_results.csv"
    )

    results_df.to_csv(
        results_path,
        index=False
    )

    # --------------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)

    print(
        results_df.to_string(
            index=False
        )
    )

    print(
        f"\nBest Model : {best_name}"
    )

    print("\nSaved Files:")

    print(
        model_path
    )

    print(
        results_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_dataset()

    # --------------------------------------------------------
    # SPLIT
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test,
        test_years
    ) = split_dataset(df)

    # --------------------------------------------------------
    # MODELS
    # --------------------------------------------------------

    models = get_models()

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    (
        best_model,
        best_name,
        results,
        prediction_tables
    ) = train_models(
        models,
        X_train,
        X_test,
        y_train,
        y_test,
        test_years
    )

    # --------------------------------------------------------
    # DETAILED ANALYSIS
    # --------------------------------------------------------

    print_prediction_analysis(
        prediction_tables,
        best_name
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_results(
        best_model,
        best_name,
        results
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 80)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
