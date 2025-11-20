import pandas as pd
import joblib

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
