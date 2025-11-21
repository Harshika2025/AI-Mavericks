
import pandas as pd

def test_basic_groupby_pipeline():
    # Create a small example dataset
    df_online = pd.DataFrame({
        "source": ["web", "web", "app"],
        "value": [10, 20, 5]
    })

    # Pipeline logic
    group_metrics = df_online.groupby("source").agg({"value": "sum"})

    # Assertions
    assert group_metrics.loc["web", "value"] == 30
    assert group_metrics.loc["app", "value"] == 5

