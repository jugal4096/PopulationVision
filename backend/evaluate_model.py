import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_DIR = os.path.join(BASE_DIR, "dataset")

FORECAST_DIR = os.path.join(
    DATASET_DIR,
    "population_forecast"
)

BACKTEST_2010_2020 = os.path.join(
    FORECAST_DIR,
    "backtest_2010_2020.csv"
)

BACKTEST_2015_2024 = os.path.join(
    FORECAST_DIR,
    "backtest_2015_2024.csv"
)

FORECAST_FILE = os.path.join(
    FORECAST_DIR,
    "population_forecast_2026_2034.csv"
)

EVALUATION_DIR = os.path.join(
    FORECAST_DIR,
    "evaluation"
)

os.makedirs(EVALUATION_DIR, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def load_csv(path, description):

    if not os.path.exists(path):
        print(f"\n⚠️ File not found:")
        print(path)
        return None

    df = pd.read_csv(path)

    print(f"\n✓ Loaded {description}")
    print(f"  Rows    : {len(df)}")
    print(f"  Columns : {len(df.columns)}")

    return df


def calculate_metrics(actual, predicted):

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    error = predicted - actual

    absolute_error = np.abs(error)

    mae = np.mean(absolute_error)

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    percentage_error = (
        absolute_error / np.abs(actual)
    ) * 100

    mean_percentage_error = np.mean(
        percentage_error
    )

    max_error = np.max(
        absolute_error
    )

    max_error_index = np.argmax(
        absolute_error
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "Mean_Percentage_Error": mean_percentage_error,
        "Maximum_Absolute_Error": max_error,
        "Maximum_Error_Index": max_error_index
    }


# ============================================================
# BACKTEST EVALUATION
# ============================================================

def evaluate_backtest(df, period):

    required_columns = [
        "Year",
        "Actual_Population",
        "Predicted_Population"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        print(
            f"\n❌ {period} is missing columns:"
        )
        print(missing)
        print("\nAvailable columns:")
        print(df.columns.tolist())
        return None

    metrics = calculate_metrics(
        df["Actual_Population"],
        df["Predicted_Population"]
    )

    df = df.copy()

    df["Error"] = (
        df["Predicted_Population"]
        - df["Actual_Population"]
    )

    df["Absolute_Error"] = np.abs(
        df["Error"]
    )

    df["Percentage_Error"] = (
        df["Absolute_Error"]
        / df["Actual_Population"]
    ) * 100

    print("\n" + "=" * 70)
    print(f"BACKTEST EVALUATION: {period}")
    print("=" * 70)

    print(
        f"MAE                    : "
        f"{metrics['MAE']:,.2f}"
    )

    print(
        f"RMSE                   : "
        f"{metrics['RMSE']:,.2f}"
    )

    print(
        f"Mean Percentage Error  : "
        f"{metrics['Mean_Percentage_Error']:.4f}%"
    )

    print(
        f"Maximum Absolute Error : "
        f"{metrics['Maximum_Absolute_Error']:,.2f}"
    )

    worst_row = df.loc[
        df["Absolute_Error"].idxmax()
    ]

    print(
        f"Worst Prediction Year  : "
        f"{int(worst_row['Year'])}"
    )

    print(
        f"Worst Prediction Error : "
        f"{worst_row['Absolute_Error']:,.2f}"
    )

    print("\nYear-by-Year Errors:")
    print(
        df[
            [
                "Year",
                "Actual_Population",
                "Predicted_Population",
                "Absolute_Error",
                "Percentage_Error"
            ]
        ].to_string(index=False)
    )

    return df, metrics


# ============================================================
# PLOT BACKTEST
# ============================================================

def plot_backtest(df, period, filename):

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["Year"],
        df["Actual_Population"],
        marker="o",
        label="Actual Population"
    )

    plt.plot(
        df["Year"],
        df["Predicted_Population"],
        marker="o",
        label="Predicted Population"
    )

    plt.title(
        f"Actual vs Predicted Population ({period})"
    )

    plt.xlabel("Year")
    plt.ylabel("Population")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_DIR,
        filename
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print(f"\n✓ Plot saved:")
    print(path)


# ============================================================
# ERROR PLOT
# ============================================================

def plot_errors(df, period, filename):

    plt.figure(figsize=(12, 6))

    plt.bar(
        df["Year"],
        df["Percentage_Error"]
    )

    plt.axhline(
        0,
        linewidth=1
    )

    plt.title(
        f"Prediction Percentage Error ({period})"
    )

    plt.xlabel("Year")
    plt.ylabel("Absolute Percentage Error (%)")

    plt.grid(
        axis="y",
        alpha=0.3
    )

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_DIR,
        filename
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print(f"\n✓ Error plot saved:")
    print(path)


# ============================================================
# FORECAST EVALUATION
# ============================================================

def evaluate_forecast(df):

    required_columns = [
        "Year",
        "Previous_Population",
        "Predicted_Population",
        "Predicted_Growth_Rate"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:

        print(
            "\n⚠️ Forecast file does not contain "
            "all expected columns."
        )

        print("Missing:")
        print(missing)

        print("\nAvailable columns:")
        print(df.columns.tolist())

        return None

    print("\n" + "=" * 70)
    print("2026-2034 FORECAST")
    print("=" * 70)

    print(
        df[
            [
                "Year",
                "Previous_Population",
                "Predicted_Population",
                "Predicted_Growth_Rate"
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------------
    # Forecast growth
    # --------------------------------------------------------

    first_population = (
        df.iloc[0]["Predicted_Population"]
    )

    last_population = (
        df.iloc[-1]["Predicted_Population"]
    )

    total_growth = (
        (last_population / first_population) - 1
    ) * 100

    print("\nForecast Summary")

    print(
        f"2026 Population : "
        f"{first_population:,.0f}"
    )

    print(
        f"2034 Population : "
        f"{last_population:,.0f}"
    )

    print(
        f"2026-2034 Growth: "
        f"{total_growth:.2f}%"
    )

    return df


# ============================================================
# FORECAST PLOT
# ============================================================

def plot_forecast(df):

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["Year"],
        df["Predicted_Population"],
        marker="o",
        label="Forecast"
    )

    plt.title(
        "India Population Forecast: 2026-2034"
    )

    plt.xlabel("Year")
    plt.ylabel("Population")

    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_DIR,
        "population_forecast_2026_2034.png"
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print("\n✓ Forecast plot saved:")
    print(path)


# ============================================================
# FORECAST GROWTH PLOT
# ============================================================

def plot_growth(df):

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["Year"],
        df["Predicted_Growth_Rate"],
        marker="o"
    )

    plt.axhline(
        0,
        linewidth=1
    )

    plt.title(
        "Predicted Population Growth Rate: 2026-2034"
    )

    plt.xlabel("Year")
    plt.ylabel("Growth Rate (%)")

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_DIR,
        "population_growth_forecast_2026_2034.png"
    )

    plt.savefig(
        path,
        dpi=150
    )

    plt.close()

    print("\n✓ Growth plot saved:")
    print(path)


# ============================================================
# SAVE EVALUATION SUMMARY
# ============================================================

def save_summary(results):

    summary = pd.DataFrame(results)

    path = os.path.join(
        EVALUATION_DIR,
        "model_evaluation_summary.csv"
    )

    summary.to_csv(
        path,
        index=False
    )

    print("\n✓ Evaluation summary saved:")
    print(path)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("INDIA POPULATION FORECASTING")
    print("MODEL EVALUATION")
    print("=" * 70)

    results = []

    # --------------------------------------------------------
    # 2010-2020
    # --------------------------------------------------------

    df_2010 = load_csv(
        BACKTEST_2010_2020,
        "2010-2020 backtest"
    )

    if df_2010 is not None:

        evaluated_2010 = evaluate_backtest(
            df_2010,
            "2010-2020"
        )

        if evaluated_2010 is not None:

            evaluated_df, metrics = evaluated_2010

            results.append({
                "Period": "2010-2020",
                "MAE": metrics["MAE"],
                "RMSE": metrics["RMSE"],
                "Mean_Percentage_Error":
                    metrics["Mean_Percentage_Error"],
                "Maximum_Absolute_Error":
                    metrics["Maximum_Absolute_Error"]
            })

            plot_backtest(
                evaluated_df,
                "2010-2020",
                "actual_vs_predicted_2010_2020.png"
            )

            plot_errors(
                evaluated_df,
                "2010-2020",
                "prediction_errors_2010_2020.png"
            )

    # --------------------------------------------------------
    # 2015-2024
    # --------------------------------------------------------

    df_2015 = load_csv(
        BACKTEST_2015_2024,
        "2015-2024 backtest"
    )

    if df_2015 is not None:

        evaluated_2015 = evaluate_backtest(
            df_2015,
            "2015-2024"
        )

        if evaluated_2015 is not None:

            evaluated_df, metrics = evaluated_2015

            results.append({
                "Period": "2015-2024",
                "MAE": metrics["MAE"],
                "RMSE": metrics["RMSE"],
                "Mean_Percentage_Error":
                    metrics["Mean_Percentage_Error"],
                "Maximum_Absolute_Error":
                    metrics["Maximum_Absolute_Error"]
            })

            plot_backtest(
                evaluated_df,
                "2015-2024",
                "actual_vs_predicted_2015_2024.png"
            )

            plot_errors(
                evaluated_df,
                "2015-2024",
                "prediction_errors_2015_2024.png"
            )

    # --------------------------------------------------------
    # Future forecast
    # --------------------------------------------------------

    forecast_df = load_csv(
        FORECAST_FILE,
        "2026-2034 population forecast"
    )

    if forecast_df is not None:

        forecast_df = evaluate_forecast(
            forecast_df
        )

        if forecast_df is not None:

            plot_forecast(
                forecast_df
            )

            plot_growth(
                forecast_df
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if results:

        print("\n" + "=" * 70)
        print("BACKTEST SUMMARY")
        print("=" * 70)

        summary_df = pd.DataFrame(results)

        print(
            summary_df.to_string(
                index=False
            )
        )

        save_summary(results)

    print("\n" + "=" * 70)
    print("MODEL EVALUATION COMPLETED")
    print("=" * 70)

    print("\nEvaluation files:")
    print(EVALUATION_DIR)


if __name__ == "__main__":
    main()