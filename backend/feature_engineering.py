import os
import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_DIR = os.path.join(BASE_DIR, "dataset")

INPUT_FILE = os.path.join(
    DATASET_DIR,
    "india_clean_dataset.csv"
)

OUTPUT_FILE = os.path.join(
    DATASET_DIR,
    "india_features_dataset.csv"
)


# ============================================================
# REQUIRED COLUMN
# ============================================================

REQUIRED_COLUMNS = [
    "Year",
    "Population"
]


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset():

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"\nClean dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("=" * 80)
    print("FEATURE ENGINEERING")
    print("=" * 80)

    print(f"\nInput dataset : {INPUT_FILE}")
    print(f"Rows          : {len(df)}")
    print(f"Columns       : {len(df.columns)}")

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}"
        )

    return df


# ============================================================
# CREATE LEAKAGE-SAFE FEATURES
# ============================================================

def create_features(df):

    df = df.copy()

    df = df.sort_values("Year").reset_index(drop=True)

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Every population-derived feature is shifted BEFORE
    # being used by the model.
    #
    # Therefore year t never receives Population(t).
    # --------------------------------------------------------

    # Previous year's population
    df["Prev_Population"] = (
        df["Population"].shift(1)
    )

    # Population from two years ago
    df["Population_Lag_2"] = (
        df["Population"].shift(2)
    )

    # Population from three years ago
    df["Population_Lag_3"] = (
        df["Population"].shift(3)
    )

    # Previous 3-year population average
    df["Population_MA3"] = (
        df["Population"]
        .shift(1)
        .rolling(window=3)
        .mean()
    )

    # Previous year's population change
    df["Population_Change"] = (
        df["Population"].shift(1)
        -
        df["Population"].shift(2)
    )

    # Previous year's population growth rate
    df["Population_Growth_Rate"] = (
        df["Population_Change"]
        /
        df["Population"].shift(2)
    ) * 100

    # --------------------------------------------------------
    # Historical changes in demographic/economic indicators
    # --------------------------------------------------------

    optional_change_columns = [
        "Birth_Rate",
        "Death_Rate",
        "Fertility_Rate",
        "Life_Expectancy",
        "GDP_Growth",
        "Net_Migration",
        "Literacy_Rate",
        "Urban_Population",
        "Infant_Mortality",
        "Population_Density"
    ]

    for column in optional_change_columns:

        if column in df.columns:

            df[f"{column}_Lag_1"] = (
                df[column].shift(1)
            )

            df[f"{column}_Change"] = (
                df[column].shift(1)
                -
                df[column].shift(2)
            )

    # --------------------------------------------------------
    # Demographic ratios
    # --------------------------------------------------------

    if {
        "Birth_Rate",
        "Death_Rate"
    }.issubset(df.columns):

        death_rate = df["Death_Rate"].shift(1)

        df["Birth_Death_Ratio"] = (
            df["Birth_Rate"].shift(1)
            /
            death_rate.replace(0, np.nan)
        )

    # --------------------------------------------------------
    # Remove infinite values
    # --------------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    # --------------------------------------------------------
    # Remove only rows where historical population
    # information genuinely does not exist.
    #
    # Three years of historical population are required.
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "Prev_Population",
            "Population_Lag_2",
            "Population_Lag_3",
            "Population_MA3",
            "Population_Change"
        ]
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df


# ============================================================
# VALIDATE FEATURES
# ============================================================

def validate_features(df):

    print("\n" + "=" * 80)
    print("FEATURE VALIDATION")
    print("=" * 80)

    print(f"\nRows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nFeature columns:")

    for column in df.columns:
        print(f"  ✓ {column}")

    print("\nMissing values:")

    missing = df.isnull().sum()

    missing = missing[
        missing > 0
    ]

    if missing.empty:
        print("  None")
    else:
        print(missing)

    print("\nYear range:")
    print(
        f"  {int(df['Year'].min())}"
        f" - "
        f"{int(df['Year'].max())}"
    )


# ============================================================
# SAVE
# ============================================================

def save_dataset(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 80)
    print("FEATURE DATASET SAVED")
    print("=" * 80)

    print(OUTPUT_FILE)


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_dataset()

    df = create_features(df)

    validate_features(df)

    save_dataset(df)

    print("\nFeature engineering completed successfully.")


if __name__ == "__main__":
    main()