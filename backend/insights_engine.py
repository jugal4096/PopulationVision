import os
import json
import pandas as pd


# ============================================================
# NATIONAL DEMOGRAPHIC INTELLIGENCE ENGINE
# ============================================================
#
# PURPOSE
# -------
# This module sits ABOVE the existing ML pipeline.
#
# It does NOT:
#   - retrain the ML model
#   - modify official WDI datasets
#   - modify forecast values
#   - modify feature engineering
#   - replace train.py
#   - replace forecast.py
#   - replace analytics_engine.py
#
# It DOES:
#   - combine historical + estimated + forecast data
#   - classify data sources
#   - generate year-wise insights
#   - detect demographic milestones
#   - analyse growth dynamics
#   - generate research insights
#   - create machine-readable JSON/CSV outputs
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

FORECAST_ROOT_DIR = os.path.join(
    DATASET_DIR,
    "population_forecast"
)

ANALYTICS_DIR = os.path.join(
    FORECAST_ROOT_DIR,
    "analytics"
)

INTELLIGENCE_DIR = os.path.join(
    ANALYTICS_DIR,
    "intelligence"
)

os.makedirs(
    INTELLIGENCE_DIR,
    exist_ok=True
)


# ============================================================
# EXPECTED INPUT FILES
# ============================================================

FEATURE_DATASET = os.path.join(
    DATASET_DIR,
    "india_features_dataset.csv"
)

POPULATION_ANALYTICS = os.path.join(
    ANALYTICS_DIR,
    "population_analytics.csv"
)

DATA_STATUS = os.path.join(
    ANALYTICS_DIR,
    "data_status.csv"
)

RESEARCH_PERIODS = os.path.join(
    ANALYTICS_DIR,
    "research_period_analysis.csv"
)

FUTURE_MILESTONES = os.path.join(
    ANALYTICS_DIR,
    "future_milestones.csv"
)

RESEARCH_REPORT = os.path.join(
    ANALYTICS_DIR,
    "research_report.json"
)


# ============================================================
# FORECAST FILE CANDIDATES
# ============================================================
#
# Different versions of forecast.py may have produced the
# forecast file in different locations.
#
# We support all known layouts instead of assuming one path.
# ============================================================

FORECAST_FILENAME = (
    "population_forecast_2026_2050.csv"
)

FORECAST_CANDIDATES = [

    # Current known location
    os.path.join(
        FORECAST_ROOT_DIR,
        FORECAST_FILENAME
    ),

    # Possible nested location
    os.path.join(
        FORECAST_ROOT_DIR,
        "population_forecast",
        FORECAST_FILENAME
    ),

    # Another possible layout
    os.path.join(
        FORECAST_ROOT_DIR,
        "population",
        "forecast",
        FORECAST_FILENAME
    ),

    # Analytics directory fallback
    os.path.join(
        ANALYTICS_DIR,
        FORECAST_FILENAME
    )

]


# ============================================================
# OUTPUT FILES
# ============================================================

YEAR_INSIGHTS_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "year_insights.csv"
)

MILESTONES_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "detected_milestones.csv"
)

GROWTH_ANALYSIS_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "growth_analysis.csv"
)

RESEARCH_INSIGHTS_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "research_insights.json"
)

INTELLIGENCE_REPORT_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "intelligence_report.json"
)

UNIFIED_DATASET_FILE = os.path.join(
    INTELLIGENCE_DIR,
    "unified_population_dataset.csv"
)


# ============================================================
# DATA POLICY
# ============================================================

HISTORICAL_END_YEAR = 2024

ESTIMATED_YEAR = 2025

FORECAST_START_YEAR = 2026

FORECAST_END_YEAR = 2050


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_header(title):

    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_section(title):

    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


# ============================================================
# VALUE HELPERS
# ============================================================

def safe_float(value, default=None):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return default


def format_population(value):

    value = safe_float(value)

    if value is None:
        return "N/A"

    return f"{int(round(value)):,}"


def percentage_change(
    start_population,
    end_population
):

    start_population = safe_float(
        start_population
    )

    end_population = safe_float(
        end_population
    )

    if (
        start_population is None
        or end_population is None
    ):
        return None

    if start_population == 0:
        return None

    return (
        (
            end_population
            - start_population
        )
        / start_population
    ) * 100


def calculate_cagr(
    start_population,
    end_population,
    years
):

    start_population = safe_float(
        start_population
    )

    end_population = safe_float(
        end_population
    )

    if (
        start_population is None
        or end_population is None
        or start_population <= 0
        or end_population <= 0
        or years <= 0
    ):
        return None

    return (
        (
            end_population
            / start_population
        )
        ** (1 / years)
        - 1
    ) * 100


# ============================================================
# FILE HELPERS
# ============================================================

def find_existing_file(
    candidates
):

    for path in candidates:

        if os.path.isfile(path):

            return path

    return None


def find_forecast_file():

    # --------------------------------------------------------
    # First check known locations
    # --------------------------------------------------------

    path = find_existing_file(
        FORECAST_CANDIDATES
    )

    if path is not None:

        return path

    # --------------------------------------------------------
    # Search recursively inside forecast root
    # --------------------------------------------------------

    if os.path.isdir(
        FORECAST_ROOT_DIR
    ):

        for root, dirs, files in os.walk(
            FORECAST_ROOT_DIR
        ):

            if FORECAST_FILENAME in files:

                return os.path.join(
                    root,
                    FORECAST_FILENAME
                )

    return None


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_inputs():

    print_header(
        "INTELLIGENCE ENGINE - INPUT VALIDATION"
    )

    files_to_check = {

        "Feature dataset":
            FEATURE_DATASET,

        "Population analytics":
            POPULATION_ANALYTICS,

        "Data status":
            DATA_STATUS,

        "Research periods":
            RESEARCH_PERIODS,

        "Future milestones":
            FUTURE_MILESTONES,

        "Research report":
            RESEARCH_REPORT

    }

    for name, path in files_to_check.items():

        if os.path.isfile(path):

            print(f"✓ {name}")

        else:

            print(f"⚠ {name} not found")
            print(f"  {path}")

    # --------------------------------------------------------
    # Forecast
    # --------------------------------------------------------

    forecast_path = find_forecast_file()

    if forecast_path:

        print("✓ Forecast dataset")
        print(
            f"  {forecast_path}"
        )

    else:

        print(
            "⚠ Forecast dataset not found"
        )

        print(
            "  Forecast file will be optional."
        )

        print(
            "  Existing population analytics "
            "will be used when available."
        )

    return forecast_path


# ============================================================
# SAFE CSV LOADING
# ============================================================

def load_csv(
    path,
    name,
    required=False
):

    if not path:

        if required:

            raise FileNotFoundError(
                f"{name} is required."
            )

        return pd.DataFrame()

    if not os.path.isfile(path):

        if required:

            raise FileNotFoundError(
                f"{name} not found:\n{path}"
            )

        return pd.DataFrame()

    try:

        df = pd.read_csv(path)

        print(
            f"✓ {name} loaded: "
            f"{len(df)} rows"
        )

        return df

    except Exception as exc:

        if required:

            raise RuntimeError(
                f"Unable to load {name}:\n{exc}"
            )

        print(
            f"⚠ Unable to load {name}: {exc}"
        )

        return pd.DataFrame()


# ============================================================
# LOAD ALL AVAILABLE DATA
# ============================================================

def load_data(
    forecast_path
):

    print_header(
        "LOADING POPULATION INTELLIGENCE DATA"
    )

    analytics_df = load_csv(
        POPULATION_ANALYTICS,
        "Population analytics",
        required=True
    )

    forecast_df = load_csv(
        forecast_path,
        "Forecast dataset",
        required=False
    )

    status_df = load_csv(
        DATA_STATUS,
        "Data status",
        required=False
    )

    research_df = load_csv(
        RESEARCH_PERIODS,
        "Research period analysis",
        required=False
    )

    return (
        analytics_df,
        forecast_df,
        status_df,
        research_df
    )


# ============================================================
# NORMALIZE POPULATION DATAFRAME
# ============================================================

def normalize_population_dataframe(
    df,
    source_name
):

    if df is None or df.empty:

        return pd.DataFrame()

    df = df.copy()

    # --------------------------------------------------------
    # Year
    # --------------------------------------------------------

    if "Year" not in df.columns:

        raise ValueError(
            f"{source_name} does not contain "
            f"a Year column."
        )

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Year"]
    )

    df["Year"] = (
        df["Year"]
        .astype(int)
    )

    # --------------------------------------------------------
    # Population
    # --------------------------------------------------------

    if "Population" not in df.columns:

        possible_population_columns = [

            "Predicted_Population",
            "Actual_Population",
            "Estimated_Population"

        ]

        population_column = None

        for column in possible_population_columns:

            if column in df.columns:

                population_column = column
                break

        if population_column:

            df["Population"] = pd.to_numeric(
                df[population_column],
                errors="coerce"
            )

        else:

            raise ValueError(
                f"{source_name} does not contain "
                f"a usable population column."
            )

    else:

        df["Population"] = pd.to_numeric(
            df["Population"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Remove invalid populations
    # --------------------------------------------------------

    df = df[
        df["Population"].notna()
        & (df["Population"] > 0)
    ]

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    df["Source_File"] = source_name

    return df


# ============================================================
# CLASSIFY YEAR
# ============================================================

def classify_year(
    year
):

    if year <= HISTORICAL_END_YEAR:

        return "Historical"

    if year == ESTIMATED_YEAR:

        return "Estimated"

    return "Forecast"


def classify_status(
    source_type
):

    if source_type == "Historical":

        return "Official"

    if source_type == "Estimated":

        return "Model Estimated"

    if source_type == "Forecast":

        return "ML Forecast"

    return "Unknown"


def classify_source_description(
    source_type
):

    if source_type == "Historical":

        return "Official WDI dataset"

    if source_type == "Estimated":

        return (
            "Population forecasting model"
        )

    if source_type == "Forecast":

        return (
            "Population forecasting model"
        )

    return "Unknown"


# ============================================================
# BUILD UNIFIED DATASET
# ============================================================

def build_unified_dataset(
    analytics_df,
    forecast_df,
    status_df
):

    print_header(
        "BUILDING UNIFIED POPULATION DATASET"
    )

    # --------------------------------------------------------
    # Normalize analytics
    # --------------------------------------------------------

    analytics = normalize_population_dataframe(
        analytics_df,
        "Population analytics"
    )

    if analytics.empty:

        raise ValueError(
            "Population analytics contains "
            "no usable population data."
        )

    # --------------------------------------------------------
    # Normalize forecast
    # --------------------------------------------------------

    forecast = normalize_population_dataframe(
        forecast_df,
        "Forecast dataset"
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # Population analytics is considered the primary
    # consolidated source because analytics_engine.py
    # already produces the historical + estimated +
    # forecast series.
    #
    # Forecast data is used only to fill missing years.
    # --------------------------------------------------------

    primary = analytics.copy()

    if not forecast.empty:

        primary_years = set(
            primary["Year"].tolist()
        )

        forecast_only = forecast[
            ~forecast["Year"].isin(
                primary_years
            )
        ].copy()

        if not forecast_only.empty:

            primary = pd.concat(
                [
                    primary,
                    forecast_only
                ],
                ignore_index=True,
                sort=False
            )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    primary = primary.sort_values(
        "Year"
    )

    # --------------------------------------------------------
    # One row per year
    # --------------------------------------------------------

    primary = primary.drop_duplicates(
        subset=["Year"],
        keep="last"
    )

    primary = primary.sort_values(
        "Year"
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    primary["Source_Type"] = (
        primary["Year"]
        .apply(classify_year)
    )

    primary["Data_Status"] = (
        primary["Source_Type"]
        .apply(classify_status)
    )

    primary["Source"] = (
        primary["Source_Type"]
        .apply(
            classify_source_description
        )
    )

    # --------------------------------------------------------
    # Population change
    # --------------------------------------------------------

    primary["Population_Change"] = (
        primary["Population"].diff()
    )

    # --------------------------------------------------------
    # Growth rate
    # --------------------------------------------------------

    primary["Population_Growth_Rate"] = (
        primary["Population"]
        .pct_change()
        * 100
    )

    # --------------------------------------------------------
    # Population growth rate should not be calculated for
    # the very first available year.
    # --------------------------------------------------------

    primary.loc[
        primary.index == 0,
        "Population_Growth_Rate"
    ] = None

    # --------------------------------------------------------
    # Previous population
    # --------------------------------------------------------

    primary["Previous_Population"] = (
        primary["Population"].shift(1)
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if primary["Year"].duplicated().any():

        duplicates = primary.loc[
            primary["Year"].duplicated(),
            "Year"
        ].tolist()

        raise ValueError(
            "Duplicate years remain after "
            f"dataset consolidation: {duplicates}"
        )

    if (
        primary["Population"].isna().any()
        or (
            primary["Population"] <= 0
        ).any()
    ):

        raise ValueError(
            "Invalid population values remain "
            "after dataset consolidation."
        )

    # --------------------------------------------------------
    # Save unified dataset
    # --------------------------------------------------------

    primary.to_csv(
        UNIFIED_DATASET_FILE,
        index=False
    )

    print(
        f"✓ Unified dataset saved:\n"
        f"{UNIFIED_DATASET_FILE}"
    )

    print(
        f"✓ Coverage: "
        f"{primary['Year'].min()} - "
        f"{primary['Year'].max()}"
    )

    print(
        f"✓ Total rows: "
        f"{len(primary)}"
    )

    print(
        "\nData classification:"
    )

    classification_columns = [
        "Year",
        "Population",
        "Source_Type",
        "Data_Status",
        "Source"
    ]

    print(
        primary[
            classification_columns
        ].tail(5).to_string(
            index=False
        )
    )

    return primary


# ============================================================
# YEAR-WISE INSIGHTS
# ============================================================

def generate_year_insights(
    df
):

    print_header(
        "GENERATING YEAR-WISE INTELLIGENCE"
    )

    rows = []

    for _, row in df.iterrows():

        year = int(
            row["Year"]
        )

        population = safe_float(
            row["Population"]
        )

        previous_population = safe_float(
            row["Previous_Population"]
        )

        population_change = safe_float(
            row["Population_Change"]
        )

        growth_rate = safe_float(
            row["Population_Growth_Rate"]
        )

        source_type = row[
            "Source_Type"
        ]

        # ----------------------------------------------------
        # Growth category
        # ----------------------------------------------------

        if growth_rate is None:

            growth_category = (
                "Not Available"
            )

        elif growth_rate < 0:

            growth_category = (
                "Population Decline"
            )

        elif growth_rate < 0.10:

            growth_category = (
                "Extremely Slow Growth"
            )

        elif growth_rate < 0.25:

            growth_category = (
                "Very Slow Growth"
            )

        elif growth_rate < 0.50:

            growth_category = (
                "Slow Growth"
            )

        elif growth_rate < 1.00:

            growth_category = (
                "Moderate Growth"
            )

        elif growth_rate < 2.00:

            growth_category = (
                "High Growth"
            )

        else:

            growth_category = (
                "Very High Growth"
            )

        # ----------------------------------------------------
        # Population direction
        # ----------------------------------------------------

        if population_change is None:

            direction = "Not Available"

        elif population_change > 0:

            direction = "Increasing"

        elif population_change < 0:

            direction = "Decreasing"

        else:

            direction = "Stable"

        # ----------------------------------------------------
        # Main insight
        # ----------------------------------------------------

        if source_type == "Historical":

            insight = (
                f"In {year}, India's official "
                f"population was approximately "
                f"{format_population(population)}."
            )

        elif source_type == "Estimated":

            insight = (
                f"The forecasting model estimates "
                f"India's {year} population at "
                f"approximately "
                f"{format_population(population)}. "
                f"This value is an estimate, not "
                f"an official historical observation."
            )

        else:

            insight = (
                f"The ML forecasting model projects "
                f"India's population at approximately "
                f"{format_population(population)} "
                f"in {year}."
            )

        # ----------------------------------------------------
        # Add growth information
        # ----------------------------------------------------

        if growth_rate is not None:

            insight += (
                f" The annual population growth rate "
                f"is approximately "
                f"{growth_rate:.4f}%."
            )

        rows.append({

            "Year":
                year,

            "Population":
                population,

            "Previous_Population":
                previous_population,

            "Population_Change":
                population_change,

            "Population_Growth_Rate":
                growth_rate,

            "Source_Type":
                source_type,

            "Data_Status":
                row["Data_Status"],

            "Source":
                row["Source"],

            "Growth_Category":
                growth_category,

            "Population_Direction":
                direction,

            "Insight":
                insight

        })

    result = pd.DataFrame(
        rows
    )

    result.to_csv(
        YEAR_INSIGHTS_FILE,
        index=False
    )

    print(
        f"✓ Year insights generated: "
        f"{len(result)}"
    )

    print(
        f"✓ Saved:\n"
        f"{YEAR_INSIGHTS_FILE}"
    )

    return result


# ============================================================
# GROWTH DYNAMICS
# ============================================================

def generate_growth_analysis(
    df
):

    print_header(
        "ANALYSING POPULATION GROWTH DYNAMICS"
    )

    forecast = df[
        df["Year"] >= FORECAST_START_YEAR
    ].copy()

    if forecast.empty:

        print(
            "⚠ No 2026-2050 forecast data found."
        )

        empty = pd.DataFrame()

        empty.to_csv(
            GROWTH_ANALYSIS_FILE,
            index=False
        )

        return empty

    # --------------------------------------------------------
    # Growth rate change
    # --------------------------------------------------------

    forecast[
        "Growth_Rate_Change"
    ] = forecast[
        "Population_Growth_Rate"
    ].diff()

    # --------------------------------------------------------
    # Population change
    # --------------------------------------------------------

    forecast[
        "Population_Change"
    ] = forecast[
        "Population"
    ].diff()

    # --------------------------------------------------------
    # Growth direction
    # --------------------------------------------------------

    def growth_direction(
        value
    ):

        value = safe_float(
            value
        )

        if value is None:

            return "Not Available"

        if value > 0:

            return "Accelerating"

        if value < 0:

            return "Decelerating"

        return "Stable"

    forecast[
        "Growth_Direction"
    ] = forecast[
        "Growth_Rate_Change"
    ].apply(
        growth_direction
    )

    # --------------------------------------------------------
    # Growth category
    # --------------------------------------------------------

    def growth_category(
        value
    ):

        value = safe_float(
            value
        )

        if value is None:

            return "Not Available"

        if value < 0:

            return "Decline"

        if value < 0.10:

            return "Extremely Slow"

        if value < 0.25:

            return "Very Slow"

        if value < 0.50:

            return "Slow"

        if value < 1.00:

            return "Moderate"

        if value < 2.00:

            return "High"

        return "Very High"

    forecast[
        "Growth_Category"
    ] = forecast[
        "Population_Growth_Rate"
    ].apply(
        growth_category
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    forecast.to_csv(
        GROWTH_ANALYSIS_FILE,
        index=False
    )

    print(
        f"✓ Growth analysis saved:\n"
        f"{GROWTH_ANALYSIS_FILE}"
    )

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    first = forecast.iloc[0]

    last = forecast.iloc[-1]

    first_growth = safe_float(
        first[
            "Population_Growth_Rate"
        ]
    )

    last_growth = safe_float(
        last[
            "Population_Growth_Rate"
        ]
    )

    if (
        first_growth is not None
        and last_growth is not None
    ):

        change = (
            last_growth
            - first_growth
        )

        print(
            "\nForecast growth rate:"
        )

        print(
            f"  {int(first['Year'])}: "
            f"{first_growth:.4f}%"
        )

        print(
            f"  {int(last['Year'])}: "
            f"{last_growth:.4f}%"
        )

        print(
            f"  Change: "
            f"{change:.4f} percentage points"
        )

    return forecast


# ============================================================
# MILESTONE DETECTION
# ============================================================

def detect_milestones(
    df
):

    print_header(
        "DETECTING POPULATION MILESTONES"
    )

    milestones = []

    # ========================================================
    # POPULATION THRESHOLDS
    # ========================================================

    population_thresholds = [

        1_500_000_000,
        1_550_000_000,
        1_600_000_000,
        1_650_000_000,
        1_700_000_000,
        1_750_000_000,
        1_800_000_000

    ]

    for threshold in population_thresholds:

        crossed = df[
            df["Population"]
            >= threshold
        ]

        if crossed.empty:

            continue

        row = crossed.iloc[0]

        year = int(
            row["Year"]
        )

        milestones.append({

            "Milestone_Type":
                "Population Threshold",

            "Threshold":
                threshold,

            "Year":
                year,

            "Population":
                safe_float(
                    row["Population"]
                ),

            "Source_Type":
                row["Source_Type"],

            "Description":
                (
                    f"India's population "
                    f"reaches or exceeds "
                    f"{format_population(threshold)} "
                    f"in {year}."
                )

        })

    # ========================================================
    # FORECAST GROWTH THRESHOLDS
    # ========================================================

    forecast = df[
        df["Year"] >= FORECAST_START_YEAR
    ].copy()

    growth_thresholds = [

        1.00,
        0.75,
        0.50,
        0.25,
        0.10

    ]

    for threshold in growth_thresholds:

        crossed = forecast[
            forecast[
                "Population_Growth_Rate"
            ] <= threshold
        ]

        if crossed.empty:

            continue

        row = crossed.iloc[0]

        year = int(
            row["Year"]
        )

        growth_rate = safe_float(
            row[
                "Population_Growth_Rate"
            ]
        )

        milestones.append({

            "Milestone_Type":
                "Growth Rate Threshold",

            "Threshold":
                threshold,

            "Year":
                year,

            "Population":
                safe_float(
                    row["Population"]
                ),

            "Source_Type":
                "Forecast",

            "Description":
                (
                    f"Projected annual "
                    f"population growth falls "
                    f"to {threshold:.2f}% or below "
                    f"in {year}. Actual projected "
                    f"rate: {growth_rate:.4f}%."
                )

        })

    # ========================================================
    # HIGHEST FORECAST GROWTH
    # ========================================================

    if not forecast.empty:

        valid_growth = forecast[
            forecast[
                "Population_Growth_Rate"
            ].notna()
        ]

        if not valid_growth.empty:

            max_index = (
                valid_growth[
                    "Population_Growth_Rate"
                ].idxmax()
            )

            row = valid_growth.loc[
                max_index
            ]

            growth_rate = safe_float(
                row[
                    "Population_Growth_Rate"
                ]
            )

            milestones.append({

                "Milestone_Type":
                    "Highest Forecast Growth",

                "Threshold":
                    growth_rate,

                "Year":
                    int(row["Year"]),

                "Population":
                    safe_float(
                        row["Population"]
                    ),

                "Source_Type":
                    "Forecast",

                "Description":
                    (
                        f"The highest projected "
                        f"annual population growth "
                        f"occurs in {int(row['Year'])} "
                        f"at approximately "
                        f"{growth_rate:.4f}%."
                    )

            })

            # =================================================
            # LOWEST FORECAST GROWTH
            # =================================================

            min_index = (
                valid_growth[
                    "Population_Growth_Rate"
                ].idxmin()
            )

            row = valid_growth.loc[
                min_index
            ]

            growth_rate = safe_float(
                row[
                    "Population_Growth_Rate"
                ]
            )

            milestones.append({

                "Milestone_Type":
                    "Lowest Forecast Growth",

                "Threshold":
                    growth_rate,

                "Year":
                    int(row["Year"]),

                "Population":
                    safe_float(
                        row["Population"]
                    ),

                "Source_Type":
                    "Forecast",

                "Description":
                    (
                        f"The lowest projected "
                        f"annual population growth "
                        f"occurs in {int(row['Year'])} "
                        f"at approximately "
                        f"{growth_rate:.4f}%."
                    )

            })

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    milestone_df = pd.DataFrame(
        milestones
    )

    if not milestone_df.empty:

        milestone_df = (
            milestone_df
            .sort_values(
                [
                    "Year",
                    "Milestone_Type"
                ]
            )
            .reset_index(
                drop=True
            )
        )

    milestone_df.to_csv(
        MILESTONES_FILE,
        index=False
    )

    print(
        f"✓ Milestones detected: "
        f"{len(milestone_df)}"
    )

    print(
        f"✓ Saved:\n"
        f"{MILESTONES_FILE}"
    )

    return milestone_df


# ============================================================
# RESEARCH INSIGHTS
# ============================================================

def generate_research_insights(
    df
):

    print_header(
        "GENERATING RESEARCH INSIGHTS"
    )

    insights = []

    # ========================================================
    # HISTORICAL TREND
    # ========================================================

    historical = df[
        df["Year"]
        <= HISTORICAL_END_YEAR
    ]

    if not historical.empty:

        first = historical.iloc[0]

        last = historical.iloc[-1]

        change = percentage_change(
            first["Population"],
            last["Population"]
        )

        if change is not None:

            insights.append({

                "type":
                    "historical_trend",

                "title":
                    "Historical Population Trend",

                "insight":
                    (
                        f"Official population "
                        f"increased from "
                        f"{format_population(first['Population'])} "
                        f"in {int(first['Year'])} "
                        f"to "
                        f"{format_population(last['Population'])} "
                        f"in {int(last['Year'])}, "
                        f"representing an increase "
                        f"of {change:.2f}%."
                    )

            })

    # ========================================================
    # 2025 ESTIMATE
    # ========================================================

    estimated = df[
        df["Year"]
        == ESTIMATED_YEAR
    ]

    if not estimated.empty:

        row = estimated.iloc[0]

        insights.append({

            "type":
                "estimated_2025",

            "title":
                "2025 Model Estimate",

            "insight":
                (
                    f"The forecasting model "
                    f"estimates India's 2025 "
                    f"population at approximately "
                    f"{format_population(row['Population'])}. "
                    f"This value is a model estimate "
                    f"and is not treated as an official "
                    f"historical observation."
                )

        })

    # ========================================================
    # FORECAST TREND
    # ========================================================

    forecast = df[
        df["Year"]
        >= FORECAST_START_YEAR
    ]

    if not forecast.empty:

        first = forecast.iloc[0]

        last = forecast.iloc[-1]

        change = percentage_change(
            first["Population"],
            last["Population"]
        )

        if change is not None:

            insights.append({

                "type":
                    "forecast_trend",

                "title":
                    "Forecast Population Trend",

                "insight":
                    (
                        f"The ML model projects "
                        f"India's population to "
                        f"change by approximately "
                        f"{change:.2f}% between "
                        f"{int(first['Year'])} "
                        f"and "
                        f"{int(last['Year'])}."
                    )

            })

        # ====================================================
        # GROWTH DYNAMICS
        # ====================================================

        first_growth = safe_float(
            first[
                "Population_Growth_Rate"
            ]
        )

        last_growth = safe_float(
            last[
                "Population_Growth_Rate"
            ]
        )

        if (
            first_growth is not None
            and last_growth is not None
        ):

            insights.append({

                "type":
                    "growth_dynamics",

                "title":
                    "Population Growth Dynamics",

                "insight":
                    (
                        f"Projected annual "
                        f"population growth "
                        f"declines from "
                        f"approximately "
                        f"{first_growth:.3f}% "
                        f"in "
                        f"{int(first['Year'])} "
                        f"to "
                        f"{last_growth:.3f}% "
                        f"by "
                        f"{int(last['Year'])}."
                    )

            })

            reduction = (
                first_growth
                - last_growth
            )

            insights.append({

                "type":
                    "growth_rate_reduction",

                "title":
                    "Growth Rate Reduction",

                "insight":
                    (
                        f"The projected annual "
                        f"growth rate declines by "
                        f"approximately "
                        f"{reduction:.3f} percentage "
                        f"points between "
                        f"{int(first['Year'])} "
                        f"and "
                        f"{int(last['Year'])}."
                    )

            })

        # ====================================================
        # 2050
        # ====================================================

        final_population = safe_float(
            last["Population"]
        )

        insights.append({

            "type":
                "2050_projection",

            "title":
                "2050 Population Projection",

            "insight":
                (
                    f"The current ML forecasting "
                    f"pipeline projects India's "
                    f"population at approximately "
                    f"{format_population(final_population)} "
                    f"by "
                    f"{int(last['Year'])}."
                )

        })

    # ========================================================
    # SAVE JSON
    # ========================================================

    with open(
        RESEARCH_INSIGHTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            insights,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"✓ Research insights saved:\n"
        f"{RESEARCH_INSIGHTS_FILE}"
    )

    return insights


# ============================================================
# BUILD FINAL INTELLIGENCE REPORT
# ============================================================

def build_intelligence_report(
    df,
    year_insights,
    growth_analysis,
    milestones,
    research_insights,
    forecast_path
):

    print_header(
        "BUILDING FINAL INTELLIGENCE REPORT"
    )

    historical_count = len(
        df[
            df["Year"]
            <= HISTORICAL_END_YEAR
        ]
    )

    estimated_count = len(
        df[
            df["Year"]
            == ESTIMATED_YEAR
        ]
    )

    forecast_count = len(
        df[
            df["Year"]
            >= FORECAST_START_YEAR
        ]
    )

    report = {

        "application":
            "AI Population Forecasting",

        "module":
            "National Demographic Intelligence Engine",

        "version":
            "1.0",

        "coverage": {

            "start_year":
                int(df["Year"].min()),

            "end_year":
                int(df["Year"].max()),

            "historical_end_year":
                HISTORICAL_END_YEAR,

            "estimated_year":
                ESTIMATED_YEAR,

            "forecast_start_year":
                FORECAST_START_YEAR,

            "forecast_end_year":
                FORECAST_END_YEAR

        },

        "data_policy": {

            "historical":
                "Official WDI observations",

            "estimated_2025":
                "Model-generated estimate",

            "forecast_2026_2050":
                "ML-generated forecast",

            "official_data_modified":
                False,

            "model_retrained":
                False,

            "forecast_values_modified":
                False

        },

        "source_files": {

            "feature_dataset":
                FEATURE_DATASET,

            "population_analytics":
                POPULATION_ANALYTICS,

            "data_status":
                DATA_STATUS,

            "forecast_dataset":
                forecast_path

        },

        "statistics": {

            "total_years":
                int(len(df)),

            "historical_years":
                int(historical_count),

            "estimated_years":
                int(estimated_count),

            "forecast_years":
                int(forecast_count),

            "year_insights":
                int(len(year_insights)),

            "milestones":
                int(len(milestones)),

            "research_insights":
                int(len(research_insights))

        },

        "population_range": {

            "first_year":
                int(df.iloc[0]["Year"]),

            "first_population":
                safe_float(
                    df.iloc[0]["Population"]
                ),

            "last_year":
                int(df.iloc[-1]["Year"]),

            "last_population":
                safe_float(
                    df.iloc[-1]["Population"]
                )

        },

        "research_insights":
            research_insights,

        "milestones":
            milestones.to_dict(
                orient="records"
            )
            if not milestones.empty
            else [],

        "generated_files": {

            "unified_dataset":
                UNIFIED_DATASET_FILE,

            "year_insights":
                YEAR_INSIGHTS_FILE,

            "growth_analysis":
                GROWTH_ANALYSIS_FILE,

            "milestones":
                MILESTONES_FILE,

            "research_insights":
                RESEARCH_INSIGHTS_FILE,

            "intelligence_report":
                INTELLIGENCE_REPORT_FILE

        }

    }

    with open(
        INTELLIGENCE_REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    print(
        f"✓ Intelligence report saved:\n"
        f"{INTELLIGENCE_REPORT_FILE}"
    )

    return report


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_final_dataset(
    df
):

    print_header(
        "FINAL INTELLIGENCE DATA VALIDATION"
    )

    # --------------------------------------------------------
    # Year checks
    # --------------------------------------------------------

    if df["Year"].duplicated().any():

        raise ValueError(
            "Final dataset contains duplicate years."
        )

    # --------------------------------------------------------
    # Population checks
    # --------------------------------------------------------

    if df["Population"].isna().any():

        bad_years = df.loc[
            df["Population"].isna(),
            "Year"
        ].tolist()

        raise ValueError(
            "Missing population values for: "
            f"{bad_years}"
        )

    if (
        df["Population"] <= 0
    ).any():

        raise ValueError(
            "Invalid population values detected."
        )

    # --------------------------------------------------------
    # Expected boundaries
    # --------------------------------------------------------

    minimum_year = int(
        df["Year"].min()
    )

    maximum_year = int(
        df["Year"].max()
    )

    print(
        f"✓ Coverage: "
        f"{minimum_year} - "
        f"{maximum_year}"
    )

    print(
        f"✓ Total rows: "
        f"{len(df)}"
    )

    print(
        "✓ No duplicate years"
    )

    print(
        "✓ No missing population values"
    )

    print(
        "✓ No invalid population values"
    )

    # --------------------------------------------------------
    # 2024 check
    # --------------------------------------------------------

    if not (
        df["Year"]
        .eq(2024)
        .any()
    ):

        print(
            "⚠ 2024 official observation "
            "not available."
        )

    else:

        print(
            "✓ 2024 population available"
        )

    # --------------------------------------------------------
    # 2025 check
    # --------------------------------------------------------

    if not (
        df["Year"]
        .eq(2025)
        .any()
    ):

        print(
            "⚠ 2025 estimated population "
            "not available."
        )

    else:

        print(
            "✓ 2025 estimated population available"
        )

    # --------------------------------------------------------
    # 2050 check
    # --------------------------------------------------------

    if not (
        df["Year"]
        .eq(2050)
        .any()
    ):

        print(
            "⚠ 2050 forecast not available."
        )

    else:

        print(
            "✓ 2050 forecast available"
        )

    # --------------------------------------------------------
    # Classification counts
    # --------------------------------------------------------

    print(
        "\nData classification:"
    )

    print(
        df[
            "Source_Type"
        ]
        .value_counts()
        .to_string()
    )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print_header(
        "NATIONAL DEMOGRAPHIC INTELLIGENCE ENGINE"
    )

    print(
        "This module does NOT retrain the ML model."
    )

    print(
        "This module does NOT modify official datasets."
    )

    print(
        "This module does NOT modify forecast values."
    )

    print(
        "This module consumes the existing "
        "forecasting and analytics pipeline."
    )

    # ========================================================
    # STEP 1 - INPUT VALIDATION
    # ========================================================

    forecast_path = validate_inputs()

    # ========================================================
    # STEP 2 - LOAD DATA
    # ========================================================

    (
        analytics_df,
        forecast_df,
        status_df,
        research_df
    ) = load_data(
        forecast_path
    )

    # ========================================================
    # STEP 3 - BUILD UNIFIED DATASET
    # ========================================================

    unified_df = build_unified_dataset(
        analytics_df,
        forecast_df,
        status_df
    )

    # ========================================================
    # STEP 4 - VALIDATE
    # ========================================================

    validate_final_dataset(
        unified_df
    )

    # ========================================================
    # STEP 5 - YEAR INSIGHTS
    # ========================================================

    year_insights = generate_year_insights(
        unified_df
    )

    # ========================================================
    # STEP 6 - GROWTH ANALYSIS
    # ========================================================

    growth_analysis = (
        generate_growth_analysis(
            unified_df
        )
    )

    # ========================================================
    # STEP 7 - MILESTONES
    # ========================================================

    milestones = detect_milestones(
        unified_df
    )

    # ========================================================
    # STEP 8 - RESEARCH INSIGHTS
    # ========================================================

    research_insights = (
        generate_research_insights(
            unified_df
        )
    )

    # ========================================================
    # STEP 9 - FINAL REPORT
    # ========================================================

    build_intelligence_report(
        unified_df,
        year_insights,
        growth_analysis,
        milestones,
        research_insights,
        forecast_path
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print_header(
        "INTELLIGENCE ENGINE COMPLETED SUCCESSFULLY"
    )

    print(
        f"Coverage:"
        f" {unified_df['Year'].min()}"
        f" - "
        f"{unified_df['Year'].max()}"
    )

    print(
        f"Total years:"
        f" {len(unified_df)}"
    )

    print(
        f"Year insights:"
        f" {len(year_insights)}"
    )

    print(
        f"Milestones:"
        f" {len(milestones)}"
    )

    print(
        f"Research insights:"
        f" {len(research_insights)}"
    )

    print(
        "\nGenerated files:"
    )

    print(
        f"✓ {UNIFIED_DATASET_FILE}"
    )

    print(
        f"✓ {YEAR_INSIGHTS_FILE}"
    )

    print(
        f"✓ {GROWTH_ANALYSIS_FILE}"
    )

    print(
        f"✓ {MILESTONES_FILE}"
    )

    print(
        f"✓ {RESEARCH_INSIGHTS_FILE}"
    )

    print(
        f"✓ {INTELLIGENCE_REPORT_FILE}"
    )

    print(
        "\nSystem policy:"
    )

    print(
        "✓ Official WDI data was NOT modified."
    )

    print(
        "✓ ML model was NOT retrained."
    )

    print(
        "✓ Existing forecast values were NOT modified."
    )

    print(
        "✓ Historical, estimated and forecast "
        "data remain separately classified."
    )

    print(
        "\nNext module: API layer."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n\nProcess interrupted by user."
        )

    except Exception as exc:

        print(
            "\n\n" + "=" * 78
        )

        print(
            "INTELLIGENCE ENGINE FAILED"
        )

        print(
            "=" * 78
        )

        print(
            f"\nError:\n{exc}"
        )

        print(
            "\nNo ML model or official dataset "
            "was modified."
        )

        raise