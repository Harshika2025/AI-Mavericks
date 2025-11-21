import pandas as pd
import joblib

import glob
import pandas as pd

def load_latest_snapshot():
    """
    Loads the most recent purchase snapshot file (.parquet or .csv)
    so that tests and API both work.
    """
    # Look for all snapshot files inside project root or snapshots folder
    files = glob.glob("*.parquet") + glob.glob("*.csv") + glob.glob("**/*.parquet", recursive=True)

    if not files:
        raise FileNotFoundError("No snapshot files found for load_latest_snapshot()")

    # Most recent file based on filename timestamp or modification time
    latest = max(files)

    print(f"[load_latest_snapshot] Loading snapshot: {latest}")

    if latest.endswith(".parquet"):
        return pd.read_parquet(latest)
    else:
        return pd.read_csv(latest)

# ===============================
# LOAD DATA
# ===============================
def load_data(path):
    """Load snapshot parquet or csv file."""
    print(f"Loading data from: {path}")

    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    else:
        return pd.read_csv(path)


# ===============================
# POPULARITY MODEL
# ===============================
def train_popularity_model(df):
    """
    Simple popularity model:
    Score = number of purchases per product_id
    """
    print("Training popularity model...")

    # Count how many times each product was purchased
    scores = df.groupby("product_id").size()

    # Convert to dictionary for easy use inside API
    model = scores.to_dict()

    print("Popularity model training complete.")
    return model
