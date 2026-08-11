import os
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------
# Project Paths
# --------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE_DIR, "dataset", "india_master_dataset.csv")
GRAPH_DIR = os.path.join(BASE_DIR, "graphs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(GRAPH_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# --------------------------------
# Load Dataset
# --------------------------------
df = pd.read_csv(DATASET)

print("=" * 60)
print("INDIA MASTER DATASET")
print("=" * 60)

print("\nFirst 5 Rows")
print(df.head())

print("\nDataset Shape")
print(df.shape)

print("\nColumn Names")
print(df.columns.tolist())

print("\nData Types")
print(df.dtypes)

print("\nMissing Values")
print(df.isnull().sum())

print("\nDuplicate Rows")
print(df.duplicated().sum())

print("\nSummary Statistics")
print(df.describe())

# --------------------------------
# Correlation
# --------------------------------
corr = df.corr(numeric_only=True)

print("\nCorrelation Matrix")
print(corr)

# --------------------------------
# Population Trend
# --------------------------------
plt.figure(figsize=(10,6))
plt.plot(df["Year"], df["Population"])
plt.title("India Population Over Time")
plt.xlabel("Year")
plt.ylabel("Population")
plt.grid(True)

plt.savefig(os.path.join(GRAPH_DIR, "population_trend.png"))
plt.close()

# --------------------------------
# Birth Rate
# --------------------------------
plt.figure(figsize=(10,6))
plt.plot(df["Year"], df["Birth_Rate"])
plt.title("Birth Rate")
plt.xlabel("Year")
plt.ylabel("Birth Rate")
plt.grid(True)

plt.savefig(os.path.join(GRAPH_DIR, "birth_rate.png"))
plt.close()

# --------------------------------
# Death Rate
# --------------------------------
plt.figure(figsize=(10,6))
plt.plot(df["Year"], df["Death_Rate"])
plt.title("Death Rate")
plt.xlabel("Year")
plt.ylabel("Death Rate")
plt.grid(True)

plt.savefig(os.path.join(GRAPH_DIR, "death_rate.png"))
plt.close()

# --------------------------------
# Report
# --------------------------------
report_path = os.path.join(REPORT_DIR, "eda_report.txt")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("INDIA POPULATION DATASET EDA REPORT\n")
    f.write("=" * 50 + "\n\n")

    f.write(f"Shape: {df.shape}\n\n")

    f.write("Missing Values\n")
    f.write(str(df.isnull().sum()))
    f.write("\n\n")

    f.write("Duplicate Rows\n")
    f.write(str(df.duplicated().sum()))
    f.write("\n\n")

    f.write("Summary Statistics\n")
    f.write(str(df.describe()))

print("\nEDA Completed Successfully")
print(f"Graphs saved in: {GRAPH_DIR}")
print(f"Report saved in: {report_path}")