import os
import json
import glob
from datetime import datetime
import subprocess
import joblib
import pandas as pd

from train_models import train_popularity_model, load_data   # your existing functions

MODEL_REGISTRY = "model_registry"


# ===============================
# Helper: Auto-find latest snapshot
# ===============================
def get_latest_snapshot():
    files = glob.glob("*.parquet") + glob.glob("*.csv")
    if not files:
        raise Exception("No snapshot files found!")
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


# ===============================
# Helper: Auto-increment version
# ===============================
def get_next_model_version():
    versions = [d for d in os.listdir(MODEL_REGISTRY) if d.startswith("v")]
    if not versions:
        return "v1.0"

    versions.sort()
    last = versions[-1]       # v1.1
    major, minor = map(int, last[1:].split("."))
    return f"v{major}.{minor + 1}"    # -> v1.2


# ===============================
# Helper: Git SHA for provenance
# ===============================
def get_git_sha():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        return sha
    except:
        return "unknown"


# ===============================
# Save model + metadata
# ===============================
def save_model_and_metadata(model, version, snapshot_name):
    model_dir = os.path.join(MODEL_REGISTRY, version)
    os.makedirs(model_dir, exist_ok=True)

    # Save model
    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_path)

    # Metadata
    metadata = {
        "model_version": version,
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "data_snapshot_id": snapshot_name,
        "pipeline_git_sha": get_git_sha(),
        "model_type": "popularity_weighted",
    }

    with open(os.path.join(model_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    # Update latest.txt
    with open(os.path.join(MODEL_REGISTRY, "latest.txt"), "w") as f:
        f.write(version)

    print(f"\nSaved {version} into model_registry/")
    print("Model:", model_path)
    print("Metadata:", os.path.join(model_dir, "metadata.json"))
    print("Updated latest.txt\n")


# ===============================
# Main workflow
# ===============================
def main():
    print("\n=== STEP 1: Finding latest snapshot ===")
    snapshot = get_latest_snapshot()
    print("Snapshot used:", snapshot)

    print("\n=== STEP 2: Loading snapshot ===")
    df = pd.read_parquet(snapshot) if snapshot.endswith(".parquet") else pd.read_csv(snapshot)

    print("\n=== STEP 3: Training model ===")
    model = train_popularity_model(df)

    print("\n=== STEP 4: Creating new version ===")
    version = get_next_model_version()
    print("New version:", version)

    print("\n=== STEP 5: Saving new model ===")
    save_model_and_metadata(model, version, snapshot)

    print("\nTraining + Publishing completed! 🚀\n")


if __name__ == "__main__":
    main()
