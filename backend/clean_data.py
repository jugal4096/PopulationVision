import os
import pandas as pd

# --------------------------------
# Project Paths
# --------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MASTER_DATASET = os.path.join(BASE_DIR, "dataset", "india_master_dataset.csv")
OUTPUT_DATASET = os.path.join(BASE_DIR, "dataset", "india_clean_dataset.csv")

# --------------------------------
# Load Dataset
# --------------------------------
df = pd.read_csv(MASTER_DATASET)

print("=" * 60)
print("DATA CLEANING")
print("=" * 60)

print("\nOriginal Shape:", df.shape)

# --------------------------------
# Remove Literacy Rate
# --------------------------------
if "Literacy_Rate" in df.columns:
    df.drop(columns=["Literacy_Rate"], inplace=True)
    print("✓ Literacy_Rate removed")

# --------------------------------
# Fill Missing Values
# --------------------------------
df = df.ffill().bfill()

print("\nMissing Values After Cleaning")
print(df.isnull().sum())

# --------------------------------
# Save Clean Dataset
# --------------------------------
df.to_csv(OUTPUT_DATASET, index=False)

print("\n======================================")
print("Clean Dataset Saved Successfully")
print(OUTPUT_DATASET)
print("======================================")

print("\nFinal Shape:", df.shape)

print("\nFirst Five Rows")
print(df.head())