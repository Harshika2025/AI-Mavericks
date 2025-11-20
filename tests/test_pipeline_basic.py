import os
import sys
import pandas as pd

# Ensure parent directory is in path for imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from product_trend_tracker.offline_eval import safe_mean


def test_safe_mean_valid_values():
    """Test the safe_mean function with valid numeric values"""
    values = [0.4, 0.6, 0.8]
    result = safe_mean(values)
    assert abs(result - 0.6) < 1e-6


def test_safe_mean_with_nans():
    """Test that safe_mean ignores NaN values"""
    values = [0.5, float("nan"), 0.7]
    result = safe_mean(values)
    assert abs(result - 0.6) < 1e-6


def test_parquet_files_exist():
    """Verify that required snapshot files exist"""
    project_root = BASE_DIR

    assert os.path.exists(os.path.join(project_root, "purchase_snapshot.parquet"))
    assert os.path.exists(os.path.join(project_root, "view_snapshot.parquet"))


def test_offline_metrics_file_creation():
    """Check if the offline metrics chart file is generated"""
    project_root = BASE_DIR

    # Run offline_eval.py inside the package
    os.system(f"python3 {project_root}/product_trend_tracker/offline_eval.py")

    assert os.path.exists(os.path.join(project_root, "offline_metrics_fixed.png"))
