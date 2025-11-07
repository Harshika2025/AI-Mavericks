import sys, os
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from offline_eval import safe_mean

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
    assert os.path.exists("purchase_snapshot.parquet")
    assert os.path.exists("view_snapshot.parquet")

def test_offline_metrics_file_creation():
    """Check if the offline metrics chart file is generated"""
    os.system("python3 offline_eval.py")
    assert os.path.exists("offline_metrics_fixed.png")
