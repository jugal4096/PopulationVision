import os
import pandas as pd

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "india_features_dataset.csv"
)

# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"\nDataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    return df


# ==========================================================
# SPLIT DATA
# ==========================================================

def split_dataset(df):

    train = df[df["Year"] <= 2015].copy()
    test = df[df["Year"] > 2015].copy()

    X_train = train.drop(columns=["Population"])
    y_train = train["Population"]

    X_test = test.drop(columns=["Population"])
    y_test = test["Population"]

    return X_train, X_test, y_train, y_test


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("DATA LOADER TEST")
    print("=" * 70)

    df = load_dataset()

    print("\nDataset Loaded Successfully")
    print(df.head())

    print("\nDataset Shape")
    print(df.shape)

    X_train, X_test, y_train, y_test = split_dataset(df)

    print("\nTraining Samples :", len(X_train))
    print("Testing Samples  :", len(X_test))

    print("\nData Loader Working Successfully!")