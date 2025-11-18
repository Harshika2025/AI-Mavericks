import os
import json
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq
import joblib


# ===============================
# CONFIG: MODEL REGISTRY + VERSION
# ===============================
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")
MODEL_REGISTRY = os.getenv("MODEL_REGISTRY", "model_registry")

os.makedirs(os.path.join(MODEL_REGISTRY, MODEL_VERSION), exist_ok=True)


# ===============================
# LOAD VIEW + PURCHASE SNAPSHOTS
# ===============================
def load_data():
    # Load view and purchase data
    view_df = pq.read_table("view_snapshot.parquet").to_pandas()
    purchase_df = pq.read_table("purchase_snapshot.parquet").to_pandas()

    # Add interaction weights
    view_df["weight"] = 1
    purchase_df["weight"] = 3

    # Add interaction type (optional)
    view_df["interaction_type"] = "view"
    purchase_df["interaction_type"] = "purchase"

    # Drop columns we don't need (so model is clean)
    view_df = view_df[["user_id", "product_id", "timestamp", "weight"]]
    purchase_df = purchase_df[["user_id", "product_id", "timestamp", "weight"]]

    # Combine
    df = pd.concat([view_df, purchase_df], ignore_index=True)

    # Sort chronologically
    df = df.sort_values(by=["user_id", "timestamp"])

    return df


# ===============================
# POPULARITY MODEL
# ===============================
def train_popularity_model(df):
    """
    Simple baseline: score = sum of weights per product_id
    More views + purchases → higher ranking.
    """
    scores = df.groupby("product_id")["weight"].sum()
    scores = scores.sort_values(ascending=False)

    model = {
        "product_rankings": scores.to_dict(),
        "total_products": len(scores)
    }
    return model


# ===============================
# SAVE MODEL & METADATA
# ===============================
def save_model_and_metadata(model):
    model_dir = os.path.join(MODEL_REGISTRY, MODEL_VERSION)
    os.makedirs(model_dir, exist_ok=True)

    # Save model
    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_path)

    # Save metadata
    metadata = {
        "version": MODEL_VERSION,
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "data_snapshot_id": os.getenv("DATA_SNAPSHOT_ID", "unknown_snapshot"),
        "pipeline_git_sha": os.getenv("PIPELINE_GIT_SHA", "local-dev"),
        "num_products": model["total_products"],
        "model_type": "popularity_weighted"
    }

    with open(os.path.join(model_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\nModel saved to: {model_path}")
    print(f"Metadata saved to: {model_dir}/metadata.json")


# ===============================
# MAIN TRAINING LOGIC
# ===============================
def main():
    print("\n=== Loading data ===")
    df = load_data()

    print("=== Training model ===")
    model = train_popularity_model(df)

    print(f"=== Saving model version: {MODEL_VERSION} ===")
    save_model_and_metadata(model)

    print("\nTraining complete!\n")


if __name__ == "__main__":
    main()
