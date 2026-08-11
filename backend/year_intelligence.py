"""
Year Intelligence Service
==========================

Builds a comprehensive national demographic intelligence response
for a selected year.

IMPORTANT:
- Does NOT retrain the ML model.
- Does NOT modify official WDI data.
- Does NOT modify forecast files.
- Does NOT claim that demographic indicators are ML forecasts.
- Keeps forecast values separate from latest available demographic context.

Project scope:
India / National level only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import json
import math

import pandas as pd


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"

MASTER_DATASET = DATASET_DIR / "india_master_dataset.csv"

UNIFIED_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "analytics"
    / "intelligence"
    / "unified_population_dataset.csv"
)

YEAR_INSIGHTS_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "analytics"
    / "intelligence"
    / "year_insights.csv"
)

GROWTH_ANALYSIS_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "analytics"
    / "intelligence"
    / "growth_analysis.csv"
)

MILESTONES_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "analytics"
    / "intelligence"
    / "detected_milestones.csv"
)

FUTURE_MILESTONES_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "analytics"
    / "future_milestones.csv"
)

MODEL_EVALUATION_DATASET = (
    DATASET_DIR
    / "population_forecast"
    / "evaluation"
    / "model_evaluation_summary.csv"
)

BACKTEST_2010_2020 = (
    DATASET_DIR
    / "population_forecast"
    / "backtest_2010_2020.csv"
)

BACKTEST_2015_2024 = (
    DATASET_DIR
    / "population_forecast"
    / "backtest_2015_2024.csv"
)

BACKTEST_SUMMARY = (
    DATASET_DIR
    / "population_forecast"
    / "backtest_summary.csv"
)


# ---------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------

FORECAST_START = 2026
FORECAST_END = 2050

HISTORICAL_START = 1960
HISTORICAL_END = 2024

ESTIMATED_YEAR = 2025

DEMOGRAPHIC_COLUMNS = [
    "Age_0_14",
    "Age_15_64",
    "Rural_Population",
    "Labor_Force_Participation",
    "Birth_Rate",
    "Death_Rate",
    "Fertility_Rate",
    "GDP_Growth",
    "Infant_Mortality",
    "Age_65_Plus",
    "Life_Expectancy",
    "Literacy_Rate",
    "Net_Migration",
    "Population_Density",
    "Urban_Population",
]


# Human-readable metadata for the demographic indicators.
INDICATOR_METADATA = {
    "Age_0_14": {
        "label": "Population age 0–14",
        "unit": "% of total population",
        "category": "Age Structure",
    },
    "Age_15_64": {
        "label": "Population age 15–64",
        "unit": "% of total population",
        "category": "Age Structure",
    },
    "Age_65_Plus": {
        "label": "Population age 65+",
        "unit": "% of total population",
        "category": "Age Structure",
    },
    "Rural_Population": {
        "label": "Rural population",
        "unit": "people",
        "category": "Settlement",
    },
    "Urban_Population": {
        "label": "Urban population",
        "unit": "% of total population",
        "category": "Settlement",
    },
    "Labor_Force_Participation": {
        "label": "Labor force participation",
        "unit": "% of population ages 15+",
        "category": "Workforce",
    },
    "Birth_Rate": {
        "label": "Birth rate",
        "unit": "births per 1,000 people",
        "category": "Vital Statistics",
    },
    "Death_Rate": {
        "label": "Death rate",
        "unit": "deaths per 1,000 people",
        "category": "Vital Statistics",
    },
    "Fertility_Rate": {
        "label": "Fertility rate",
        "unit": "births per woman",
        "category": "Fertility",
    },
    "GDP_Growth": {
        "label": "GDP growth",
        "unit": "%",
        "category": "Economy",
    },
    "Infant_Mortality": {
        "label": "Infant mortality",
        "unit": "per 1,000 live births",
        "category": "Health",
    },
    "Life_Expectancy": {
        "label": "Life expectancy",
        "unit": "years",
        "category": "Health",
    },
    "Literacy_Rate": {
        "label": "Literacy rate",
        "unit": "% of population",
        "category": "Education",
    },
    "Net_Migration": {
        "label": "Net migration",
        "unit": "people",
        "category": "Migration",
    },
    "Population_Density": {
        "label": "Population density",
        "unit": "people per km²",
        "category": "Population",
    },
}


# ---------------------------------------------------------------------
# SAFE HELPERS
# ---------------------------------------------------------------------

def _safe_float(value: Any) -> Optional[float]:
    """Convert a value to float or return None."""
    if value is None:
        return None

    try:
        number = float(value)

        if math.isnan(number) or math.isinf(number):
            return None

        return number

    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """Convert a value to int or return None."""
    number = _safe_float(value)

    if number is None:
        return None

    return int(number)


def _clean_value(value: Any) -> Any:
    """Convert pandas/numpy values into JSON-safe Python values."""
    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    """Clean an entire dictionary."""
    return {
        key: _clean_value(value)
        for key, value in record.items()
    }


def _load_csv(path: Path) -> Optional[pd.DataFrame]:
    """Safely load a CSV."""
    if not path.exists():
        return None

    try:
        df = pd.read_csv(path)

        if "Year" in df.columns:
            df["Year"] = pd.to_numeric(
                df["Year"],
                errors="coerce",
            )

        return df

    except Exception:
        return None


def _year_row(
    df: Optional[pd.DataFrame],
    year: int,
) -> Optional[pd.Series]:

    if df is None or "Year" not in df.columns:
        return None

    result = df[df["Year"] == year]

    if result.empty:
        return None

    return result.iloc[0]


def _latest_available_row(
    df: Optional[pd.DataFrame],
    year: int,
) -> Optional[pd.Series]:

    if df is None or "Year" not in df.columns:
        return None

    eligible = df[df["Year"] <= year].copy()

    if eligible.empty:
        return None

    eligible = eligible.sort_values("Year")

    return eligible.iloc[-1]


# ---------------------------------------------------------------------
# SOURCE CLASSIFICATION
# ---------------------------------------------------------------------

def _population_classification(year: int) -> dict[str, Any]:

    if year <= HISTORICAL_END:
        return {
            "classification": "Historical",
            "status": "Official Historical",
            "label": "Official historical data",
            "is_forecast": False,
        }

    if year == ESTIMATED_YEAR:
        return {
            "classification": "Estimated",
            "status": "Model Estimated",
            "label": "Model-estimated year",
            "is_forecast": False,
        }

    if FORECAST_START <= year <= FORECAST_END:
        return {
            "classification": "Forecast",
            "status": "ML Forecast",
            "label": "Machine-learning forecast",
            "is_forecast": True,
        }

    return {
        "classification": "Unavailable",
        "status": "Unavailable",
        "label": "No supported population value",
        "is_forecast": False,
    }


# ---------------------------------------------------------------------
# POPULATION INFORMATION
# ---------------------------------------------------------------------

def _get_population_information(
    year: int,
    unified: Optional[pd.DataFrame],
) -> dict[str, Any]:

    row = _year_row(unified, year)

    if row is None:
        return {
            "available": False,
            "year": year,
            "classification": "Unavailable",
            "status": "Unavailable",
        }

    classification = _population_classification(year)

    population = _safe_float(
        row.get("Population")
    )

    population_change = _safe_float(
        row.get("Population_Change")
    )

    growth_rate = _safe_float(
        row.get("Growth_Rate")
    )

    previous_population = _safe_float(
        row.get("Previous_Population")
    )

    return {
        "available": population is not None,
        "year": year,
        "population": population,
        "population_change": population_change,
        "growth_rate_percent": growth_rate,
        "previous_population": previous_population,
        "classification": classification["classification"],
        "status": classification["status"],
        "label": classification["label"],
        "source": _clean_value(
            row.get("Source")
        ),
        "source_file": _clean_value(
            row.get("Source_File")
        ),
    }


# ---------------------------------------------------------------------
# LATEST DEMOGRAPHIC CONTEXT
# ---------------------------------------------------------------------

def _get_demographic_context(
    year: int,
    master: Optional[pd.DataFrame],
) -> dict[str, Any]:

    if master is None:
        return {
            "available": False,
            "message": (
                "Demographic master dataset is unavailable."
            ),
            "indicators": [],
        }

    row = _latest_available_row(
        master,
        year,
    )

    if row is None:
        return {
            "available": False,
            "message": (
                "No demographic context is available "
                "for this year."
            ),
            "indicators": [],
        }

    context_year = _safe_int(
        row.get("Year")
    )

    indicators = []

    for column in DEMOGRAPHIC_COLUMNS:

        if column not in master.columns:
            continue

        value = _safe_float(
            row.get(column)
        )

        if value is None:
            continue

        metadata = INDICATOR_METADATA.get(
            column,
            {},
        )

        indicators.append({
            "key": column,
            "label": metadata.get(
                "label",
                column.replace("_", " "),
            ),
            "value": value,
            "unit": metadata.get(
                "unit",
                "",
            ),
            "category": metadata.get(
                "category",
                "Demographics",
            ),
            "source_year": context_year,
            "source_status": (
                "Latest available demographic "
                "context"
            ),
            "is_forecast": False,
        })

    if context_year == year:
        message = (
            "Demographic indicators are available "
            "for the selected year."
        )
    else:
        message = (
            f"Demographic indicators are shown "
            f"from the latest available year "
            f"({context_year}), because the population "
            f"forecast model does not independently "
            f"forecast these indicators."
        )

    return {
        "available": len(indicators) > 0,
        "source_year": context_year,
        "source_dataset": "india_master_dataset.csv",
        "message": message,
        "indicators": indicators,
    }


# ---------------------------------------------------------------------
# YEAR INTELLIGENCE
# ---------------------------------------------------------------------

def _get_year_intelligence(
    year: int,
    year_insights: Optional[pd.DataFrame],
) -> dict[str, Any]:

    row = _year_row(
        year_insights,
        year,
    )

    if row is None:
        return {
            "available": False,
            "insights": {},
        }

    record = _clean_record(
        row.to_dict()
    )

    # Remove Year because it is already represented
    # by the parent response.
    record.pop("Year", None)

    return {
        "available": True,
        "insights": record,
    }


# ---------------------------------------------------------------------
# MILESTONES
# ---------------------------------------------------------------------

def _get_milestones(
    year: int,
    detected: Optional[pd.DataFrame],
    future: Optional[pd.DataFrame],
) -> list[dict[str, Any]]:

    frames = []

    for df in [detected, future]:

        if df is None or "Year" not in df.columns:
            continue

        result = df[
            df["Year"] == year
        ]

        if not result.empty:
            frames.append(result)

    if not frames:
        return []

    combined = pd.concat(
        frames,
        ignore_index=True,
    )

    records = []

    for record in combined.to_dict(
        orient="records"
    ):
        records.append(
            _clean_record(record)
        )

    return records


# ---------------------------------------------------------------------
# GROWTH CONTEXT
# ---------------------------------------------------------------------

def _get_growth_context(
    year: int,
    growth_analysis: Optional[pd.DataFrame],
) -> dict[str, Any]:

    row = _year_row(
        growth_analysis,
        year,
    )

    if row is None:
        return {
            "available": False,
            "data": {},
        }

    record = _clean_record(
        row.to_dict()
    )

    record.pop("Year", None)

    return {
        "available": True,
        "data": record,
    }


# ---------------------------------------------------------------------
# MODEL RELIABILITY
# ---------------------------------------------------------------------

def _read_model_evaluation() -> dict[str, Any]:

    result: dict[str, Any] = {
        "model": "Linear Regression",
        "evaluation_available": False,
        "comparison": [],
        "backtesting": [],
        "interpretation": (
            "Forecasts are model estimates and "
            "should not be interpreted as certainty."
        ),
    }

    evaluation = _load_csv(
        MODEL_EVALUATION_DATASET
    )

    if evaluation is not None:

        records = []

        for record in evaluation.to_dict(
            orient="records"
        ):
            records.append(
                _clean_record(record)
            )

        result["evaluation_available"] = (
            len(records) > 0
        )

        result["comparison"] = records

    backtest_summary = _load_csv(
        BACKTEST_SUMMARY
    )

    if backtest_summary is not None:

        records = []

        for record in backtest_summary.to_dict(
            orient="records"
        ):
            records.append(
                _clean_record(record)
            )

        result["backtesting"] = records

    # If the summary file is unavailable, use the
    # project's validated backtest files directly.
    if not result["backtesting"]:

        for path, period in [
            (
                BACKTEST_2010_2020,
                "2010-2020",
            ),
            (
                BACKTEST_2015_2024,
                "2015-2024",
            ),
        ]:

            df = _load_csv(path)

            if df is None:
                continue

            numeric_columns = [
                column
                for column in [
                    "MAE",
                    "RMSE",
                    "R2",
                    "MPE",
                    "R²",
                ]
                if column in df.columns
            ]

            if numeric_columns:

                records = []

                for record in df.to_dict(
                    orient="records"
                ):
                    cleaned = _clean_record(
                        record
                    )
                    cleaned["period"] = period
                    records.append(cleaned)

                result["backtesting"].extend(
                    records
                )

    return result


# ---------------------------------------------------------------------
# POLICY-ORIENTED INTERPRETATION
# ---------------------------------------------------------------------

def _build_policy_signals(
    year: int,
    population: dict[str, Any],
    demographics: dict[str, Any],
) -> list[dict[str, Any]]:

    signals = []

    if not population.get("available"):
        return signals

    growth = population.get(
        "growth_rate_percent"
    )

    if growth is not None:

        if growth < 0.5:
            signals.append({
                "type": "growth_slowdown",
                "title": "Low population growth",
                "description": (
                    "The projected annual population "
                    "growth rate is below 0.5%, indicating "
                    "a substantially slower growth phase "
                    "than India's earlier demographic history."
                ),
                "policy_relevance": (
                    "Long-term planning may increasingly "
                    "shift from managing rapid population "
                    "expansion toward ageing, workforce "
                    "composition and productivity."
                ),
            })

        elif growth < 1.0:
            signals.append({
                "type": "moderate_growth",
                "title": "Moderating population growth",
                "description": (
                    "Population is still projected to grow, "
                    "but at a relatively moderate annual rate."
                ),
                "policy_relevance": (
                    "Planning remains important for employment, "
                    "infrastructure, health and education while "
                    "population growth gradually decelerates."
                ),
            })

        else:
            signals.append({
                "type": "higher_growth",
                "title": "Relatively higher population growth",
                "description": (
                    "The projected annual growth rate remains "
                    "above 1%."
                ),
                "policy_relevance": (
                    "Population expansion can increase demand "
                    "for employment, housing, healthcare, "
                    "education and infrastructure."
                ),
            })

    # Age-structure signals from latest available context.
    indicator_map = {
        item["key"]: item
        for item in demographics.get(
            "indicators",
            []
        )
    }

    age_65 = indicator_map.get(
        "Age_65_Plus"
    )

    if age_65 and age_65.get("value") is not None:

        value = age_65["value"]

        if value >= 7:
            signals.append({
                "type": "ageing",
                "title": "Ageing pressure",
                "description": (
                    f"The latest available demographic "
                    f"context places the 65+ population "
                    f"share at approximately {value:.1f}%."
                ),
                "policy_relevance": (
                    "Population ageing has implications for "
                    "healthcare, pensions, social protection "
                    "and the future dependency structure."
                ),
            })

    age_15_64 = indicator_map.get(
        "Age_15_64"
    )

    if age_15_64 and age_15_64.get("value") is not None:

        value = age_15_64["value"]

        if value >= 60:
            signals.append({
                "type": "working_age",
                "title": "Large working-age share",
                "description": (
                    f"The latest available context shows "
                    f"approximately {value:.1f}% of the "
                    f"population in the 15–64 age group."
                ),
                "policy_relevance": (
                    "Employment, skills, productivity and "
                    "labour-force participation are important "
                    "for converting a large working-age "
                    "population into economic gains."
                ),
            })

    return signals


# ---------------------------------------------------------------------
# MAIN SERVICE
# ---------------------------------------------------------------------

def build_year_intelligence(
    year: int,
) -> dict[str, Any]:

    if not isinstance(year, int):
        raise ValueError(
            "Year must be an integer."
        )

    if year < HISTORICAL_START or year > FORECAST_END:
        raise ValueError(
            f"Year must be between "
            f"{HISTORICAL_START} and "
            f"{FORECAST_END}."
        )

    unified = _load_csv(
        UNIFIED_DATASET
    )

    master = _load_csv(
        MASTER_DATASET
    )

    year_insights = _load_csv(
        YEAR_INSIGHTS_DATASET
    )

    growth_analysis = _load_csv(
        GROWTH_ANALYSIS_DATASET
    )

    milestones = _load_csv(
        MILESTONES_DATASET
    )

    future_milestones = _load_csv(
        FUTURE_MILESTONES_DATASET
    )

    population = _get_population_information(
        year,
        unified,
    )

    if not population.get("available"):

        raise LookupError(
            f"No population forecast or historical "
            f"population value is available for {year}."
        )

    demographic_context = (
        _get_demographic_context(
            year,
            master,
        )
    )

    intelligence = _get_year_intelligence(
        year,
        year_insights,
    )

    milestone_records = _get_milestones(
        year,
        milestones,
        future_milestones,
    )

    growth_context = _get_growth_context(
        year,
        growth_analysis,
    )

    model_reliability = (
        _read_model_evaluation()
    )

    policy_signals = _build_policy_signals(
        year,
        population,
        demographic_context,
    )

    classification = _population_classification(
        year
    )

    # Calculate years from latest historical point
    # to make the forecast horizon understandable.
    if year >= FORECAST_START:
        years_from_historical = (
            year - HISTORICAL_END
        )
    else:
        years_from_historical = 0

    response = {
        "application": (
            "India Population Forecasting System"
        ),
        "report_type": (
            "National Demographic Intelligence"
        ),
        "scope": "India",
        "year": year,

        "population": population,

        "forecast_context": {
            "is_forecast_year":
                classification["is_forecast"],
            "forecast_start": FORECAST_START,
            "forecast_end": FORECAST_END,
            "years_from_latest_official":
                years_from_historical,
            "interpretation": (
                "Population values for forecast years "
                "come from the existing recursive ML "
                "forecasting pipeline."
                if classification["is_forecast"]
                else (
                    "This year is not an ML forecast year."
                )
            ),
        },

        "demographic_context": demographic_context,

        "intelligence": intelligence,

        "growth_analysis": growth_context,

        "milestones": {
            "count": len(milestone_records),
            "data": milestone_records,
        },

        "policy_signals": {
            "count": len(policy_signals),
            "data": policy_signals,
            "disclaimer": (
                "Policy signals are analytical "
                "interpretations of available demographic "
                "and forecast information. They are not "
                "official government policy recommendations."
            ),
        },

        "model_reliability": model_reliability,

        "data_provenance": {
            "historical": {
                "years": "1960-2024",
                "status": "Official historical data",
            },
            "estimated": {
                "year": 2025,
                "status": "Model estimated",
            },
            "forecast": {
                "years": "2026-2050",
                "status": "ML Forecast",
                "model": "Linear Regression",
            },
            "demographic_context": {
                "dataset": (
                    "india_master_dataset.csv"
                ),
                "status": (
                    "Latest available demographic "
                    "context; not independently forecast "
                    "by the population model."
                ),
            },
        },

        "limitations": [
            (
                "Population forecasts are model estimates "
                "and are not guaranteed outcomes."
            ),
            (
                "The existing population model predicts "
                "population change; it does not independently "
                "forecast every demographic indicator."
            ),
            (
                "For future years, demographic indicators "
                "are reported only when actually available "
                "for that year. Otherwise the API identifies "
                "the latest available demographic context."
            ),
            (
                "Policy signals are analytical interpretations "
                "and should not be treated as official policy."
            ),
        ],
    }

    return response