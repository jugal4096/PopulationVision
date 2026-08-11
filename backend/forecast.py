import os
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
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

POPULATION_SOURCE = os.path.join(
    DATASET_DIR,
    "population.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)

FORECAST_DIR = os.path.join(
    DATASET_DIR,
    "population_forecast"
)

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(FORECAST_DIR, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

FORECAST_START = 2026
FORECAST_END = 2050

BACKTEST_PERIODS = {
    "2010_2020": (2010, 2020),
    "2015_2024": (2015, 2024)
}

TREND_WINDOW = 10


# ============================================================
# FINAL FEATURE CONTRACT
# ============================================================
#
# IMPORTANT:
# These features MUST match train.py.
#
# Do not dynamically add/remove features here.
# If train.py changes, this list must change with it.
#
# ============================================================

MODEL_FEATURES = [
    "Year",
    "Prev_Population",
    "Population_Lag_2",
    "Population_Lag_3",
    "Population_MA3",
    "Birth_Rate_Lag_1",
    "Death_Rate_Lag_1",
    "Fertility_Rate_Lag_1",
    "Life_Expectancy_Lag_1",
    "GDP_Growth_Lag_1",
    "Net_Migration_Lag_1",
    "Literacy_Rate_Lag_1",
    "Urban_Population_Lag_1",
    "Infant_Mortality_Lag_1",
    "Population_Density_Lag_1"
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 80)
    print("INDIA POPULATION FORECASTING")
    print("=" * 80)

    if not os.path.exists(FEATURE_DATASET):
        raise FileNotFoundError(
            f"\nFeature dataset not found:\n{FEATURE_DATASET}"
        )

    if not os.path.exists(POPULATION_SOURCE):
        raise FileNotFoundError(
            f"\nPopulation source dataset not found:\n{POPULATION_SOURCE}"
        )

    features = pd.read_csv(
        FEATURE_DATASET
    )

    population_raw = pd.read_csv(
        POPULATION_SOURCE,
        skiprows=4
    )

    india_population = population_raw[
        population_raw["Country Name"] == "India"
    ]

    if india_population.empty:
        raise ValueError(
            "India was not found in population.csv"
        )

    india_population = india_population.iloc[0]

    population_values = []

    for year in range(1960, 2026):

        year_str = str(year)

        if year_str in india_population.index:

            value = pd.to_numeric(
                india_population[year_str],
                errors="coerce"
            )

        else:

            value = np.nan

        population_values.append(
            {
                "Year": year,
                "Official_Population": value
            }
        )

    official_population = pd.DataFrame(
        population_values
    )

    print("\nFeature dataset loaded successfully.")

    print(
        f"Rows    : {len(features)}"
    )

    print(
        f"Columns : {len(features.columns)}"
    )

    print("\nOfficial population data loaded.")

    return features, official_population


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(
    features,
    official_population
):

    df = features.copy()

    # Never trust a processed Population column.
    # Official population is loaded independently.
    df = df.drop(
        columns=["Population"],
        errors="ignore"
    )

    df = df.merge(
        official_population,
        on="Year",
        how="left"
    )

    df.rename(
        columns={
            "Official_Population": "Population"
        },
        inplace=True
    )

    df.sort_values(
        "Year",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    df["Population_Observed"] = (
        df["Population"].notna()
    )

    # --------------------------------------------------------
    # Population change
    # --------------------------------------------------------

    df["Population_Diff"] = (
        df["Population"].diff()
    )

    # --------------------------------------------------------
    # Only calculate population difference when BOTH
    # current and previous population are official.
    # --------------------------------------------------------

    previous_observed = (
        df["Population_Observed"]
        .shift(1)
        .astype("boolean")
        .fillna(False)
        .astype(bool)
    )

    valid_difference = (
        df["Population_Observed"]
        & previous_observed
    )

    df.loc[
        ~valid_difference,
        "Population_Diff"
    ] = np.nan

    return df


# ============================================================
# VALIDATE FEATURE CONTRACT
# ============================================================

def validate_features(df):

    missing = [
        feature
        for feature in MODEL_FEATURES
        if feature not in df.columns
    ]

    if missing:

        raise ValueError(
            "\nThe feature dataset does not contain "
            "the exact features required by the final model.\n\n"
            f"Missing features:\n{missing}\n\n"
            "Run feature_engineering.py first."
        )

    print("\n" + "=" * 80)
    print("FINAL MODEL FEATURES")
    print("=" * 80)

    for feature in MODEL_FEATURES:

        print(
            f"✓ {feature}"
        )

    print(
        f"\nNumber of model features: "
        f"{len(MODEL_FEATURES)}"
    )


# ============================================================
# FEATURE MEDIANS
# ============================================================

def fit_feature_medians(
    dataframe
):

    X = dataframe[
        MODEL_FEATURES
    ].copy()

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    medians = X.median()

    medians = medians.fillna(
        0.0
    )

    return medians


# ============================================================
# PREPARE X
# ============================================================

def prepare_X(
    dataframe,
    medians
):

    X = dataframe[
        MODEL_FEATURES
    ].copy()

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(
        medians
    )

    X = X.fillna(
        0.0
    )

    return X


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    train_df
):

    valid = train_df[
        train_df["Population_Diff"].notna()
    ].copy()

    if valid.empty:

        raise ValueError(
            "No valid Population_Diff observations "
            "available for training."
        )

    medians = fit_feature_medians(
        valid
    )

    X = prepare_X(
        valid,
        medians
    )

    y = valid[
        "Population_Diff"
    ]

    model = LinearRegression()

    model.fit(
        X,
        y
    )

    return model, medians


# ============================================================
# HISTORICAL BACKTEST
# ============================================================

def run_backtest(
    df,
    start_year,
    end_year,
    label
):

    print("\n" + "=" * 80)

    print(
        f"HISTORICAL BACKTEST: "
        f"{start_year} → {end_year}"
    )

    print("=" * 80)

    training_data = df[
        (df["Year"] < start_year)
        & df["Population_Diff"].notna()
    ].copy()

    test_data = df[
        (df["Year"] >= start_year)
        & (df["Year"] <= end_year)
        & df["Population"].notna()
        & df["Population_Diff"].notna()
    ].copy()

    if training_data.empty:

        print(
            "❌ No training data available."
        )

        return None

    if test_data.empty:

        print(
            "❌ No test data available."
        )

        return None

    print(
        f"\nTraining period: "
        f"{training_data['Year'].min()} - "
        f"{training_data['Year'].max()}"
    )

    print(
        f"Testing period: "
        f"{test_data['Year'].min()} - "
        f"{test_data['Year'].max()}"
    )

    model, medians = train_model(
        training_data
    )

    X_test = prepare_X(
        test_data,
        medians
    )

    predicted_diff = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Reconstruct absolute population.
    # --------------------------------------------------------

    previous_population = (
        test_data["Population"]
        .shift(1)
    )

    first_test_year = int(
        test_data["Year"].iloc[0]
    )

    previous_year_value = df.loc[
        df["Year"] == first_test_year - 1,
        "Population"
    ]

    if previous_year_value.empty:

        previous_population.iloc[0] = np.nan

    else:

        previous_population.iloc[0] = float(
            previous_year_value.iloc[0]
        )

    previous_population = (
        previous_population
        .astype(float)
        .values
    )

    actual_population = (
        test_data["Population"]
        .astype(float)
        .values
    )

    predicted_population = (
        previous_population
        + predicted_diff
    )

    valid_mask = (
        ~np.isnan(previous_population)
        & ~np.isnan(predicted_population)
        & ~np.isnan(actual_population)
    )

    actual_population = (
        actual_population[valid_mask]
    )

    predicted_population = (
        predicted_population[valid_mask]
    )

    predicted_diff = (
        predicted_diff[valid_mask]
    )

    test_years = (
        test_data["Year"]
        .values[valid_mask]
    )

    absolute_error = np.abs(
        actual_population
        - predicted_population
    )

    percentage_error = (
        absolute_error
        / actual_population
    ) * 100

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

    mpe = percentage_error.mean()

    result = pd.DataFrame(
        {
            "Year":
                test_years,

            "Actual_Population":
                actual_population,

            "Predicted_Population":
                predicted_population,

            "Predicted_Population_Change":
                predicted_diff,

            "Absolute_Error":
                absolute_error,

            "Percentage_Error":
                percentage_error
        }
    )

    print(
        f"\nMAE  : {mae:,.2f}"
    )

    print(
        f"RMSE : {rmse:,.2f}"
    )

    print(
        f"R²   : {r2:.5f}"
    )

    print(
        f"Mean Percentage Error : "
        f"{mpe:.4f}%"
    )

    output_path = os.path.join(
        FORECAST_DIR,
        f"backtest_{label}.csv"
    )

    result.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nBacktest saved:\n"
        f"{output_path}"
    )

    return {
        "Period":
            label,

        "Start_Year":
            start_year,

        "End_Year":
            end_year,

        "MAE":
            mae,

        "RMSE":
            rmse,

        "R2":
            r2,

        "Mean_Percentage_Error":
            mpe
    }


# ============================================================
# TREND PROJECTION
# ============================================================

def trend_project(
    df,
    column,
    target_year
):

    if column not in df.columns:

        return np.nan

    series = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if series.empty:

        return np.nan

    recent = series.tail(
        TREND_WINDOW
    )

    if len(recent) == 1:

        return float(
            recent.iloc[-1]
        )

    x = np.arange(
        len(recent),
        dtype=float
    )

    y = recent.values.astype(
        float
    )

    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

    latest_year = int(
        df["Year"].max()
    )

    steps_ahead = (
        target_year
        - latest_year
    )

    projected = (
        intercept
        + slope
        * (
            len(recent) - 1
            + steps_ahead
        )
    )

    return float(
        projected
    )


# ============================================================
# POPULATION HISTORY
# ============================================================

def get_population_history(
    df,
    current_population
):

    history = {}

    for _, row in df.iterrows():

        year = int(
            row["Year"]
        )

        population = row[
            "Population"
        ]

        if pd.notna(population):

            history[year] = float(
                population
            )

    # Replace / add 2025.
    history[2025] = float(
        current_population
    )

    return history


# ============================================================
# BUILD FUTURE MODEL ROW
# ============================================================

def build_future_row(
    df,
    population_history,
    target_year,
    medians
):

    row = {}

    # --------------------------------------------------------
    # Year
    # --------------------------------------------------------

    row["Year"] = target_year

    # --------------------------------------------------------
    # Population history
    # --------------------------------------------------------

    previous_population = (
        population_history.get(
            target_year - 1,
            np.nan
        )
    )

    population_lag_2 = (
        population_history.get(
            target_year - 2,
            np.nan
        )
    )

    population_lag_3 = (
        population_history.get(
            target_year - 3,
            np.nan
        )
    )

    row["Prev_Population"] = (
        previous_population
    )

    row["Population_Lag_2"] = (
        population_lag_2
    )

    row["Population_Lag_3"] = (
        population_lag_3
    )

    # --------------------------------------------------------
    # Previous 3-year moving average
    # --------------------------------------------------------

    historical_values = []

    for year in range(
        target_year - 3,
        target_year
    ):

        value = population_history.get(
            year,
            np.nan
        )

        if pd.notna(value):

            historical_values.append(
                float(value)
            )

    if historical_values:

        row["Population_MA3"] = (
            np.mean(
                historical_values
            )
        )

    else:

        row["Population_MA3"] = np.nan

    # --------------------------------------------------------
    # Future explanatory variables
    # --------------------------------------------------------

    future_feature_source = {

        "Birth_Rate_Lag_1":
            "Birth_Rate",

        "Death_Rate_Lag_1":
            "Death_Rate",

        "Fertility_Rate_Lag_1":
            "Fertility_Rate",

        "Life_Expectancy_Lag_1":
            "Life_Expectancy",

        "GDP_Growth_Lag_1":
            "GDP_Growth",

        "Net_Migration_Lag_1":
            "Net_Migration",

        "Literacy_Rate_Lag_1":
            "Literacy_Rate",

        "Urban_Population_Lag_1":
            "Urban_Population",

        "Infant_Mortality_Lag_1":
            "Infant_Mortality",

        "Population_Density_Lag_1":
            "Population_Density"
    }

    for (
        target_feature,
        source_feature
    ) in future_feature_source.items():

        if source_feature in df.columns:

            row[target_feature] = (
                trend_project(
                    df,
                    source_feature,
                    target_year - 1
                )
            )

        else:

            row[target_feature] = np.nan

    X = pd.DataFrame(
        [row]
    )

    X = X[
        MODEL_FEATURES
    ]

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(
        medians
    )

    X = X.fillna(
        0.0
    )

    return X


# ============================================================
# ESTIMATE 2025
# ============================================================

def estimate_2025(
    df,
    final_model,
    medians
):

    population_2025 = df.loc[
        df["Year"] == 2025,
        "Population"
    ]

    # --------------------------------------------------------
    # Official 2025 exists
    # --------------------------------------------------------

    if (
        not population_2025.empty
        and pd.notna(
            population_2025.iloc[0]
        )
    ):

        value = float(
            population_2025.iloc[0]
        )

        print(
            "\nOfficial 2025 population found: "
            f"{value:,.0f}"
        )

        return value, False

    # --------------------------------------------------------
    # Official 2024 required
    # --------------------------------------------------------

    population_2024 = df.loc[
        df["Year"] == 2024,
        "Population"
    ]

    if (
        population_2024.empty
        or pd.isna(
            population_2024.iloc[0]
        )
    ):

        raise ValueError(
            "Official 2024 population is required "
            "to estimate 2025."
        )

    population_2024 = float(
        population_2024.iloc[0]
    )

    population_history = (
        get_population_history(
            df,
            population_2024
        )
    )

    X_2025 = build_future_row(
        df,
        population_history,
        2025,
        medians
    )

    predicted_change = float(
        final_model.predict(
            X_2025
        )[0]
    )

    estimated_population = (
        population_2024
        + predicted_change
    )

    growth = (
        predicted_change
        / population_2024
    ) * 100

    print("\n" + "=" * 80)
    print("2025 POPULATION ESTIMATION")
    print("=" * 80)

    print(
        f"\nOfficial 2024 population : "
        f"{population_2024:,.0f}"
    )

    print(
        f"Estimated 2025 change    : "
        f"{predicted_change:,.0f}"
    )

    print(
        f"Estimated 2025 population: "
        f"{estimated_population:,.0f}"
    )

    print(
        f"Estimated 2025 growth    : "
        f"{growth:.4f}%"
    )

    return estimated_population, True


# ============================================================
# FUTURE FORECAST
# ============================================================

def forecast_future(
    df,
    final_model,
    medians
):

    print("\n" + "=" * 80)
    print(
        f"{FORECAST_START}-{FORECAST_END} FUTURE FORECAST"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # Estimate / retrieve 2025
    # --------------------------------------------------------

    (
        population_2025,
        estimated_2025
    ) = estimate_2025(
        df,
        final_model,
        medians
    )

    # --------------------------------------------------------
    # Population history
    # --------------------------------------------------------

    population_history = (
        get_population_history(
            df,
            population_2025
        )
    )

    # --------------------------------------------------------
    # Save 2025 status
    # --------------------------------------------------------

    status_df = pd.DataFrame(
        {
            "Year": [2025],

            "Population": [
                population_2025
            ],

            "Status": [
                "Estimated"
                if estimated_2025
                else "Official"
            ]
        }
    )

    status_path = os.path.join(
        FORECAST_DIR,
        "population_2025_status.csv"
    )

    status_df.to_csv(
        status_path,
        index=False
    )

    # --------------------------------------------------------
    # Recursive forecasting
    # --------------------------------------------------------

    forecast_rows = []

    for year in range(
        FORECAST_START,
        FORECAST_END + 1
    ):

        X_future = build_future_row(
            df,
            population_history,
            year,
            medians
        )

        predicted_change = float(
            final_model.predict(
                X_future
            )[0]
        )

        previous_population = (
            population_history[
                year - 1
            ]
        )

        predicted_population = (
            previous_population
            + predicted_change
        )

        # Prevent impossible negative population.
        predicted_population = max(
            predicted_population,
            0.0
        )

        growth_rate = (
            predicted_change
            / previous_population
        ) * 100

        forecast_rows.append(
            {
                "Year":
                    year,

                "Previous_Population":
                    previous_population,

                "Predicted_Population_Change":
                    predicted_change,

                "Predicted_Population":
                    predicted_population,

                "Predicted_Growth_Rate":
                    growth_rate,

                "Status":
                    "Forecast"
            }
        )

        # ----------------------------------------------------
        # Critical:
        # Current prediction becomes history for next year.
        # ----------------------------------------------------

        population_history[
            year
        ] = predicted_population

    forecast_df = pd.DataFrame(
        forecast_rows
    )

    # --------------------------------------------------------
    # Save forecast
    # --------------------------------------------------------

    forecast_filename = (
        f"population_forecast_"
        f"{FORECAST_START}_"
        f"{FORECAST_END}.csv"
    )

    forecast_path = os.path.join(
        FORECAST_DIR,
        forecast_filename
    )

    forecast_df.to_csv(
        forecast_path,
        index=False
    )

    print("\n")
    print(
        forecast_df.to_string(
            index=False
        )
    )

    print(
        f"\n2025 status saved:\n"
        f"{status_path}"
    )

    print(
        f"\nForecast saved:\n"
        f"{forecast_path}"
    )

    return forecast_df


# ============================================================
# SAVE FINAL MODEL
# ============================================================

def save_final_model(
    model,
    medians
):

    model_path = os.path.join(
        MODEL_DIR,
        "population_forecast_model.pkl"
    )

    model_bundle = {

        "model":
            model,

        "feature_columns":
            MODEL_FEATURES,

        "feature_medians":
            medians.to_dict(),

        "model_type":
            "LinearRegression",

        "target":
            "Population_Diff",

        "forecast_start":
            FORECAST_START,

        "forecast_end":
            FORECAST_END
    }

    joblib.dump(
        model_bundle,
        model_path
    )

    feature_path = os.path.join(
        MODEL_DIR,
        "forecast_model_features.csv"
    )

    pd.DataFrame(
        {
            "Feature":
                MODEL_FEATURES
        }
    ).to_csv(
        feature_path,
        index=False
    )

    metadata_path = os.path.join(
        MODEL_DIR,
        "selected_model.txt"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "Model: Linear Regression\n"
        )

        file.write(
            "Target: Population_Diff\n"
        )

        file.write(
            f"Features: "
            f"{len(MODEL_FEATURES)}\n"
        )

        file.write(
            "Forecast Horizon: "
            f"{FORECAST_START}-{FORECAST_END}\n"
        )

        file.write(
            "Chronological validation: Yes\n"
        )

        file.write(
            "Population leakage features: "
            "Excluded from model inputs\n"
        )

    print(
        "\nFinal forecasting model saved:"
    )

    print(
        model_path
    )

    print(
        "\nModel feature list saved:"
    )

    print(
        feature_path
    )

    print(
        "\nModel metadata saved:"
    )

    print(
        metadata_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. LOAD DATA
    # --------------------------------------------------------

    (
        features,
        official_population
    ) = load_data()

    # --------------------------------------------------------
    # 2. PREPARE DATA
    # --------------------------------------------------------

    df = prepare_data(
        features,
        official_population
    )

    print("\n" + "=" * 80)
    print("OFFICIAL POPULATION CHECK")
    print("=" * 80)

    print(
        df[
            df["Year"].isin(
                [2023, 2024, 2025]
            )
        ][
            [
                "Year",
                "Population",
                "Population_Observed"
            ]
        ].to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # 3. VALIDATE FEATURE CONTRACT
    # --------------------------------------------------------

    validate_features(
        df
    )

    # --------------------------------------------------------
    # 4. HISTORICAL BACKTEST
    # --------------------------------------------------------

    backtest_results = []

    for (
        label,
        (
            start_year,
            end_year
        )
    ) in BACKTEST_PERIODS.items():

        result = run_backtest(
            df,
            start_year,
            end_year,
            label
        )

        if result is not None:

            backtest_results.append(
                result
            )

    # --------------------------------------------------------
    # 5. SAVE BACKTEST SUMMARY
    # --------------------------------------------------------

    if backtest_results:

        summary_df = pd.DataFrame(
            backtest_results
        )

        summary_path = os.path.join(
            FORECAST_DIR,
            "backtest_summary.csv"
        )

        summary_df.to_csv(
            summary_path,
            index=False
        )

        print("\n" + "=" * 80)
        print("BACKTEST SUMMARY")
        print("=" * 80)

        print(
            summary_df.to_string(
                index=False
            )
        )

        print(
            f"\nSaved:\n"
            f"{summary_path}"
        )

    # --------------------------------------------------------
    # 6. FINAL TRAINING
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("TRAINING FINAL MODEL")
    print("=" * 80)

    valid_training_data = df[
        df["Population_Diff"].notna()
    ].copy()

    print(
        f"\nTraining observations: "
        f"{len(valid_training_data)}"
    )

    print(
        f"Training period: "
        f"{valid_training_data['Year'].min()} - "
        f"{valid_training_data['Year'].max()}"
    )

    final_model, final_medians = (
        train_model(
            valid_training_data
        )
    )

    print(
        "\nFinal model trained successfully."
    )

    # --------------------------------------------------------
    # 7. SAVE MODEL
    # --------------------------------------------------------

    save_final_model(
        final_model,
        final_medians
    )

    # --------------------------------------------------------
    # 8. FORECAST 2026-2050
    # --------------------------------------------------------

    forecast_df = forecast_future(
        df,
        final_model,
        final_medians
    )

    # --------------------------------------------------------
    # 9. FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("FORECASTING PIPELINE COMPLETED")
    print("=" * 80)

    print(
        "\nOriginal official WDI datasets were NOT modified."
    )

    print(
        f"The final model uses exactly "
        f"{len(MODEL_FEATURES)} trained features."
    )

    print(
        "Chronological backtesting was performed."
    )

    print(
        "Future population is generated recursively."
    )

    print(
        "2025 is estimated only when official "
        "2025 data is unavailable."
    )

    print(
        f"Forecast horizon: "
        f"{FORECAST_START}-{FORECAST_END}"
    )

    if not forecast_df.empty:

        first_population = (
            forecast_df.iloc[0][
                "Predicted_Population"
            ]
        )

        last_population = (
            forecast_df.iloc[-1][
                "Predicted_Population"
            ]
        )

        total_growth = (
            (
                last_population
                / first_population
            ) - 1
        ) * 100

        print(
            f"\n{FORECAST_START} population: "
            f"{first_population:,.0f}"
        )

        print(
            f"{FORECAST_END} population: "
            f"{last_population:,.0f}"
        )

        print(
            f"{FORECAST_START}-{FORECAST_END} "
            f"growth: {total_growth:.2f}%"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()