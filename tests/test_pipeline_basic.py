import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from product_trend_tracker.offline_eval import safe_mean


def test_safe_mean_valid_values():
    values = [0.4, 0.6, 0.8]
    assert abs(safe_mean(values) - 0.6) < 1e-6


def test_safe_mean_with_nans():
    values = [0.5, float("nan"), 0.7]
    assert abs(safe_mean(values) - 0.6) < 1e-6
