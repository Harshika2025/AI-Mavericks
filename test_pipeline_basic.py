import pandas as pd

def test_basic_pipeline_groupby():
    # Create a tiny example dataset
    df_online = pd.DataFrame({
        "source": ["web", "web", "app"],
        "value": [10, 20, 5]
    })

    group_metrics = df_online.groupby("source").agg({"value": "sum"})

    # Assertions
    assert group_metrics.loc["web"]["value"] == 30
    assert group_metrics.loc["app"]["value"] == 5


