import os
import json
import pandas as pd
from datetime import datetime

# ======================================================
# IMPORT MODEL TRAINING FUNCTIONS FROM train_models.py
# ======================================================
from product_trend_tracker.train_models import train_popularity_model


# ======================================================
# 1. Find latest snapshot in snapshots_downloaded/
# ======================================================
def get_latest_snapshot():
    folder = "snapshots_downloaded"
    if not os.path.exists(folder):
        raise FileNotFoundError("snapshots_downloaded/ folder does not exist")

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".csv") or f.endswith(".parquet")
    ]

    if not files:
        raise FileNotFoundError("No snapshot files found in snapshots_downloaded/")

    latest = max(files, key=os.path.getmtime)
    return latest


# ======================================================
# 2. Create next version number
# ======================================================
def get_next_model_version():
    registry = "model_registry"
    os.makedirs(registry, exist_ok=True)

    versions = [
        d for d in os.listdir(registry)
        if d.startswith("v") and d[1:].isdigit()
    ]

    if not versions:
        return "v1"

    numbers = [int(v[1:]) for v in versions]
    next_num = max(numbers) + 1

    return f"v{next_num}"


# ======================================================
# 3. Save model and metadata
# ======================================================
def save_model_and_metadata(model_dict, version, snapshot_path):
    save_dir = f"model_registry/{version}"
    os.makedirs(save_dir, exist_ok=True)

    # Save model
    model_file = os.path.join(save_dir, "model.json")
    with open(model_file, "w") as f:
        json.dump(model_dict, f)

    # Save metadata
    metadata = {
        "version": version,
        "snapshot_used": snapshot_path,
        "created_at": datetime.utcnow().isoformat()
    }

    metadata_file = os.path.join(save_dir, "metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print("✔ Model saved at:", model_file)
    print("✔ Metadata saved at:", metadata_file)


# ======================================================
# 4. MAIN WORKFLOW
# ======================================================
def main():
    print("\n=== STEP 1: Finding latest snapshot ===")
    snapshot = get_latest_snapshot()
    print("➡ Snapshot used:", snapshot)

    print("\n=== STEP 2: Loading snapshot ===")
    if snapshot.endswith(".parquet"):
        df = pd.read_parquet(snapshot)
    else:
        df = pd.read_csv(snapshot)
    print("✔ Loaded:", len(df), "rows")

    print("\n=== STEP 3: Training model ===")
    model = train_popularity_model(df)

    print("\n=== STEP 4: Creating new version ===")
    version = get_next_model_version()
    print("New model version:", version)

    print("\n=== STEP 5: Saving new model ===")
    save_model_and_metadata(model, version, snapshot)

    print("\n Training + Publishing completed! \n")


# ======================================================
# Run script
# ======================================================
if __name__ == "__main__":
    main()
