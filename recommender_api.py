import json
import os

MODEL_DIR = "model_registry"

def load_latest_model():
    versions = sorted(os.listdir(MODEL_DIR))
    latest = versions[-1]
    with open(f"{MODEL_DIR}/{latest}/model.json") as f:
        return json.load(f)

model = load_latest_model()
