
import os
import glob
import json
import math
import numpy as np
import pandas as pd


# ============================================================
# NATIONAL DEMOGRAPHIC ANALYTICS ENGINE
# ============================================================
#
# PURPOSE
# -------
# This module does NOT train or modify the ML model.
#
# It combines:
#
#   1. Official historical population data
#      1960 - 2024
#
#   2. Model-estimated 2025 population
#
#   3. ML forecast
#      2026 - 2050
#
# and generates:
#
#   - 10-year analysis
#   - 20-year analysis
#   - 25-year analysis
#   - 50-year analysis
#   - 100-year requested analysis
#   - population milestones
#   - demographic insights
#   - research CSV files
#   - research JSON report
#
# IMPORTANT
# ---------
# Official datasets are NEVER modified by this script.
# No model is retrained by this script.
# No forecast values are changed by this script.
#
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)


# ============================================================
# INPUT DATASET PATHS
# ============================================================

CLEAN_DATASET = os.path.join(
    DATASET_DIR,
    "india_clean_dataset.csv"
)


# Forecast directory created by forecast.py
FORECAST_DIR = os.path.join(
    DATASET_DIR,
    "population_forecast"
)


# 2025 status file created by forecast.py
STATUS_2025_FILE = os.path.join(
    FORECAST_DIR,
    "population_2025_status.csv"
)


# Expected forecast file
FORECAST_FILE = os.path.join(
    FORECAST_DIR,
    "population_forecast_2026_2050.csv"
)


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR = os.path.join(
    FORECAST_DIR,
    "analytics"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# OUTPUT FILES
# ============================================================

POPULATION_ANALYTICS_FILE = os.path.join(
    OUTPUT_DIR,
    "population_analytics.csv"
)

RESEARCH_ANALYSIS_FILE = os.path.join(
    OUTPUT_DIR,
    "research_period_analysis.csv"
)

MILESTONES_FILE = os.path.join(
    OUTPUT_DIR,
    "future_milestones.csv"
)

REPORT_FILE = os.path.join(
    OUTPUT_DIR,
    "research_report.json"
)

DATA_STATUS_FILE = os.path.join(
    OUTPUT_DIR,
    "data_status.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

OFFICIAL_START_YEAR = 1960
OFFICIAL_LAST_YEAR = 2024

ESTIMATED_YEAR = 2025

FORECAST_START_YEAR = 2026
FORECAST_END_YEAR = 2050


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(
    dataframe,
    possible_names
):
    """
    Find the first matching column from a list of possible names.

    Matching is case-insensitive and ignores spaces,
    underscores and hyphens.
    """

    normalized = {}

    for column in dataframe.columns:

        key = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        normalized[key] = column

    for name in possible_names:

        key = (
            str(name)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        if key in normalized:
            return normalized[key]

    return None


def convert_numeric(
    series
):
    """
    Safely convert a pandas Series to numeric.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def safe_round(
    value,
    digits=2
):
    """
    Safe rounding for JSON/CSV output.
    """

    if value is None:
        return None

    try:

        if pd.isna(value):
            return None

        return round(
            float(value),
            digits
        )

    except Exception:
        return None


# ============================================================
# LOAD OFFICIAL HISTORICAL DATA
# ============================================================

def load_historical_data():

    print(
        "\nLoading official historical dataset..."
    )

    if not os.path.exists(
        CLEAN_DATASET
    ):

        raise FileNotFoundError(
            "\nOfficial clean dataset not found:\n"
            f"{CLEAN_DATASET}"
        )

    df = pd.read_csv(
        CLEAN_DATASET
    )

    year_column = find_column(
        df,
        [
            "Year"
        ]
    )

    population_column = find_column(
        df,
        [
            "Population",
            "Population_Total"
        ]
    )

    if year_column is None:

        raise ValueError(
            "Historical dataset does not contain a Year column."
        )

    if population_column is None:

        raise ValueError(
            "Historical dataset does not contain a Population column."
        )

    df = df.rename(
        columns={
            year_column: "Year",
            population_column: "Population"
        }
    )

    df["Year"] = convert_numeric(
        df["Year"]
    )

    df["Population"] = convert_numeric(
        df["Population"]
    )

    df = df.dropna(
        subset=["Year"]
    ).copy()

    df["Year"] = (
        df["Year"]
        .astype(int)
    )

    # --------------------------------------------------------
    # CRITICAL:
    # Only official observations through 2024 are accepted.
    #
    # Even if the clean dataset contains a filled/interpolated
    # 2025 value, this analytics engine will NOT treat it as
    # official historical data.
    # --------------------------------------------------------

    df = df[
        (df["Year"] >= OFFICIAL_START_YEAR)
        &
        (df["Year"] <= OFFICIAL_LAST_YEAR)
    ].copy()

    df = df.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    # Remove duplicate years defensively.
    df = df.drop_duplicates(
        subset=["Year"],
        keep="last"
    ).reset_index(
        drop=True
    )

    # Official population must exist for historical analysis.
    missing_population = df[
        df["Population"].isna()
    ]

    if not missing_population.empty:

        print(
            "\n⚠️ Warning: official historical population "
            "contains missing values."
        )

        print(
            missing_population[
                ["Year"]
            ].to_string(
                index=False
            )
        )

    print(
        f"Official historical rows : {len(df)}"
    )

    if not df.empty:

        print(
            f"Historical period       : "
            f"{df['Year'].min()} - "
            f"{df['Year'].max()}"
        )

    return df


# ============================================================
# FIND FORECAST FILE
# ============================================================

def locate_forecast_file():

    # --------------------------------------------------------
    # First try the exact expected path.
    # --------------------------------------------------------

    if os.path.exists(
        FORECAST_FILE
    ):

        return FORECAST_FILE

    # --------------------------------------------------------
    # If the filename changed slightly, search the directory.
    # --------------------------------------------------------

    if not os.path.exists(
        FORECAST_DIR
    ):

        raise FileNotFoundError(
            "\nForecast directory does not exist:\n"
            f"{FORECAST_DIR}"
        )

    candidates = glob.glob(
        os.path.join(
            FORECAST_DIR,
            "*.csv"
        )
    )

    valid_candidates = []

    for path in candidates:

        filename = os.path.basename(
            path
        ).lower()

        if (
            "forecast" in filename
            and "2026" in filename
            and "2050" in filename
            and "status" not in filename
        ):

            valid_candidates.append(
                path
            )

    if len(valid_candidates) == 1:

        return valid_candidates[0]

    if len(valid_candidates) > 1:

        valid_candidates.sort(
            key=os.path.getmtime,
            reverse=True
        )

        return valid_candidates[0]

    raise FileNotFoundError(
        "\nNo 2026-2050 forecast file found.\n"
        f"Expected:\n{FORECAST_FILE}\n"
        f"Directory searched:\n{FORECAST_DIR}"
    )


# ============================================================
# LOAD FORECAST DATA
# ============================================================

def load_forecast_data():

    forecast_path = locate_forecast_file()

    print(
        "\nForecast dataset:"
    )

    print(
        forecast_path
    )

    df = pd.read_csv(
        forecast_path
    )

    year_column = find_column(
        df,
        [
            "Year"
        ]
    )

    population_column = find_column(
        df,
        [
            "Predicted_Population",
            "Forecast_Population",
            "Population"
        ]
    )

    if year_column is None:

        raise ValueError(
            "Forecast dataset does not contain a Year column."
        )

    if population_column is None:

        raise ValueError(
            "Forecast dataset does not contain a population "
            "prediction column."
        )

    df = df.rename(
        columns={
            year_column: "Year",
            population_column: "Predicted_Population"
        }
    )

    df["Year"] = convert_numeric(
        df["Year"]
    )

    df["Predicted_Population"] = convert_numeric(
        df["Predicted_Population"]
    )

    df = df.dropna(
        subset=["Year"]
    ).copy()

    df["Year"] = (
        df["Year"]
        .astype(int)
    )

    df = df[
        (
            df["Year"] >= FORECAST_START_YEAR
        )
        &
        (
            df["Year"] <= FORECAST_END_YEAR
        )
    ].copy()

    df = df.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    df = df.drop_duplicates(
        subset=["Year"],
        keep="last"
    ).reset_index(
        drop=True
    )

    if df.empty:

        raise ValueError(
            "Forecast dataset contains no valid "
            "2026-2050 forecast rows."
        )

    print(
        f"Forecast rows           : {len(df)}"
    )

    print(
        f"Forecast period         : "
        f"{df['Year'].min()} - "
        f"{df['Year'].max()}"
    )

    return df


# ============================================================
# LOAD 2025 ESTIMATED STATUS
# ============================================================

def load_2025_estimate():

    print(
        "\nLoading 2025 model estimate..."
    )

    if not os.path.exists(
        STATUS_2025_FILE
    ):

        print(
            "\n⚠️ 2025 status file not found:"
        )

        print(
            STATUS_2025_FILE
        )

        print(
            "\n2025 will NOT be invented by analytics."
        )

        return None

    df = pd.read_csv(
        STATUS_2025_FILE
    )

    if df.empty:

        print(
            "\n⚠️ 2025 status file is empty."
        )

        return None

    year_column = find_column(
        df,
        [
            "Year"
        ]
    )

    population_column = find_column(
        df,
        [
            "Estimated_Population",
            "Predicted_Population",
            "Population",
            "EstimatedPopulation",
            "PredictedPopulation"
        ]
    )

    # --------------------------------------------------------
    # Some forecast.py versions may save a single-row status
    # file without an explicit Year column.
    #
    # In that case, we know this file represents 2025.
    # --------------------------------------------------------

    if population_column is None:

        print(
            "\n⚠️ Could not identify a 2025 population "
            "column in status file."
        )

        print(
            "Available columns:"
        )

        print(
            list(df.columns)
        )

        return None

    values = convert_numeric(
        df[population_column]
    ).dropna()

    if values.empty:

        print(
            "\n⚠️ No numeric 2025 population found "
            "in status file."
        )

        return None

    estimated_population = float(
        values.iloc[0]
    )

    # --------------------------------------------------------
    # If a Year column exists, verify it.
    # --------------------------------------------------------

    if year_column is not None:

        years = convert_numeric(
            df[year_column]
        ).dropna()

        if not years.empty:

            if int(years.iloc[0]) != ESTIMATED_YEAR:

                print(
                    "\n⚠️ Warning: status file year is "
                    f"{int(years.iloc[0])}, not 2025."
                )

                print(
                    "The file will not be used."
                )

                return None

    print(
        f"Estimated 2025 population : "
        f"{estimated_population:,.0f}"
    )

    return estimated_population


# ============================================================
# BUILD UNIFIED POPULATION DATASET
# ============================================================

def build_population_series(
    historical,
    estimated_2025,
    forecast
):

    records = []

    # ========================================================
    # HISTORICAL
    # ========================================================

    for _, row in historical.iterrows():

        population = row["Population"]

        if pd.isna(
            population
        ):
            continue

        records.append({

            "Year":
                int(row["Year"]),

            "Population":
                float(population),

            "Source_Type":
                "Historical",

            "Data_Status":
                "Official",

            "Source":
                "Official WDI dataset"

        })

    # ========================================================
    # ESTIMATED 2025
    # ========================================================

    if estimated_2025 is not None:

        records.append({

            "Year":
                ESTIMATED_YEAR,

            "Population":
                float(estimated_2025),

            "Source_Type":
                "Estimated",

            "Data_Status":
                "Model Estimated",

            "Source":
                "Population forecasting model"

        })

    # ========================================================
    # FORECAST 2026-2050
    # ========================================================

    for _, row in forecast.iterrows():

        population = row[
            "Predicted_Population"
        ]

        if pd.isna(
            population
        ):
            continue

        records.append({

            "Year":
                int(row["Year"]),

            "Population":
                float(population),

            "Source_Type":
                "Forecast",

            "Data_Status":
                "ML Forecast",

            "Source":
                "Population forecasting model"

        })

    result = pd.DataFrame(
        records
    )

    if result.empty:

        raise ValueError(
            "Unified population dataset is empty."
        )

    result = result.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Ensure exactly one row per year.
    # --------------------------------------------------------

    duplicate_years = result[
        result["Year"].duplicated(
            keep=False
        )
    ]

    if not duplicate_years.empty:

        raise ValueError(
            "Duplicate years detected in unified "
            "population dataset:\n"
            f"{duplicate_years['Year'].tolist()}"
        )

    # ========================================================
    # YEARLY CHANGE
    # ========================================================

    result["Population_Change"] = (
        result["Population"].diff()
    )

    # ========================================================
    # GROWTH RATE
    # ========================================================

    result["Growth_Rate"] = (
        result["Population"]
        .pct_change()
        * 100
    )

    # ========================================================
    # DATA SOURCE VALIDATION
    # ========================================================

    print(
        "\nUnified data classification:"
    )

    classification_years = [
        2023,
        2024,
        2025,
        2026
    ]

    classification = result[
        result["Year"].isin(
            classification_years
        )
    ][
        [
            "Year",
            "Population",
            "Source_Type",
            "Data_Status",
            "Source"
        ]
    ]

    if classification.empty:

        print(
            "⚠️ Classification check returned no rows."
        )

    else:

        print(
            classification.to_string(
                index=False
            )
        )

    return result


# ============================================================
# VALIDATE DATA PIPELINE
# ============================================================

def validate_population_series(
    population_df
):

    print(
        "\nValidating population analytics series..."
    )

    errors = []

    # --------------------------------------------------------
    # Historical validation
    # --------------------------------------------------------

    historical = population_df[
        population_df["Source_Type"]
        == "Historical"
    ]

    if not historical.empty:

        max_historical_year = int(
            historical["Year"].max()
        )

        if (
            max_historical_year
            > OFFICIAL_LAST_YEAR
        ):

            errors.append(
                "Historical data extends beyond 2024."
            )

    # --------------------------------------------------------
    # Estimated validation
    # --------------------------------------------------------

    estimated = population_df[
        population_df["Source_Type"]
        == "Estimated"
    ]

    for year in estimated["Year"]:

        if int(year) != ESTIMATED_YEAR:

            errors.append(
                f"Estimated data contains unexpected "
                f"year {year}."
            )

    # --------------------------------------------------------
    # Forecast validation
    # --------------------------------------------------------

    forecast = population_df[
        population_df["Source_Type"]
        == "Forecast"
    ]

    if not forecast.empty:

        min_forecast_year = int(
            forecast["Year"].min()
        )

        max_forecast_year = int(
            forecast["Year"].max()
        )

        if (
            min_forecast_year
            < FORECAST_START_YEAR
        ):

            errors.append(
                "Forecast data starts before 2026."
            )

        if (
            max_forecast_year
            > FORECAST_END_YEAR
        ):

            errors.append(
                "Forecast data extends beyond 2050."
            )

    # --------------------------------------------------------
    # Population sanity
    # --------------------------------------------------------

    invalid_population = population_df[
        (
            population_df["Population"]
            <= 0
        )
        |
        (
            population_df["Population"].isna()
        )
    ]

    if not invalid_population.empty:

        errors.append(
            "Invalid or missing population values detected."
        )

    # --------------------------------------------------------
    # Duplicate years
    # --------------------------------------------------------

    if population_df["Year"].duplicated().any():

        errors.append(
            "Duplicate years detected."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    if errors:

        print(
            "\n❌ DATA VALIDATION FAILED"
        )

        for error in errors:

            print(
                f"   - {error}"
            )

        raise ValueError(
            "Analytics data validation failed."
        )

    print(
        "✓ Historical period validated: 1960-2024"
    )

    if not estimated.empty:

        print(
            "✓ Estimated period validated: 2025"
        )

    if not forecast.empty:

        print(
            "✓ Forecast period validated: 2026-2050"
        )

    print(
        "✓ No duplicate years"
    )

    print(
        "✓ No invalid population values"
    )

    return True


# ============================================================
# DETERMINE PERIOD TYPE
# ============================================================

def determine_period_type(
    start_year,
    end_year
):

    if (
        start_year >= OFFICIAL_START_YEAR
        and end_year <= OFFICIAL_LAST_YEAR
    ):

        return "Historical"

    if (
        start_year >= FORECAST_START_YEAR
    ):

        return "Forecast"

    if (
        start_year <= ESTIMATED_YEAR
        and end_year >= FORECAST_START_YEAR
    ):

        return "Mixed"

    return "Mixed"


# ============================================================
# PERIOD ANALYSIS
# ============================================================

def calculate_period_analysis(
    population_df,
    start_year,
    end_year,
    label
):

    period = population_df[
        (
            population_df["Year"]
            >= start_year
        )
        &
        (
            population_df["Year"]
            <= end_year
        )
    ].copy()

    if period.empty:

        return {

            "Period":
                label,

            "Start_Year":
                start_year,

            "End_Year":
                end_year,

            "Status":
                "Insufficient data",

            "Available_Start_Year":
                None,

            "Available_End_Year":
                None

        }

    period = period.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    actual_start_year = int(
        period.iloc[0]["Year"]
    )

    actual_end_year = int(
        period.iloc[-1]["Year"]
    )

    start_population = float(
        period.iloc[0]["Population"]
    )

    end_population = float(
        period.iloc[-1]["Population"]
    )

    absolute_change = (
        end_population
        - start_population
    )

    if start_population != 0:

        percentage_change = (
            absolute_change
            / start_population
            * 100
        )

    else:

        percentage_change = np.nan

    number_of_years = (
        actual_end_year
        - actual_start_year
    )

    if (
        number_of_years > 0
        and start_population > 0
        and end_population > 0
    ):

        cagr = (

            (
                end_population
                / start_population
            )
            **
            (
                1
                / number_of_years
            )
            - 1

        ) * 100

    else:

        cagr = np.nan

    if number_of_years > 0:

        average_annual_change = (
            absolute_change
            / number_of_years
        )

    else:

        average_annual_change = 0

    # ========================================================
    # GROWTH ANALYSIS
    # ========================================================

    growth_period = period[
        period["Growth_Rate"].notna()
    ].copy()

    if not growth_period.empty:

        fastest_index = (
            growth_period[
                "Growth_Rate"
            ].idxmax()
        )

        slowest_index = (
            growth_period[
                "Growth_Rate"
            ].idxmin()
        )

        fastest_row = (
            growth_period.loc[
                fastest_index
            ]
        )

        slowest_row = (
            growth_period.loc[
                slowest_index
            ]
        )

        fastest_year = int(
            fastest_row["Year"]
        )

        fastest_growth = float(
            fastest_row["Growth_Rate"]
        )

        slowest_year = int(
            slowest_row["Year"]
        )

        slowest_growth = float(
            slowest_row["Growth_Rate"]
        )

    else:

        fastest_year = None
        fastest_growth = None

        slowest_year = None
        slowest_growth = None

    # ========================================================
    # SOURCE MIX
    # ========================================================

    source_types = (
        period["Source_Type"]
        .dropna()
        .unique()
        .tolist()
    )

    source_types = sorted(
        source_types
    )

    # ========================================================
    # REQUESTED PERIOD VS AVAILABLE PERIOD
    # ========================================================

    requested_years = (
        end_year
        - start_year
        + 1
    )

    available_years = len(
        period
    )

    # A 100-year request may not have 100 years
    # because official data begins in 1960.
    if available_years < requested_years:

        availability_status = (
            "Partial - available data used"
        )

    else:

        availability_status = (
            "Complete"
        )

    period_type = determine_period_type(
        actual_start_year,
        actual_end_year
    )

    return {

        "Period":
            label,

        "Requested_Start_Year":
            int(start_year),

        "Requested_End_Year":
            int(end_year),

        "Available_Start_Year":
            actual_start_year,

        "Available_End_Year":
            actual_end_year,

        "Requested_Years":
            requested_years,

        "Available_Years":
            available_years,

        "Availability_Status":
            availability_status,

        "Period_Type":
            period_type,

        "Source_Types":
            ", ".join(source_types),

        "Start_Population":
            round(start_population),

        "End_Population":
            round(end_population),

        "Absolute_Change":
            round(absolute_change),

        "Percentage_Change":
            safe_round(
                percentage_change,
                4
            ),

        "CAGR_Percent":
            safe_round(
                cagr,
                4
            ),

        "Average_Annual_Change":
            round(
                average_annual_change
            ),

        "Fastest_Growth_Year":
            fastest_year,

        "Fastest_Growth_Rate":
            safe_round(
                fastest_growth,
                4
            ),

        "Slowest_Growth_Year":
            slowest_year,

        "Slowest_Growth_Rate":
            safe_round(
                slowest_growth,
                4
            )

    }


# ============================================================
# FUTURE MILESTONES
# ============================================================

def calculate_future_milestones(
    population_df
):

    future = population_df[
        (
            population_df["Year"]
            >= FORECAST_START_YEAR
        )
        &
        (
            population_df["Year"]
            <= FORECAST_END_YEAR
        )
    ].copy()

    if future.empty:

        return pd.DataFrame()

    milestones = [

        1_500_000_000,

        1_550_000_000,

        1_600_000_000,

        1_650_000_000,

        1_700_000_000,

        1_750_000_000,

        1_800_000_000,

        1_850_000_000,

        1_900_000_000,

        2_000_000_000

    ]

    records = []

    for target in milestones:

        reached = future[
            future["Population"]
            >= target
        ]

        if reached.empty:

            records.append({

                "Population_Milestone":
                    target,

                "Estimated_Year":
                    None,

                "Status":
                    "Not reached by 2050"

            })

        else:

            first = reached.iloc[0]

            records.append({

                "Population_Milestone":
                    target,

                "Estimated_Year":
                    int(first["Year"]),

                "Status":
                    "Projected"

            })

    return pd.DataFrame(
        records
    )


# ============================================================
# GENERATE RESEARCH INSIGHTS
# ============================================================

def generate_insights(
    population_df
):

    insights = {}

    # ========================================================
    # HISTORICAL TREND
    # ========================================================

    historical = population_df[
        population_df["Source_Type"]
        == "Historical"
    ].copy()

    if not historical.empty:

        first = historical.iloc[0]

        last = historical.iloc[-1]

        historical_change = (

            (
                last["Population"]
                - first["Population"]
            )
            / first["Population"]

        ) * 100

        insights[
            "historical_trend"
        ] = (

            f"Official population increased from "
            f"{first['Population']:,.0f} in "
            f"{int(first['Year'])} to "
            f"{last['Population']:,.0f} in "
            f"{int(last['Year'])}, representing "
            f"an increase of "
            f"{historical_change:.2f}%."

        )

    # ========================================================
    # 2025 ESTIMATE
    # ========================================================

    estimated = population_df[
        population_df["Source_Type"]
        == "Estimated"
    ].copy()

    if not estimated.empty:

        row = estimated.iloc[0]

        insights[
            "estimated_2025"
        ] = (

            f"The forecasting model estimates "
            f"India's 2025 population at "
            f"approximately "
            f"{row['Population']:,.0f}. "
            f"This is a model estimate and is "
            f"not treated as an official "
            f"historical observation."

        )

    else:

        insights[
            "estimated_2025"
        ] = (

            "A 2025 model estimate was not "
            "available in the current forecast "
            "outputs."

        )

    # ========================================================
    # FORECAST TREND
    # ========================================================

    forecast = population_df[
        population_df["Source_Type"]
        == "Forecast"
    ].copy()

    if not forecast.empty:

        first = forecast.iloc[0]

        last = forecast.iloc[-1]

        future_change = (

            (
                last["Population"]
                - first["Population"]
            )
            / first["Population"]

        ) * 100

        insights[
            "forecast_trend"
        ] = (

            f"The model projects India's "
            f"population to change by "
            f"approximately "
            f"{future_change:.2f}% between "
            f"{int(first['Year'])} and "
            f"{int(last['Year'])}."

        )

        first_growth = (
            first["Growth_Rate"]
        )

        last_growth = (
            last["Growth_Rate"]
        )

        insights[
            "growth_dynamics"
        ] = (

            f"Projected annual population "
            f"growth declines from "
            f"approximately "
            f"{first_growth:.3f}% in "
            f"{int(first['Year'])} to "
            f"{last_growth:.3f}% by "
            f"{int(last['Year'])}."

        )

        insights[
            "2050_projection"
        ] = (

            f"The current model projects "
            f"India's population at "
            f"approximately "
            f"{last['Population']:,.0f} "
            f"by 2050."

        )

    # ========================================================
    # GROWTH DECELERATION
    # ========================================================

    if len(forecast) >= 2:

        first_growth = float(
            forecast.iloc[0]["Growth_Rate"]
        )

        last_growth = float(
            forecast.iloc[-1]["Growth_Rate"]
        )

        reduction = (
            first_growth
            - last_growth
        )

        insights[
            "growth_rate_reduction"
        ] = (

            f"The projected annual growth "
            f"rate declines by approximately "
            f"{reduction:.3f} percentage points "
            f"between "
            f"{int(forecast.iloc[0]['Year'])} "
            f"and "
            f"{int(forecast.iloc[-1]['Year'])}."

        )

    return insights


# ============================================================
# BUILD DATA STATUS TABLE
# ============================================================

def build_data_status(
    population_df
):

    records = []

    for source_type, group in (
        population_df.groupby(
            "Source_Type"
        )
    ):

        records.append({

            "Source_Type":
                source_type,

            "Start_Year":
                int(group["Year"].min()),

            "End_Year":
                int(group["Year"].max()),

            "Rows":
                len(group),

            "Data_Status":
                group[
                    "Data_Status"
                ].iloc[0],

            "Source":
                group[
                    "Source"
                ].iloc[0]

        })

    return pd.DataFrame(
        records
    )


# ============================================================
# PRINT PERIOD RESULT
# ============================================================

def print_period_result(
    result
):

    print(
        f"\n--- {result['Period']} ---"
    )

    if (
        result.get("Availability_Status")
        == "Insufficient data"
    ):

        print(
            "Status            : "
            "Insufficient data"
        )

        return

    print(
        f"Period type       : "
        f"{result['Period_Type']}"
    )

    print(
        f"Requested period  : "
        f"{result['Requested_Start_Year']}"
        f"-"
        f"{result['Requested_End_Year']}"
    )

    print(
        f"Available period  : "
        f"{result['Available_Start_Year']}"
        f"-"
        f"{result['Available_End_Year']}"
    )

    print(
        f"Availability      : "
        f"{result['Availability_Status']}"
    )

    print(
        f"Source types      : "
        f"{result['Source_Types']}"
    )

    print(
        f"Start population  : "
        f"{result['Start_Population']:,}"
    )

    print(
        f"End population    : "
        f"{result['End_Population']:,}"
    )

    print(
        f"Absolute change   : "
        f"{result['Absolute_Change']:,}"
    )

    print(
        f"Percentage change : "
        f"{result['Percentage_Change']:.4f}%"
    )

    print(
        f"CAGR              : "
        f"{result['CAGR_Percent']:.4f}%"
    )

    print(
        f"Avg annual change : "
        f"{result['Average_Annual_Change']:,}"
    )

    if (
        result["Fastest_Growth_Year"]
        is not None
    ):

        print(
            f"Fastest growth    : "
            f"{result['Fastest_Growth_Year']} "
            f"("
            f"{result['Fastest_Growth_Rate']:.4f}%"
            f")"
        )

    if (
        result["Slowest_Growth_Year"]
        is not None
    ):

        print(
            f"Slowest growth    : "
            f"{result['Slowest_Growth_Year']} "
            f"("
            f"{result['Slowest_Growth_Rate']:.4f}%"
            f")"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 80
    )

    print(
        "NATIONAL DEMOGRAPHIC ANALYTICS ENGINE"
    )

    print(
        "=" * 80
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

    historical = (
        load_historical_data()
    )

    forecast = (
        load_forecast_data()
    )

    estimated_2025 = (
        load_2025_estimate()
    )

    # ========================================================
    # BUILD UNIFIED DATASET
    # ========================================================

    population_df = (
        build_population_series(
            historical,
            estimated_2025,
            forecast
        )
    )

    # ========================================================
    # VALIDATE
    # ========================================================

    validate_population_series(
        population_df
    )

    print(
        f"\nCoverage: "
        f"{population_df['Year'].min()} - "
        f"{population_df['Year'].max()}"
    )

    print(
        f"Total analytics rows: "
        f"{len(population_df)}"
    )

    # ========================================================
    # SAVE COMPLETE POPULATION ANALYTICS
    # ========================================================

    population_df.to_csv(
        POPULATION_ANALYTICS_FILE,
        index=False
    )

    print(
        "\nPopulation analytics saved:"
    )

    print(
        POPULATION_ANALYTICS_FILE
    )

    # ========================================================
    # DATA STATUS
    # ========================================================

    data_status = (
        build_data_status(
            population_df
        )
    )

    data_status.to_csv(
        DATA_STATUS_FILE,
        index=False
    )

    print(
        "\nData status saved:"
    )

    print(
        DATA_STATUS_FILE
    )

    # ========================================================
    # RESEARCH PERIODS
    # ========================================================
    #
    # These are intentionally defined as requested research
    # windows.
    #
    # 10-year:
    #     2040-2050
    #
    # 20-year:
    #     2030-2050
    #
    # 25-year:
    #     2025-2050
    #
    # 50-year:
    #     2000-2050
    #
    # 100-year:
    #     1950-2050
    #
    # Since official data begins in 1960, the 100-year request
    # will transparently use 1960-2050 instead of inventing
    # 1950 data.
    # ========================================================

    periods = [

        (
            "10-Year",
            2040,
            2050
        ),

        (
            "20-Year",
            2030,
            2050
        ),

        (
            "25-Year",
            2025,
            2050
        ),

        (
            "50-Year",
            2000,
            2050
        ),

        (
            "100-Year",
            1950,
            2050
        )

    ]

    analysis_records = []

    for (
        label,
        start_year,
        end_year
    ) in periods:

        result = (
            calculate_period_analysis(
                population_df,
                start_year,
                end_year,
                label
            )
        )

        analysis_records.append(
            result
        )

        print_period_result(
            result
        )

    # ========================================================
    # SAVE PERIOD ANALYSIS
    # ========================================================

    analysis_df = pd.DataFrame(
        analysis_records
    )

    analysis_df.to_csv(
        RESEARCH_ANALYSIS_FILE,
        index=False
    )

    print(
        "\nResearch period analysis saved:"
    )

    print(
        RESEARCH_ANALYSIS_FILE
    )

    # ========================================================
    # FUTURE MILESTONES
    # ========================================================

    milestones_df = (
        calculate_future_milestones(
            population_df
        )
    )

    milestones_df.to_csv(
        MILESTONES_FILE,
        index=False
    )

    print(
        "\nFuture milestones saved:"
    )

    print(
        MILESTONES_FILE
    )

    # ========================================================
    # INSIGHTS
    # ========================================================

    insights = (
        generate_insights(
            population_df
        )
    )

    print(
        "\n--- RESEARCH INSIGHTS ---"
    )

    for key, text in insights.items():

        print(
            f"\n[{key}]"
        )

        print(
            text
        )

    # ========================================================
    # 2050 SUMMARY
    # ========================================================

    forecast_2050 = population_df[
        population_df["Year"] == 2050
    ]

    if not forecast_2050.empty:

        population_2050 = float(
            forecast_2050.iloc[0][
                "Population"
            ]
        )

        print(
            "\n--- 2050 PROJECTION ---"
        )

        print(
            f"2050 Population : "
            f"{population_2050:,.0f}"
        )

    # ========================================================
    # FINAL RESEARCH REPORT
    # ========================================================

    report = {

        "project":
            "India Population Forecasting",

        "analytics_engine":
            "National Demographic Analytics Engine",

        "coverage": {

            "official_historical":
                "1960-2024",

            "model_estimated":
                "2025",

            "ml_forecast":
                "2026-2050"

        },

        "data_policy": {

            "official_data_modified":
                False,

            "official_historical_cutoff":
                OFFICIAL_LAST_YEAR,

            "estimated_2025_is_official":
                False,

            "forecast_values_modified":
                False,

            "model_retrained":
                False

        },

        "period_analysis":
            analysis_records,

        "data_status":
            data_status.to_dict(
                orient="records"
            ),

        "future_milestones":
            milestones_df.to_dict(
                orient="records"
            ),

        "insights":
            insights

    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nResearch report saved:"
    )

    print(
        REPORT_FILE
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "ANALYTICS ENGINE COMPLETED SUCCESSFULLY"
    )

    print(
        "=" * 80
    )

    print(
        "\nData policy:"
    )

    print(
        "✓ Official WDI datasets were NOT modified."
    )

    print(
        "✓ Official historical data: 1960-2024."
    )

    if estimated_2025 is not None:

        print(
            "✓ 2025 is model-estimated."
        )

    else:

        print(
            "⚠ 2025 estimate unavailable."
        )

    print(
        "✓ ML forecast: 2026-2050."
    )

    print(
        "✓ No model was retrained."
    )

    print(
        "✓ No forecast values were changed."
    )

    print(
        "\nGenerated files:"
    )

    print(
        f"✓ {POPULATION_ANALYTICS_FILE}"
    )

    print(
        f"✓ {DATA_STATUS_FILE}"
    )

    print(
        f"✓ {RESEARCH_ANALYSIS_FILE}"
    )

    print(
        f"✓ {MILESTONES_FILE}"
    )

    print(
        f"✓ {REPORT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
