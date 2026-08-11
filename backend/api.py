# ================================================================
# INDIA POPULATION FORECASTING SYSTEM
# NATIONAL DEMOGRAPHIC INTELLIGENCE API
# ================================================================
#
# This API is the backend gateway for the India Population
# Forecasting / Demographic Intelligence application.
#
# COVERAGE
# --------
# Historical:
#     1960 - latest available historical year
#
# Forecast:
#     2026 - 2050
#
# Overall application:
#     1960 - 2050
#
# IMPORTANT
# ---------
# This API:
#
#   DOES:
#       - Read existing datasets
#       - Read existing ML forecast output
#       - Read analytics
#       - Read intelligence
#       - Build year-specific intelligence
#       - Serve JSON through FastAPI
#       - Provide frontend endpoints
#
#   DOES NOT:
#       - Train the ML model
#       - Retrain the ML model
#       - Modify official datasets
#       - Modify forecast values
#       - Generate a replacement prediction
#       - Modify CSV files
#
# ================================================================


# ================================================================
# IMPORTS
# ================================================================

import json
import math
import os
from contextlib import asynccontextmanager
from typing import Any, Optional

import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# ================================================================
# YEAR INTELLIGENCE SERVICE
# ================================================================
#
# IMPORTANT:
# build_year_intelligence(year) is the main service used by the
# frontend when a user selects a year.
#
# Example:
#
#     build_year_intelligence(2032)
#
#     build_year_intelligence(2040)
#
#     build_year_intelligence(2050)
#
# The API does NOT contain a special case for 2032.
# The requested year is passed dynamically.
#
# ================================================================

try:
    from year_intelligence import build_year_intelligence

except ImportError as exc:

    raise ImportError(
        "Unable to import build_year_intelligence from "
        "backend/year_intelligence.py. "
        "Make sure year_intelligence.py exists and exposes "
        "build_year_intelligence(year)."
    ) from exc


# ================================================================
# PROJECT PATHS
# ================================================================

# backend/
#     api.py
#
# Project root:
#     AI-Population-Forecasting/
#
# Therefore:
#
#     dirname(api.py)
#             -> backend
#
#     dirname(backend)
#             -> project root
#

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ================================================================
# DATASET DIRECTORIES
# ================================================================

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

FORECAST_DIR = os.path.join(
    DATASET_DIR,
    "population_forecast"
)

ANALYTICS_DIR = os.path.join(
    FORECAST_DIR,
    "analytics"
)

INTELLIGENCE_DIR = os.path.join(
    ANALYTICS_DIR,
    "intelligence"
)

SAVED_MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)


# ================================================================
# DATA FILE PATHS
# ================================================================

# ------------------------------------------------
# Historical data
# ------------------------------------------------

CLEAN_DATASET = os.path.join(
    DATASET_DIR,
    "india_clean_dataset.csv"
)

# Fallback in case the clean dataset is unavailable
# but the master dataset exists.
MASTER_DATASET = os.path.join(
    DATASET_DIR,
    "india_master_dataset.csv"
)


# ------------------------------------------------
# Feature dataset
# ------------------------------------------------

FEATURE_DATASET = os.path.join(
    DATASET_DIR,
    "india_features_dataset.csv"
)


# ------------------------------------------------
# Forecast
# ------------------------------------------------

FORECAST_FILE = os.path.join(
    FORECAST_DIR,
    "population_forecast_2026_2050.csv"
)


# ------------------------------------------------
# Analytics
# ------------------------------------------------

ANALYTICS_FILE = os.path.join(
    ANALYTICS_DIR,
    "population_analytics.csv"
)

DATA_STATUS_FILE = os.path.join(
    ANALYTICS_DIR,
    "data_status.csv"
)

RESEARCH_PERIOD_FILE = os.path.join(
    ANALYTICS_DIR,
    "research_period_analysis.csv"
)

FUTURE_MILESTONES_FILE = os.path.join(
    ANALYTICS_DIR,
    "future_milestones.csv"
)


# ------------------------------------------------
# Intelligence
# ------------------------------------------------

UNIFIED_POPULATION_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "unified_population_dataset.csv"
)

YEAR_INSIGHTS_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "year_insights.csv"
)

GROWTH_ANALYSIS_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "growth_analysis.csv"
)

DETECTED_MILESTONES_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "detected_milestones.csv"
)


# ------------------------------------------------
# JSON reports
# ------------------------------------------------

RESEARCH_REPORT_FILE = os.path.join(
    ANALYTICS_DIR,
    "research_report.json"
)

RESEARCH_INSIGHTS_FILE = os.path.join(
    ANALYTICS_DIR,
    "research_insights.json"
)

INTELLIGENCE_REPORT_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "intelligence_report.json"
)


# ------------------------------------------------
# Model metadata
# ------------------------------------------------

MODEL_FEATURES_FILE = os.path.join(
    SAVED_MODEL_DIR,
    "forecast_model_features.csv"
)

SELECTED_MODEL_FILE = os.path.join(
    SAVED_MODEL_DIR,
    "selected_model.txt"
)

MODEL_FILE = os.path.join(
    SAVED_MODEL_DIR,
    "population_forecast_model.pkl"
)


# ================================================================
# GLOBAL DATA CACHE
# ================================================================

DATA: dict[str, Any] = {

    "historical": None,

    "forecast": None,

    "analytics": None,

    "data_status": None,

    "research_periods": None,

    "future_milestones": None,

    "unified": None,

    "year_insights": None,

    "growth_analysis": None,

    "detected_milestones": None,

    "research_report": None,

    "research_insights": None,

    "intelligence_report": None,
}


# ================================================================
# BASIC UTILITIES
# ================================================================

def file_exists(path: str) -> bool:
    """
    Check whether a file exists.
    """

    return os.path.isfile(path)


# ================================================================
# CSV READER
# ================================================================

def read_csv_file(
    path: str,
    required: bool = False
) -> Optional[pd.DataFrame]:
    """
    Safely read a CSV file.

    Parameters
    ----------
    path:
        CSV file path.

    required:
        If True, raise an exception when the file does not exist
        or cannot be read.
    """

    if not file_exists(path):

        if required:

            raise FileNotFoundError(
                f"Required CSV file not found:\n{path}"
            )

        return None

    try:

        df = pd.read_csv(path)

        return df

    except Exception as exc:

        if required:

            raise RuntimeError(
                f"Unable to read CSV file:\n"
                f"{path}\n\n"
                f"Error: {exc}"
            ) from exc

        return None


# ================================================================
# JSON READER
# ================================================================

def read_json_file(
    path: str,
    required: bool = False
) -> Optional[Any]:
    """
    Safely read a JSON file.
    """

    if not file_exists(path):

        if required:

            raise FileNotFoundError(
                f"Required JSON file not found:\n{path}"
            )

        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as exc:

        if required:

            raise RuntimeError(
                f"Unable to read JSON file:\n"
                f"{path}\n\n"
                f"Error: {exc}"
            ) from exc

        return None


# ================================================================
# JSON-SAFE VALUE CONVERSION
# ================================================================

def clean_value(value: Any) -> Any:
    """
    Convert pandas / NumPy values into values that FastAPI can
    safely serialize as JSON.
    """

    if value is None:

        return None

    # Handle pandas NaN / NaT
    try:

        if pd.isna(value):

            return None

    except Exception:

        pass

    # Handle NumPy scalar values
    if hasattr(value, "item"):

        try:

            value = value.item()

        except Exception:

            pass

    # Handle floating-point infinity
    if isinstance(value, float):

        if math.isnan(value):

            return None

        if math.isinf(value):

            return None

    return value


# ================================================================
# RECURSIVE JSON-SAFE CONVERSION
# ================================================================

def make_json_safe(value: Any) -> Any:
    """
    Recursively convert dictionaries, lists, tuples and pandas
    values into JSON-safe Python objects.
    """

    if isinstance(value, dict):

        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):

        return [
            make_json_safe(item)
            for item in value
        ]

    return clean_value(value)


# ================================================================
# DATAFRAME -> RECORDS
# ================================================================

def dataframe_to_records(
    df: Optional[pd.DataFrame]
) -> list[dict[str, Any]]:
    """
    Convert a DataFrame to JSON-safe dictionaries.
    """

    if df is None:

        return []

    if df.empty:

        return []

    clean = df.copy()

    clean = clean.where(
        pd.notna(clean),
        None
    )

    records = clean.to_dict(
        orient="records"
    )

    return make_json_safe(records)


# ================================================================
# DATAFRAME -> SINGLE RECORD
# ================================================================

def dataframe_to_record(
    df: Optional[pd.DataFrame]
) -> Optional[dict[str, Any]]:
    """
    Return the first DataFrame row as a dictionary.
    """

    records = dataframe_to_records(df)

    if not records:

        return None

    return records[0]


# ================================================================
# SAFE INTEGER
# ================================================================

def safe_int(
    value: Any
) -> Optional[int]:
    """
    Safely convert a value to int.
    """

    value = clean_value(value)

    if value is None:

        return None

    try:

        return int(value)

    except Exception:

        return None


# ================================================================
# SAFE FLOAT
# ================================================================

def safe_float(
    value: Any
) -> Optional[float]:
    """
    Safely convert a value to float.
    """

    value = clean_value(value)

    if value is None:

        return None

    try:

        return float(value)

    except Exception:

        return None


# ================================================================
# YEAR VALIDATION
# ================================================================

def validate_year(
    year: int
) -> None:
    """
    Validate a year for the complete application.

    Supported application period:
        1960 - 2050
    """

    if year < 1960 or year > 2050:

        raise HTTPException(
            status_code=400,
            detail=(
                "Year must be between "
                "1960 and 2050."
            )
        )


# ================================================================
# FIND YEAR IN DATAFRAME
# ================================================================

def find_year_row(
    df: Optional[pd.DataFrame],
    year: int
) -> Optional[pd.Series]:
    """
    Return the row belonging to a specific year.
    """

    if df is None:

        return None

    if "Year" not in df.columns:

        return None

    result = df[
        df["Year"] == year
    ]

    if result.empty:

        return None

    return result.iloc[0]


# ================================================================
# LOAD HISTORICAL DATA
# ================================================================

def load_historical_data() -> pd.DataFrame:
    """
    Load historical national population data.

    Primary:
        india_clean_dataset.csv

    Fallback:
        india_master_dataset.csv
    """

    historical = None

    # ------------------------------------------------------------
    # Try clean dataset first
    # ------------------------------------------------------------

    if file_exists(CLEAN_DATASET):

        historical = read_csv_file(
            CLEAN_DATASET,
            required=True
        )

    # ------------------------------------------------------------
    # Fallback to master dataset
    # ------------------------------------------------------------

    elif file_exists(MASTER_DATASET):

        print(
            "⚠ Clean dataset not found."
        )

        print(
            "Using india_master_dataset.csv"
        )

        historical = read_csv_file(
            MASTER_DATASET,
            required=True
        )

    else:

        raise FileNotFoundError(
            "Neither historical dataset was found.\n\n"
            f"Expected:\n"
            f"{CLEAN_DATASET}\n\n"
            f"or:\n"
            f"{MASTER_DATASET}"
        )

    if historical is None:

        raise RuntimeError(
            "Historical dataset could not be loaded."
        )

    # ------------------------------------------------------------
    # Required columns
    # ------------------------------------------------------------

    required_columns = [
        "Year",
        "Population"
    ]

    for column in required_columns:

        if column not in historical.columns:

            raise RuntimeError(
                "Historical dataset is missing "
                f"required column: {column}"
            )

    # ------------------------------------------------------------
    # Clean and sort
    # ------------------------------------------------------------

    historical = historical.copy()

    historical["Year"] = pd.to_numeric(
        historical["Year"],
        errors="coerce"
    )

    historical["Population"] = pd.to_numeric(
        historical["Population"],
        errors="coerce"
    )

    historical = historical.dropna(
        subset=[
            "Year",
            "Population"
        ]
    )

    historical["Year"] = (
        historical["Year"]
        .astype(int)
    )

    historical = historical.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    return historical


# ================================================================
# LOAD FORECAST DATA
# ================================================================

def load_forecast_data() -> pd.DataFrame:
    """
    Load the already-generated ML forecast.
    """

    forecast = read_csv_file(
        FORECAST_FILE,
        required=True
    )

    if forecast is None:

        raise RuntimeError(
            "Forecast dataset could not be loaded."
        )

    required_columns = [
        "Year",
        "Predicted_Population"
    ]

    for column in required_columns:

        if column not in forecast.columns:

            raise RuntimeError(
                "Forecast dataset is missing "
                f"required column: {column}"
            )

    forecast = forecast.copy()

    forecast["Year"] = pd.to_numeric(
        forecast["Year"],
        errors="coerce"
    )

    forecast["Predicted_Population"] = pd.to_numeric(
        forecast["Predicted_Population"],
        errors="coerce"
    )

    forecast = forecast.dropna(
        subset=[
            "Year",
            "Predicted_Population"
        ]
    )

    forecast["Year"] = (
        forecast["Year"]
        .astype(int)
    )

    forecast = forecast.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    return forecast


# ================================================================
# LOAD ALL PIPELINE OUTPUTS
# ================================================================

def load_all_data() -> None:
    """
    Load all existing pipeline outputs into memory.

    No model training happens here.
    No CSV is modified here.
    """

    print()
    print("=" * 70)
    print("LOADING NATIONAL DEMOGRAPHIC DATA")
    print("=" * 70)

    # ------------------------------------------------------------
    # Historical
    # ------------------------------------------------------------

    historical = load_historical_data()

    DATA["historical"] = historical

    print(
        f"✓ Historical data: "
        f"{len(historical)} rows"
    )

    # ------------------------------------------------------------
    # Forecast
    # ------------------------------------------------------------

    forecast = load_forecast_data()

    DATA["forecast"] = forecast

    print(
        f"✓ Forecast data: "
        f"{len(forecast)} rows"
    )

    # ------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------

    DATA["analytics"] = read_csv_file(
        ANALYTICS_FILE
    )

    DATA["data_status"] = read_csv_file(
        DATA_STATUS_FILE
    )

    DATA["research_periods"] = read_csv_file(
        RESEARCH_PERIOD_FILE
    )

    DATA["future_milestones"] = read_csv_file(
        FUTURE_MILESTONES_FILE
    )

    # ------------------------------------------------------------
    # Intelligence datasets
    # ------------------------------------------------------------

    DATA["unified"] = read_csv_file(
        UNIFIED_POPULATION_FILE
    )

    DATA["year_insights"] = read_csv_file(
        YEAR_INSIGHTS_FILE
    )

    DATA["growth_analysis"] = read_csv_file(
        GROWTH_ANALYSIS_FILE
    )

    DATA["detected_milestones"] = read_csv_file(
        DETECTED_MILESTONES_FILE
    )

    # ------------------------------------------------------------
    # JSON reports
    # ------------------------------------------------------------

    DATA["research_report"] = read_json_file(
        RESEARCH_REPORT_FILE
    )

    DATA["research_insights"] = read_json_file(
        RESEARCH_INSIGHTS_FILE
    )

    DATA["intelligence_report"] = read_json_file(
        INTELLIGENCE_REPORT_FILE
    )

    print()
    print("✓ Data loading completed.")


# ================================================================
# VALIDATE DATA
# ================================================================

def validate_loaded_data() -> None:
    """
    Validate core datasets before the API starts.
    """

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    # ------------------------------------------------------------
    # Historical
    # ------------------------------------------------------------

    if historical is None:

        raise RuntimeError(
            "Historical dataset is unavailable."
        )

    if historical.empty:

        raise RuntimeError(
            "Historical dataset is empty."
        )

    if historical["Year"].duplicated().any():

        raise RuntimeError(
            "Historical dataset contains duplicate years."
        )

    if historical["Population"].isna().any():

        raise RuntimeError(
            "Historical dataset contains missing "
            "population values."
        )

    # ------------------------------------------------------------
    # Forecast
    # ------------------------------------------------------------

    if forecast is None:

        raise RuntimeError(
            "Forecast dataset is unavailable."
        )

    if forecast.empty:

        raise RuntimeError(
            "Forecast dataset is empty."
        )

    if forecast["Year"].duplicated().any():

        raise RuntimeError(
            "Forecast dataset contains duplicate years."
        )

    if forecast[
        "Predicted_Population"
    ].isna().any():

        raise RuntimeError(
            "Forecast dataset contains missing "
            "predicted population values."
        )

    print(
        "✓ Historical dataset validated."
    )

    print(
        "✓ Forecast dataset validated."
    )

    print(
        "✓ No duplicate years."
    )

    print(
        "✓ No missing core population values."
    )


# ================================================================
# FASTAPI LIFESPAN
# ================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print()
    print("=" * 70)
    print(
        "INDIA POPULATION FORECASTING"
    )
    print(
        "NATIONAL DEMOGRAPHIC INTELLIGENCE API"
    )
    print("=" * 70)

    print()
    print("Project directory:")
    print(BASE_DIR)

    print()
    print(
        "Loading existing pipeline outputs..."
    )

    load_all_data()

    validate_loaded_data()

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    print()
    print("=" * 70)
    print("API READY")
    print("=" * 70)

    print()

    if historical is not None:

        historical_start = safe_int(
            historical["Year"].min()
        )

        historical_end = safe_int(
            historical["Year"].max()
        )

        print(
            f"Historical coverage: "
            f"{historical_start} - "
            f"{historical_end}"
        )

    if forecast is not None:

        forecast_start = safe_int(
            forecast["Year"].min()
        )

        forecast_end = safe_int(
            forecast["Year"].max()
        )

        print(
            f"Forecast coverage: "
            f"{forecast_start} - "
            f"{forecast_end}"
        )

    print(
        "Application coverage: 1960 - 2050"
    )

    print()
    print("Swagger documentation:")
    print(
        "http://127.0.0.1:8000/docs"
    )

    print()
    print("ReDoc documentation:")
    print(
        "http://127.0.0.1:8000/redoc"
    )

    print()
    print(
        "No model training performed."
    )

    print(
        "No official dataset modified."
    )

    print(
        "No forecast value modified."
    )

    yield

    print()
    print("=" * 70)
    print("API SHUTDOWN")
    print("=" * 70)


# ================================================================
# FASTAPI APPLICATION
# ================================================================

app = FastAPI(
    title=(
        "India Population Forecasting "
        "and Demographic Intelligence API"
    ),

    description=(
        "National demographic intelligence API "
        "for India providing historical population, "
        "machine-learning forecasts, analytics, "
        "milestones, research information and "
        "comprehensive year-specific intelligence "
        "from 1960 to 2050."
    ),

    version="2.0.0",

    lifespan=lifespan
)


# ================================================================
# CORS
# ================================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# ================================================================
# ROOT
# ================================================================

@app.get("/")
def root():

    return {
        "application":
            "India Population Forecasting System",

        "module":
            "National Demographic Intelligence API",

        "version":
            "2.0.0",

        "coverage":
            "1960-2050",

        "status":
            "running",

        "documentation":
            "/docs",

        "main_year_endpoint":
            "/api/intelligence/year/{year}",

        "architecture": [
            "Historical Data",
            "Data Cleaning",
            "Feature Engineering",
            "Machine Learning",
            "Population Forecasting",
            "Analytics",
            "Demographic Intelligence",
            "REST API",
            "React Frontend"
        ]
    }


# ================================================================
# HEALTH CHECK
# ================================================================

@app.get("/api/health")
def health():

    return {

        "status":
            "healthy",

        "historical_loaded":
            DATA["historical"] is not None,

        "forecast_loaded":
            DATA["forecast"] is not None,

        "analytics_loaded":
            DATA["analytics"] is not None,

        "intelligence_loaded":
            DATA["unified"] is not None,

        "year_intelligence_service":
            True,

        "coverage":
            "1960-2050"
    }


# ================================================================
# SYSTEM STATUS
# ================================================================

@app.get("/api/status")
def system_status():

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    return {

        "system":
            "India Population Forecasting",

        "module":
            "National Demographic Intelligence API",

        "status":
            "operational",

        "coverage": {

            "application_start":
                1960,

            "application_end":
                2050,

            "historical_start":
                safe_int(
                    historical["Year"].min()
                ) if historical is not None else None,

            "historical_end":
                safe_int(
                    historical["Year"].max()
                ) if historical is not None else None,

            "forecast_start":
                safe_int(
                    forecast["Year"].min()
                ) if forecast is not None else None,

            "forecast_end":
                safe_int(
                    forecast["Year"].max()
                ) if forecast is not None else None
        },

        "datasets": {

            "historical":
                len(historical)
                if historical is not None
                else 0,

            "forecast":
                len(forecast)
                if forecast is not None
                else 0,

            "analytics":
                len(DATA["analytics"])
                if DATA["analytics"] is not None
                else 0,

            "intelligence":
                len(DATA["unified"])
                if DATA["unified"] is not None
                else 0
        },

        "ml_model": {

            "loaded":
                file_exists(
                    MODEL_FILE
                ),

            "feature_metadata_available":
                file_exists(
                    MODEL_FEATURES_FILE
                ),

            "selected_model_metadata":
                file_exists(
                    SELECTED_MODEL_FILE
                )
        },

        "supported_scopes": {

            "international":
                "Coming Soon",

            "national":
                "Available",

            "state":
                "Coming Soon",

            "district":
                "Coming Soon",

            "city":
                "Coming Soon",

            "village":
                "Coming Soon"
        }
    }


# ================================================================
# DASHBOARD SUMMARY
# ================================================================

@app.get("/api/dashboard/summary")
def dashboard_summary():

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    if historical is None:

        raise HTTPException(
            status_code=503,
            detail="Historical data unavailable."
        )

    if forecast is None:

        raise HTTPException(
            status_code=503,
            detail="Forecast data unavailable."
        )

    historical_latest = (
        historical
        .sort_values("Year")
        .iloc[-1]
    )

    forecast_first = (
        forecast
        .sort_values("Year")
        .iloc[0]
    )

    forecast_last = (
        forecast
        .sort_values("Year")
        .iloc[-1]
    )

    latest_population = safe_float(
        historical_latest["Population"]
    )

    first_forecast_population = safe_float(
        forecast_first[
            "Predicted_Population"
        ]
    )

    final_forecast_population = safe_float(
        forecast_last[
            "Predicted_Population"
        ]
    )

    forecast_growth = None

    if (
        first_forecast_population is not None
        and final_forecast_population is not None
        and first_forecast_population != 0
    ):

        forecast_growth = (

            (
                final_forecast_population
                - first_forecast_population
            )
            /
            first_forecast_population

        ) * 100

    return {

        "latest_official_population": {

            "year":
                safe_int(
                    historical_latest["Year"]
                ),

            "population":
                latest_population
        },

        "first_forecast": {

            "year":
                safe_int(
                    forecast_first["Year"]
                ),

            "population":
                first_forecast_population
        },

        "final_forecast": {

            "year":
                safe_int(
                    forecast_last["Year"]
                ),

            "population":
                final_forecast_population
        },

        "forecast_period_growth_percent":
            safe_float(
                forecast_growth
            ),

        "coverage":
            "1960-2050",

        "data_policy": {

            "historical":
                "Historical dataset",

            "estimated":
                "Model-estimated where applicable",

            "forecast":
                "Machine-learning forecast",

            "year_intelligence":
                "Comprehensive demographic intelligence"
        }
    }


# ================================================================
# HISTORICAL POPULATION
# ================================================================

@app.get("/api/population/historical")
def historical_population(

    start_year: Optional[int] = Query(
        default=None,
        ge=1960,
        le=2050
    ),

    end_year: Optional[int] = Query(
        default=None,
        ge=1960,
        le=2050
    )
):

    df = DATA["historical"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail="Historical data unavailable."
        )

    result = df.copy()

    if start_year is not None:

        result = result[
            result["Year"] >= start_year
        ]

    if end_year is not None:

        result = result[
            result["Year"] <= end_year
        ]

    return {

        "count":
            len(result),

        "source_type":
            "Historical",

        "data":
            dataframe_to_records(result)
    }


# ================================================================
# FORECAST POPULATION
# ================================================================

@app.get("/api/population/forecast")
def population_forecast(

    start_year: Optional[int] = Query(
        default=None,
        ge=2026,
        le=2050
    ),

    end_year: Optional[int] = Query(
        default=None,
        ge=2026,
        le=2050
    )
):

    df = DATA["forecast"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail="Forecast data unavailable."
        )

    result = df.copy()

    if start_year is not None:

        result = result[
            result["Year"] >= start_year
        ]

    if end_year is not None:

        result = result[
            result["Year"] <= end_year
        ]

    return {

        "count":
            len(result),

        "source_type":
            "ML Forecast",

        "data":
            dataframe_to_records(result)
    }


# ================================================================
# SPECIFIC YEAR - BASIC POPULATION DATA
# ================================================================
#
# This endpoint is intentionally separate from the comprehensive
# intelligence endpoint.
#
# Frontend can use:
#
#     /api/population/year/2032
#
# for a lightweight population lookup.
#
# ================================================================

@app.get("/api/population/year/{year}")
def population_year(year: int):

    validate_year(year)

    unified = DATA["unified"]

    # ------------------------------------------------------------
    # Try unified intelligence dataset first
    # ------------------------------------------------------------

    if unified is not None:

        row = find_year_row(
            unified,
            year
        )

        if row is not None:

            return make_json_safe(
                row.to_dict()
            )

    # ------------------------------------------------------------
    # Historical fallback
    # ------------------------------------------------------------

    historical = DATA["historical"]

    if historical is not None:

        row = find_year_row(
            historical,
            year
        )

        if row is not None:

            record = row.to_dict()

            record["Source_Type"] = (
                "Historical"
            )

            record["Data_Status"] = (
                "Historical Data"
            )

            return make_json_safe(
                record
            )

    # ------------------------------------------------------------
    # Forecast fallback
    # ------------------------------------------------------------

    forecast = DATA["forecast"]

    if forecast is not None:

        row = find_year_row(
            forecast,
            year
        )

        if row is not None:

            record = row.to_dict()

            predicted = (
                record.get(
                    "Predicted_Population"
                )
            )

            record["Population"] = predicted

            record["Source_Type"] = (
                "Forecast"
            )

            record["Data_Status"] = (
                "ML Forecast"
            )

            return make_json_safe(
                record
            )

    raise HTTPException(
        status_code=404,
        detail=(
            f"No population data available "
            f"for year {year}."
        )
    )


# ================================================================
# ⭐ COMPREHENSIVE YEAR INTELLIGENCE
# ================================================================
#
# THIS IS THE MOST IMPORTANT ENDPOINT FOR THE NEW FRONTEND.
#
# The user selects a year:
#
#     2032
#
# Frontend calls:
#
#     GET /api/intelligence/year/2032
#
# The API then executes:
#
#     build_year_intelligence(2032)
#
# The same mechanism works for:
#
#     1960
#     1975
#     1990
#     2000
#     2025
#     2032
#     2040
#     2050
#
# There is NO hardcoded 2032 logic.
#
# ================================================================

@app.get("/api/intelligence/year/{year}")
def comprehensive_year_report(year: int):
    """
    Return a complete demographic intelligence report
    for the selected year.

    Supported:
        1960 - 2050
    """

    # ------------------------------------------------------------
    # Validate year
    # ------------------------------------------------------------

    validate_year(year)

    # ------------------------------------------------------------
    # Call the actual intelligence engine
    # ------------------------------------------------------------

    try:

        report = build_year_intelligence(
            year
        )

        # --------------------------------------------------------
        # Make absolutely sure the returned object is JSON safe
        # --------------------------------------------------------

        return make_json_safe(
            report
        )

    # ------------------------------------------------------------
    # Year not available
    # ------------------------------------------------------------

    except LookupError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    # ------------------------------------------------------------
    # Invalid data / validation problem
    # ------------------------------------------------------------

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    # ------------------------------------------------------------
    # Unexpected failure
    # ------------------------------------------------------------

    except Exception as exc:

        print()
        print(
            "YEAR INTELLIGENCE ERROR"
        )

        print(
            f"Year: {year}"
        )

        print(
            f"Error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to build year intelligence "
                f"report for year {year}: {exc}"
            )
        ) from exc


# ================================================================
# LEGACY / LIGHTWEIGHT YEAR INTELLIGENCE
# ================================================================
#
# Kept as a separate endpoint so existing frontend components
# that only need year_insights.csv do not break.
#
# New frontend should prefer:
#
#     /api/intelligence/year/{year}
#
# ================================================================

@app.get("/api/intelligence/year-summary/{year}")
def year_intelligence_summary(year: int):

    validate_year(year)

    insights = DATA["year_insights"]

    if insights is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Year intelligence summary "
                "is unavailable."
            )
        )

    result = insights[
        insights["Year"] == year
    ]

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No intelligence summary "
                f"available for year {year}."
            )
        )

    return make_json_safe(
        result.iloc[0].to_dict()
    )


# ================================================================
# GROWTH ANALYSIS
# ================================================================

@app.get("/api/analytics/growth")
def growth_analysis():

    df = DATA["growth_analysis"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail="Growth analysis unavailable."
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# POPULATION ANALYTICS
# ================================================================

@app.get("/api/analytics/population")
def population_analytics():

    df = DATA["analytics"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Population analytics unavailable."
            )
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# RESEARCH PERIODS
# ================================================================

@app.get("/api/research/periods")
def research_periods():

    df = DATA["research_periods"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Research period analysis unavailable."
            )
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# MILESTONES
# ================================================================

@app.get("/api/milestones")
def milestones():

    df = DATA["detected_milestones"]

    if df is None:

        df = DATA["future_milestones"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Population milestones unavailable."
            )
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# FUTURE MILESTONES
# ================================================================

@app.get("/api/milestones/future")
def future_milestones():

    df = DATA["future_milestones"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Future milestones unavailable."
            )
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# RESEARCH INSIGHTS
# ================================================================

@app.get("/api/research/insights")
def research_insights():

    data = DATA["research_insights"]

    if data is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Research insights unavailable."
            )
        )

    return make_json_safe(
        data
    )


# ================================================================
# RESEARCH REPORT
# ================================================================

@app.get("/api/research/report")
def research_report():

    data = DATA["research_report"]

    if data is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Research report unavailable."
            )
        )

    return make_json_safe(
        data
    )


# ================================================================
# GLOBAL INTELLIGENCE REPORT
# ================================================================

@app.get("/api/intelligence/report")
def intelligence_report():

    data = DATA["intelligence_report"]

    if data is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Intelligence report unavailable."
            )
        )

    return make_json_safe(
        data
    )


# ================================================================
# UNIFIED POPULATION DATA
# ================================================================

@app.get("/api/intelligence/population")
def unified_population(

    start_year: Optional[int] = Query(
        default=None,
        ge=1960,
        le=2050
    ),

    end_year: Optional[int] = Query(
        default=None,
        ge=1960,
        le=2050
    )
):

    df = DATA["unified"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Unified population dataset "
                "is unavailable."
            )
        )

    result = df.copy()

    if start_year is not None:

        result = result[
            result["Year"] >= start_year
        ]

    if end_year is not None:

        result = result[
            result["Year"] <= end_year
        ]

    return {

        "count":
            len(result),

        "data":
            dataframe_to_records(result)
    }


# ================================================================
# DATA STATUS
# ================================================================

@app.get("/api/data/status")
def data_status():

    df = DATA["data_status"]

    if df is None:

        raise HTTPException(
            status_code=503,
            detail="Data status unavailable."
        )

    return {

        "count":
            len(df),

        "data":
            dataframe_to_records(df)
    }


# ================================================================
# MODEL INFORMATION
# ================================================================

@app.get("/api/model/info")
def model_info():

    model_exists = file_exists(
        MODEL_FILE
    )

    features = None

    # ------------------------------------------------------------
    # Feature metadata
    # ------------------------------------------------------------

    if file_exists(
        MODEL_FEATURES_FILE
    ):

        try:

            feature_df = pd.read_csv(
                MODEL_FEATURES_FILE
            )

            features = (
                dataframe_to_records(
                    feature_df
                )
            )

        except Exception:

            features = None

    # ------------------------------------------------------------
    # Selected model
    # ------------------------------------------------------------

    selected_model = None

    if file_exists(
        SELECTED_MODEL_FILE
    ):

        try:

            with open(
                SELECTED_MODEL_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                selected_model = (
                    file.read()
                    .strip()
                )

        except Exception:

            selected_model = None

    return {

        "model_exists":
            model_exists,

        "model_file":
            MODEL_FILE,

        "selected_model":
            selected_model,

        "feature_metadata":
            features,

        "prediction_horizon":
            "2026-2050",

        "application_horizon":
            "1960-2050",

        "note":
            (
                "The API serves an already-trained "
                "model and does not retrain it."
            )
    }


# ================================================================
# DASHBOARD CHART DATA
# ================================================================

@app.get("/api/dashboard/chart")
def dashboard_chart():

    unified = DATA["unified"]

    if unified is None:

        raise HTTPException(
            status_code=503,
            detail="Unified data unavailable."
        )

    desired_columns = [
        "Year",
        "Population",
        "Source_Type",
        "Data_Status"
    ]

    columns = [
        column
        for column in desired_columns
        if column in unified.columns
    ]

    result = unified[
        columns
    ].copy()

    return {

        "data":
            dataframe_to_records(
                result
            )
    }


# ================================================================
# YEAR RANGE
# ================================================================

@app.get("/api/year-range")
def year_range():

    unified = DATA["unified"]

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    # ------------------------------------------------------------
    # Prefer unified dataset
    # ------------------------------------------------------------

    if unified is not None and not unified.empty:

        return {

            "start_year":
                safe_int(
                    unified["Year"].min()
                ),

            "end_year":
                safe_int(
                    unified["Year"].max()
                ),

            "total_years":
                int(
                    unified["Year"].nunique()
                )
        }

    # ------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------

    years = []

    if historical is not None:

        years.extend(
            historical["Year"]
            .dropna()
            .astype(int)
            .tolist()
        )

    if forecast is not None:

        years.extend(
            forecast["Year"]
            .dropna()
            .astype(int)
            .tolist()
        )

    if not years:

        raise HTTPException(
            status_code=503,
            detail="Year range unavailable."
        )

    years = sorted(
        set(years)
    )

    return {

        "start_year":
            years[0],

        "end_year":
            years[-1],

        "total_years":
            len(years)
    }


# ================================================================
# SEARCH YEAR
# ================================================================

@app.get("/api/search")
def search_year(

    year: int = Query(
        ...,
        ge=1960,
        le=2050
    )
):

    response = {

        "year":
            year,

        "population":
            None,

        "source_type":
            None,

        "data_status":
            None,

        "intelligence":
            None
    }

    # ------------------------------------------------------------
    # Unified population
    # ------------------------------------------------------------

    unified = DATA["unified"]

    if unified is not None:

        row = find_year_row(
            unified,
            year
        )

        if row is not None:

            if "Population" in row:

                response["population"] = (
                    clean_value(
                        row["Population"]
                    )
                )

            if "Source_Type" in row:

                response["source_type"] = (
                    clean_value(
                        row["Source_Type"]
                    )
                )

            if "Data_Status" in row:

                response["data_status"] = (
                    clean_value(
                        row["Data_Status"]
                    )
                )

    # ------------------------------------------------------------
    # Year insight summary
    # ------------------------------------------------------------

    insights = DATA["year_insights"]

    if insights is not None:

        row = find_year_row(
            insights,
            year
        )

        if row is not None:

            response["intelligence"] = (
                make_json_safe(
                    row.to_dict()
                )
            )

    # ------------------------------------------------------------
    # If nothing found
    # ------------------------------------------------------------

    if (
        response["population"] is None
        and response["intelligence"] is None
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                f"No information found "
                f"for year {year}."
            )
        )

    return response


# ================================================================
# ⭐ YEAR INTELLIGENCE METADATA
# ================================================================
#
# Lightweight endpoint useful for the frontend before loading
# the complete report.
#
# ================================================================

@app.get("/api/intelligence/year-meta/{year}")
def year_intelligence_meta(year: int):

    validate_year(year)

    historical = DATA["historical"]

    forecast = DATA["forecast"]

    historical_row = find_year_row(
        historical,
        year
    )

    forecast_row = find_year_row(
        forecast,
        year
    )

    # ------------------------------------------------------------
    # Historical year
    # ------------------------------------------------------------

    if historical_row is not None:

        return {

            "year":
                year,

            "available":
                True,

            "data_type":
                "historical",

            "source_type":
                "Historical",

            "population":
                clean_value(
                    historical_row[
                        "Population"
                    ]
                ),

            "message":
                (
                    "Historical population data "
                    "is available for this year."
                )
        }

    # ------------------------------------------------------------
    # Forecast year
    # ------------------------------------------------------------

    if forecast_row is not None:

        return {

            "year":
                year,

            "available":
                True,

            "data_type":
                "forecast",

            "source_type":
                "ML Forecast",

            "population":
                clean_value(
                    forecast_row[
                        "Predicted_Population"
                    ]
                ),

            "message":
                (
                    "Machine-learning population "
                    "forecast is available for this year."
                )
        }

    # ------------------------------------------------------------
    # No data
    # ------------------------------------------------------------

    return {

        "year":
            year,

        "available":
            False,

        "data_type":
            None,

        "source_type":
            None,

        "population":
            None,

        "message":
            (
                "No population record is available "
                "for this year."
            )
    }


# ================================================================
# SYSTEM RELOAD
# ================================================================
#
# This reloads existing files from disk.
#
# It DOES NOT:
#     - train model
#     - alter datasets
#     - alter forecasts
#
# ================================================================

@app.post("/api/system/reload")
def reload_data():

    try:

        load_all_data()

        validate_loaded_data()

        return {

            "status":
                "success",

            "message":
                (
                    "Existing pipeline outputs "
                    "were reloaded successfully."
                ),

            "warning":
                (
                    "No source dataset or forecast "
                    "was modified."
                )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# ================================================================
# RUN DIRECTLY
# ================================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )