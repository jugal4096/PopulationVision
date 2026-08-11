import os
import glob
import numpy as np
import pandas as pd


# ============================================================
# PATH CONFIGURATION
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

RAW_MASTER_DATASET = os.path.join(
    DATASET_DIR,
    "india_master_dataset.csv"
)

CLEAN_DATASET = os.path.join(
    DATASET_DIR,
    "india_clean_dataset.csv"
)

FEATURE_DATASET = os.path.join(
    DATASET_DIR,
    "india_features_dataset.csv"
)

CORRELATION_DATASET = os.path.join(
    DATASET_DIR,
    "correlation_matrix.csv"
)


# ============================================================
# GENERATED FILES
# These files are produced by our pipeline and must NOT
# be treated as official source datasets.
# ============================================================

IGNORE_FILES = {
    "india_master_dataset.csv",
    "india_clean_dataset.csv",
    "india_features_dataset.csv",
    "correlation_matrix.csv",

    "model_fit_result.csv",

    "X_train_scaled.csv",
    "X_test_scaled.csv",
    "X_trained_scale.csv",

    "y_train.csv",
    "y_test.csv"
}


# ============================================================
# YEARS
# ============================================================

YEAR_COLUMNS = [
    str(year)
    for year in range(1960, 2026)
]


# ============================================================
# WDI INDICATOR MAP
#
# IMPORTANT:
#
# We identify the data using the OFFICIAL WORLD BANK
# INDICATOR CODE.
#
# We DO NOT trust the filename.
# ============================================================

INDICATOR_MAP = {

    # --------------------------------------------------------
    # Population
    # --------------------------------------------------------

    "SP.POP.TOTL":
        "Population",

    "SP.POP.GROW":
        "Population_Growth",

    "EN.POP.DNST":
        "Population_Density",


    # --------------------------------------------------------
    # Age structure
    # --------------------------------------------------------

    "SP.POP.0014.TO.ZS":
        "Age_0_14",

    "SP.POP.1564.TO.ZS":
        "Age_15_64",

    "SP.POP.65UP.TO.ZS":
        "Age_65_Plus",

    "SP.POP.DPND":
        "Age_Dependency",


    # --------------------------------------------------------
    # Birth / Death / Fertility
    # --------------------------------------------------------

    "SP.DYN.CBRT.IN":
        "Birth_Rate",

    "SP.DYN.CDRT.IN":
        "Death_Rate",

    "SP.DYN.TFRT.IN":
        "Fertility_Rate",


    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------

    "SP.DYN.IMRT.IN":
        "Infant_Mortality",

    "SP.DYN.LE00.IN":
        "Life_Expectancy",


    # --------------------------------------------------------
    # Migration
    # --------------------------------------------------------

    "SM.POP.NETM":
        "Net_Migration",


    # --------------------------------------------------------
    # Urban / Rural
    # --------------------------------------------------------

    "SP.URB.TOTL.IN.ZS":
        "Urban_Population",

    "SP.RUR.TOTL":
        "Rural_Population",

    # Some WDI exports may use rural percentage.
    "SP.RUR.TOTL.ZS":
        "Rural_Population",


    # --------------------------------------------------------
    # Economy
    # --------------------------------------------------------

    "NY.GDP.MKTP.KD.ZG":
        "GDP_Growth",


    # --------------------------------------------------------
    # Literacy
    # --------------------------------------------------------

    "SE.ADT.LITR.ZS":
        "Literacy_Rate",


    # --------------------------------------------------------
    # Labour
    #
    # SL.TLF.TOTL.IN = total labour force
    #
    # SL.TLF.CACT.ZS = labour force participation rate
    #
    # We support both.
    # --------------------------------------------------------

    "SL.TLF.TOTL.IN":
        "Labor_Force",

    "SL.TLF.CACT.ZS":
        "Labor_Force_Participation"
}


# ============================================================
# EXPECTED SOURCE FEATURES
# ============================================================

EXPECTED_SOURCE_FEATURES = {
    "Population",
    "Population_Growth",
    "Population_Density",

    "Age_0_14",
    "Age_15_64",
    "Age_65_Plus",
    "Age_Dependency",

    "Birth_Rate",
    "Death_Rate",
    "Fertility_Rate",

    "Infant_Mortality",
    "Life_Expectancy",

    "Net_Migration",

    "Urban_Population",
    "Rural_Population",

    "GDP_Growth",

    "Literacy_Rate",

    "Labor_Force",
    "Labor_Force_Participation"
}


# ============================================================
# PROCESSOR
# ============================================================

class IndiaDatasetProcessor:

    def __init__(self):

        self.master = pd.DataFrame()
        self.cleaned = pd.DataFrame()
        self.features = pd.DataFrame()

        self.processed = []
        self.skipped = []
        self.failed = []

        self.loaded_indicators = set()

        self.file_indicator_map = {}

        self.filename_mismatches = []


    # ========================================================
    # DISCOVER SOURCE FILES
    # ========================================================

    def discover_files(self):

        files = []

        csv_files = glob.glob(
            os.path.join(
                DATASET_DIR,
                "*.csv"
            )
        )

        for filepath in csv_files:

            filename = os.path.basename(filepath)

            filename_lower = filename.lower()

            # ------------------------------------------------
            # Ignore generated files
            # ------------------------------------------------

            if filename in IGNORE_FILES:
                continue

            # ------------------------------------------------
            # Ignore ML artifacts
            # ------------------------------------------------

            if (
                "train" in filename_lower
                or "test" in filename_lower
                or "scaled" in filename_lower
                or "model_fit" in filename_lower
                or "correlation" in filename_lower
            ):
                continue

            files.append(filepath)

        files.sort()

        print("=" * 80)
        print("AI POPULATION FORECASTING SYSTEM")
        print("=" * 80)

        print(
            f"CSV source files discovered : {len(files)}"
        )

        print("\nSource files:")

        for filepath in files:

            print(
                f"  - {os.path.basename(filepath)}"
            )

        return files


    # ========================================================
    # READ WDI CSV
    # ========================================================

    def read_wdi_file(self, filepath):

        filename = os.path.basename(filepath)

        try:

            df = pd.read_csv(
                filepath,
                skiprows=4
            )

        except Exception as e:

            print(
                f"❌ Error reading {filename}: {e}"
            )

            self.failed.append(filename)

            return None

        required_columns = [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            print(
                f"❌ {filename}: missing columns:"
            )

            for column in missing_columns:

                print(
                    f"   - {column}"
                )

            self.failed.append(filename)

            return None

        return df


    # ========================================================
    # LOAD DATASET
    # ========================================================

    def load_dataset(self, filepath):

        filename = os.path.basename(filepath)

        print("\n" + "-" * 80)

        print(
            f"Loading: {filename}"
        )

        df = self.read_wdi_file(filepath)

        if df is None:
            return None


        # ====================================================
        # IDENTIFY ACTUAL INDICATOR
        # ====================================================

        indicator_codes = (
            df["Indicator Code"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        if len(indicator_codes) == 0:

            print(
                f"❌ {filename}: "
                f"no Indicator Code found."
            )

            self.failed.append(filename)

            return None


        # ----------------------------------------------------
        # A WDI indicator CSV should normally contain
        # one indicator.
        # ----------------------------------------------------

        if len(indicator_codes) > 1:

            print(
                f"⚠️ Multiple indicator codes found:"
            )

            for code in indicator_codes:

                print(
                    f"   - {code}"
                )


        indicator_code = indicator_codes[0]


        # ====================================================
        # GET ACTUAL INDICATOR NAME
        # ====================================================

        indicator_rows = df[
            df["Indicator Code"].astype(str).str.strip()
            == indicator_code
        ]

        if indicator_rows.empty:

            print(
                f"❌ Could not identify indicator "
                f"for {filename}"
            )

            self.failed.append(filename)

            return None


        actual_indicator_name = (
            indicator_rows[
                "Indicator Name"
            ]
            .dropna()
            .astype(str)
            .iloc[0]
        )


        print(
            f"Actual WDI Code   : {indicator_code}"
        )

        print(
            f"Actual WDI Name   : {actual_indicator_name}"
        )


        # ====================================================
        # CHECK WHETHER WE SUPPORT THIS INDICATOR
        # ====================================================

        if indicator_code not in INDICATOR_MAP:

            print(
                f"⚠️ Unsupported indicator:"
            )

            print(
                f"   {indicator_code}"
            )

            print(
                f"   File skipped."
            )

            self.skipped.append(filename)

            return None


        feature_name = INDICATOR_MAP[
            indicator_code
        ]


        print(
            f"Our feature name  : {feature_name}"
        )


        # ====================================================
        # DETECT DUPLICATE INDICATORS
        # ====================================================

        if feature_name in self.loaded_indicators:

            print(
                f"⚠️ Duplicate indicator detected:"
            )

            print(
                f"   {feature_name}"
            )

            print(
                f"   File skipped: {filename}"
            )

            self.skipped.append(filename)

            return None


        # ====================================================
        # DETECT FILENAME / INDICATOR MISMATCH
        # ====================================================

        expected_filename_mapping = {

            "age_0_14.csv":
                "Age_0_14",

            "age_15_64.csv":
                "Age_15_64",

            "age_65_plus.csv":
                "Age_65_Plus",

            "age_dependency.csv":
                "Age_Dependency",

            "birth_rate.csv":
                "Birth_Rate",

            "death_rate.csv":
                "Death_Rate",

            "fertility_rate.csv":
                "Fertility_Rate",

            "gdp_growth.csv":
                "GDP_Growth",

            "infant_mortality.csv":
                "Infant_Mortality",

            "labor_force.csv":
                "Labor_Force",

            "life_expectancy.csv":
                "Life_Expectancy",

            "literacy_rate.csv":
                "Literacy_Rate",

            "net_migration.csv":
                "Net_Migration",

            "population.csv":
                "Population",

            "population_density.csv":
                "Population_Density",

            "population_growth.csv":
                "Population_Growth",

            "rural_population.csv":
                "Rural_Population",

            "urban_population.csv":
                "Urban_Population"
        }


        expected_feature = (
            expected_filename_mapping.get(
                filename
            )
        )


        if (
            expected_feature is not None
            and
            expected_feature != feature_name
        ):

            print(
                f"⚠️ Filename/content mismatch:"
            )

            print(
                f"   Filename suggests : "
                f"{expected_feature}"
            )

            print(
                f"   Actual WDI data   : "
                f"{feature_name}"
            )

            print(
                f"   Using actual WDI indicator."
            )

            self.filename_mismatches.append({

                "file":
                    filename,

                "filename_suggests":
                    expected_feature,

                "actual_indicator":
                    feature_name,

                "indicator_code":
                    indicator_code
            })


        # ====================================================
        # FIND INDIA
        # ====================================================

        india = df[
            df["Country Code"]
            .astype(str)
            .str.strip()
            == "IND"
        ]


        # ----------------------------------------------------
        # Fallback to Country Name
        # ----------------------------------------------------

        if india.empty:

            india = df[
                df["Country Name"]
                .astype(str)
                .str.strip()
                == "India"
            ]


        if india.empty:

            print(
                f"❌ India not found in {filename}"
            )

            self.failed.append(filename)

            return None


        india = india.iloc[0]


        # ====================================================
        # EXTRACT YEARS
        # ====================================================

        years = []

        values = []


        for year in YEAR_COLUMNS:

            years.append(
                int(year)
            )

            if year in india.index:

                value = india[year]

            else:

                value = np.nan

            values.append(value)


        # ====================================================
        # BUILD DATAFRAME
        # ====================================================

        output = pd.DataFrame({

            "Year":
                years,

            feature_name:
                values
        })


        # ====================================================
        # NUMERIC CONVERSION
        # ====================================================

        output[feature_name] = pd.to_numeric(
            output[feature_name],
            errors="coerce"
        )


        # ====================================================
        # RECORD SUCCESS
        # ====================================================

        self.processed.append(
            filename
        )

        self.loaded_indicators.add(
            feature_name
        )

        self.file_indicator_map[
            filename
        ] = {

            "indicator_code":
                indicator_code,

            "indicator_name":
                actual_indicator_name,

            "feature_name":
                feature_name
        }


        print(
            f"✅ Successfully loaded "
            f"{feature_name}"
        )


        return output


    # ========================================================
    # MERGE DATASET
    # ========================================================

    def merge_dataset(self, df):

        if df is None:
            return


        if self.master.empty:

            self.master = df.copy()

        else:

            self.master = pd.merge(
                self.master,
                df,
                on="Year",
                how="outer"
            )


    # ========================================================
    # BUILD MASTER DATASET
    # ========================================================

    def build_master_dataset(self):

        files = self.discover_files()

        if not files:

            print(
                "❌ No source datasets found."
            )

            return


        for filepath in files:

            df = self.load_dataset(
                filepath
            )

            self.merge_dataset(
                df
            )


        if self.master.empty:

            print(
                "❌ Master dataset is empty."
            )

            return


        # ====================================================
        # SORT
        # ====================================================

        self.master.sort_values(
            by="Year",
            inplace=True
        )

        self.master.reset_index(
            drop=True,
            inplace=True
        )


        # ====================================================
        # YEAR TYPE
        # ====================================================

        self.master["Year"] = (
            pd.to_numeric(
                self.master["Year"],
                errors="coerce"
            )
            .astype("Int64")
        )


        # ====================================================
        # SAVE RAW MASTER
        #
        # IMPORTANT:
        #
        # NO INTERPOLATION
        # NO FEATURE ENGINEERING
        #
        # This remains closest to official source data.
        # ====================================================

        self.master.to_csv(
            RAW_MASTER_DATASET,
            index=False
        )


        print("\n" + "=" * 80)

        print(
            "RAW MASTER DATASET CREATED"
        )

        print("=" * 80)

        print(
            f"Shape: {self.master.shape}"
        )

        print(
            f"Saved to:\n{RAW_MASTER_DATASET}"
        )


        print(
            "\nColumns:"
        )

        for column in self.master.columns:

            print(
                f"  - {column}"
            )


    # ========================================================
    # CLEAN DATASET
    # ========================================================

    def clean_dataset(self):

        if self.master.empty:
            return


        df = self.master.copy()


        # ====================================================
        # SORT
        # ====================================================

        df.sort_values(
            "Year",
            inplace=True
        )


        df.reset_index(
            drop=True,
            inplace=True
        )


        # ====================================================
        # NUMERIC CONVERSION
        # ====================================================

        numeric_columns = [
            column
            for column in df.columns
            if column != "Year"
        ]


        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


        # ====================================================
        # REMOVE DUPLICATE YEARS
        # ====================================================

        df.drop_duplicates(
            subset=["Year"],
            keep="first",
            inplace=True
        )


        # ====================================================
        # MISSING DATA
        #
        # Only interpolate INTERNAL gaps.
        #
        # We do not blindly fabricate data outside
        # the observed range.
        # ====================================================

        for column in numeric_columns:

            df[column] = df[column].interpolate(
                method="linear",
                limit_area="inside"
            )


        # ====================================================
        # EDGE VALUES
        #
        # If a variable has missing values at the beginning
        # or end, use nearest valid observation.
        #
        # This is applied only when the column actually
        # contains some real observations.
        # ====================================================

        for column in numeric_columns:

            if df[column].notna().any():

                df[column] = (
                    df[column]
                    .ffill()
                    .bfill()
                )


        # ====================================================
        # REMOVE INFINITE VALUES
        # ====================================================

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True
        )


        # ====================================================
        # SAVE CLEAN DATASET
        # ====================================================

        self.cleaned = df.copy()

        self.cleaned.to_csv(
            CLEAN_DATASET,
            index=False
        )


        print("\n" + "=" * 80)

        print(
            "CLEAN DATASET CREATED"
        )

        print("=" * 80)

        print(
            f"Shape: {self.cleaned.shape}"
        )

        print(
            f"Saved to:\n{CLEAN_DATASET}"
        )


    # ========================================================
    # FEATURE ENGINEERING
    # ========================================================

    def create_features(self):

        if self.cleaned.empty:
            return


        df = self.cleaned.copy()


        # ====================================================
        # POPULATION LAGS
        # ====================================================

        if "Population" in df.columns:

            df["Population_Lag_1"] = (
                df["Population"].shift(1)
            )

            df["Population_Lag_2"] = (
                df["Population"].shift(2)
            )

            df["Population_Lag_3"] = (
                df["Population"].shift(3)
            )


        # ====================================================
        # BIRTH / DEATH LAGS
        # ====================================================

        if "Birth_Rate" in df.columns:

            df["Birth_Rate_Lag"] = (
                df["Birth_Rate"].shift(1)
            )


        if "Death_Rate" in df.columns:

            df["Death_Rate_Lag"] = (
                df["Death_Rate"].shift(1)
            )


        # ====================================================
        # POPULATION MOVING AVERAGES
        # ====================================================

        if "Population" in df.columns:

            df["Population_MA_3"] = (
                df["Population"]
                .rolling(
                    window=3,
                    min_periods=1
                )
                .mean()
            )

            df["Population_MA_5"] = (
                df["Population"]
                .rolling(
                    window=5,
                    min_periods=1
                )
                .mean()
            )


        # ====================================================
        # BIRTH / DEATH RATIO
        # ====================================================

        if (
            "Birth_Rate" in df.columns
            and
            "Death_Rate" in df.columns
        ):

            df["Birth_Death_Ratio"] = (
                df["Birth_Rate"]
                /
                df["Death_Rate"].replace(
                    0,
                    np.nan
                )
            )


        # ====================================================
        # IMPORTANT PERCENTAGE VARIABLES
        #
        # WDI gives these as percentages:
        #
        # Age_0_14 = 40.58
        # Age_15_64 = 56.11
        # Urban_Population = 17.92
        #
        # Therefore convert them into proportions:
        #
        # 40.58 / 100 = 0.4058
        #
        # DO NOT divide these by Population.
        # ====================================================

        if "Urban_Population" in df.columns:

            df["Urbanization_Rate"] = (
                df["Urban_Population"] / 100.0
            )


        if( "Rural_Population" in df.columns and "Population" in df.columns):

            # If WDI gives rural population as percentage
            # rather than absolute population.
            #
            # SP.RUR.TOTL is normally percentage of total
            # population in WDI exports.
            df["Ruralization_Rate"] = (
                df["Rural_Population"] / df["Population"]
            )


        if "Age_15_64" in df.columns:

            df["Working_Age_Ratio"] = (
                df["Age_15_64"] / 100.0
            )


        if "Age_0_14" in df.columns:

            df["Child_Ratio"] = (
                df["Age_0_14"] / 100.0
            )


        if "Age_65_Plus" in df.columns:

            df["Senior_Ratio"] = (
                df["Age_65_Plus"] / 100.0
            )


        # ====================================================
        # POPULATION CHANGE
        # ====================================================

        if "Population" in df.columns:

            df["Population_Change"] = (
                df["Population"].pct_change()
            )


        # ====================================================
        # BIRTH RATE CHANGE
        # ====================================================

        if "Birth_Rate" in df.columns:

            df["BirthRate_Change"] = (
                df["Birth_Rate"].pct_change()
            )


        # ====================================================
        # DEATH RATE CHANGE
        # ====================================================

        if "Death_Rate" in df.columns:

            df["DeathRate_Change"] = (
                df["Death_Rate"].pct_change()
            )


        # ====================================================
        # GDP CHANGE
        # ====================================================

        if "GDP_Growth" in df.columns:

            df["GDP_Change"] = (
                df["GDP_Growth"].pct_change()
            )


        # ====================================================
        # LIFE EXPECTANCY CHANGE
        # ====================================================

        if "Life_Expectancy" in df.columns:

            df["LifeExp_Change"] = (
                df["Life_Expectancy"].pct_change()
            )


        # ====================================================
        # MIGRATION CHANGE
        #
        # IMPORTANT:
        #
        # Percentage change is unstable when migration
        # approaches or crosses zero.
        #
        # Therefore use absolute year-to-year change.
        # ====================================================

        if "Net_Migration" in df.columns:

            df["Migration_Change"] = (
                df["Net_Migration"].diff()
            )


        # ====================================================
        # REPLACE INFINITY
        # ====================================================

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True
        )


        # ====================================================
        # CLEAN FEATURE-GENERATED NaN VALUES
        # ====================================================

        numeric_columns = [
            column
            for column in df.columns
            if column != "Year"
        ]


        for column in numeric_columns:

            df[column] = df[column].interpolate(
                method="linear",
                limit_area="inside"
            )


        for column in numeric_columns:

            if df[column].notna().any():

                df[column] = (
                    df[column]
                    .ffill()
                    .bfill()
                )


        # ====================================================
        # SAVE FEATURE DATASET
        # ====================================================

        self.features = df.copy()

        self.features.to_csv(
            FEATURE_DATASET,
            index=False
        )


        print("\n" + "=" * 80)

        print(
            "FEATURE DATASET CREATED"
        )

        print("=" * 80)

        print(
            f"Shape: {self.features.shape}"
        )

        print(
            f"Saved to:\n{FEATURE_DATASET}"
        )


    # ========================================================
    # VALIDATE DATASET
    # ========================================================

    def validate_dataset(self):

        if self.features.empty:
            return


        df = self.features


        print("\n" + "=" * 80)

        print(
            "DATASET VALIDATION"
        )

        print("=" * 80)


        print(
            f"\nShape: {df.shape}"
        )


        print(
            f"Year range: "
            f"{df['Year'].min()} - "
            f"{df['Year'].max()}"
        )


        # ====================================================
        # DUPLICATES
        # ====================================================

        print(
            "\nDuplicate rows:",
            df.duplicated().sum()
        )


        print(
            "Duplicate years:",
            df["Year"].duplicated().sum()
        )


        # ====================================================
        # MISSING VALUES
        # ====================================================

        missing = df.isnull().sum()

        missing = missing[
            missing > 0
        ]


        print(
            "\nRemaining missing values:"
        )


        if missing.empty:

            print(
                "✅ None"
            )

        else:

            print(
                missing
            )


        # ====================================================
        # DATA TYPES
        # ====================================================

        print(
            "\nData types:"
        )

        print(
            df.dtypes
        )


        # ====================================================
        # STATISTICS
        # ====================================================

        print(
            "\nDescriptive statistics:"
        )

        print(
            df.describe()
        )


    # ========================================================
    # CHECK INDICATORS
    # ========================================================

    def check_indicators(self):

        if self.master.empty:
            return


        available = set(
            self.master.columns
        )


        print("\n" + "=" * 80)

        print(
            "SOURCE INDICATOR CHECK"
        )

        print("=" * 80)


        print(
            f"\nIndicators available: "
            f"{len(available - {'Year'})}"
        )


        print(
            "\nAvailable source indicators:"
        )

        for column in self.master.columns:

            if column != "Year":

                print(
                    f"  ✅ {column}"
                )


        # ----------------------------------------------------
        # Missing expected indicators
        # ----------------------------------------------------

        missing = (
            EXPECTED_SOURCE_FEATURES
            - available
        )


        if missing:

            print(
                "\n⚠️ Expected indicators "
                "not currently available:"
            )

            for column in sorted(missing):

                print(
                    f"  ❌ {column}"
                )

        else:

            print(
                "\n✅ All supported indicators "
                "are available."
            )


    # ========================================================
    # FILE MISMATCH REPORT
    # ========================================================

    def show_mismatch_report(self):

        print("\n" + "=" * 80)

        print(
            "FILENAME / CONTENT REPORT"
        )

        print("=" * 80)


        if not self.filename_mismatches:

            print(
                "\n✅ No filename/content mismatches detected."
            )

            return


        print(
            "\n⚠️ The following files contain an indicator "
            "different from what their filename suggests:"
        )


        for mismatch in self.filename_mismatches:

            print(
                "\nFile:"
            )

            print(
                f"  {mismatch['file']}"
            )

            print(
                f"  Filename suggests : "
                f"{mismatch['filename_suggests']}"
            )

            print(
                f"  Actual WDI data   : "
                f"{mismatch['actual_indicator']}"
            )

            print(
                f"  WDI code          : "
                f"{mismatch['indicator_code']}"
            )


        print(
            "\nIMPORTANT:"
        )

        print(
            "The source CSV files were NOT modified."
        )

        print(
            "The pipeline uses the actual WDI indicator."
        )


    # ========================================================
    # CORRELATION MATRIX
    # ========================================================

    def generate_correlation(self):

        if self.features.empty:
            return


        correlation = (
            self.features
            .corr(
                numeric_only=True
            )
        )


        correlation.to_csv(
            CORRELATION_DATASET
        )


        print("\n" + "=" * 80)

        print(
            "CORRELATION MATRIX CREATED"
        )

        print("=" * 80)


        print(
            CORRELATION_DATASET
        )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    def save_dataset(self):

        print("\n" + "=" * 80)

        print(
            "DATASET OUTPUTS"
        )

        print("=" * 80)


        print(
            "\nRaw master:"
        )

        print(
            RAW_MASTER_DATASET
        )


        print(
            "\nClean dataset:"
        )

        print(
            CLEAN_DATASET
        )


        print(
            "\nFeature dataset:"
        )

        print(
            FEATURE_DATASET
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(self):

        print("\n" + "=" * 80)

        print(
            "PROCESSING SUMMARY"
        )

        print("=" * 80)


        # ====================================================
        # PROCESSED
        # ====================================================

        print(
            f"\nProcessed files : "
            f"{len(self.processed)}"
        )


        for filename in self.processed:

            print(
                f"  ✓ {filename}"
            )


        # ====================================================
        # SKIPPED
        # ====================================================

        print(
            f"\nSkipped files : "
            f"{len(self.skipped)}"
        )


        for filename in self.skipped:

            print(
                f"  ⚠ {filename}"
            )


        # ====================================================
        # FAILED
        # ====================================================

        print(
            f"\nFailed files : "
            f"{len(self.failed)}"
        )


        if self.failed:

            for filename in self.failed:

                print(
                    f"  ✗ {filename}"
                )

        else:

            print(
                "  None"
            )


        # ====================================================
        # MISMATCHES
        # ====================================================

        print(
            f"\nFilename/content mismatches : "
            f"{len(self.filename_mismatches)}"
        )


        for mismatch in self.filename_mismatches:

            print(
                f"  ⚠ {mismatch['file']} "
                f"→ {mismatch['actual_indicator']}"
            )


        # ====================================================
        # FINAL DATASET
        # ====================================================

        if not self.features.empty:

            print(
                f"\nFinal dataset shape: "
                f"{self.features.shape}"
            )


            print(
                "\nFinal columns:"
            )


            for column in self.features.columns:

                print(
                    f"  - {column}"
                )


        print(
            "\n" + "=" * 80
        )

        print(
            "PROCESSING COMPLETED"
        )

        print("=" * 80)


# ============================================================
# MAIN
# ============================================================

def main():

    processor = IndiaDatasetProcessor()


    # --------------------------------------------------------
    # STEP 1
    # Read official WDI files
    # --------------------------------------------------------

    processor.build_master_dataset()


    # --------------------------------------------------------
    # STEP 2
    # Clean source-derived data
    # --------------------------------------------------------

    processor.clean_dataset()


    # --------------------------------------------------------
    # STEP 3
    # Create ML features
    # --------------------------------------------------------

    processor.create_features()


    # --------------------------------------------------------
    # STEP 4
    # Validate
    # --------------------------------------------------------

    processor.validate_dataset()


    # --------------------------------------------------------
    # STEP 5
    # Check available indicators
    # --------------------------------------------------------

    processor.check_indicators()


    # --------------------------------------------------------
    # STEP 6
    # Report filename mismatches
    # --------------------------------------------------------

    processor.show_mismatch_report()


    # --------------------------------------------------------
    # STEP 7
    # Correlation matrix
    # --------------------------------------------------------

    processor.generate_correlation()


    # --------------------------------------------------------
    # STEP 8
    # Output locations
    # --------------------------------------------------------

    processor.save_dataset()


    # --------------------------------------------------------
    # STEP 9
    # Final summary
    # --------------------------------------------------------

    processor.summary()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()