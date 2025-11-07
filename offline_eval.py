import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- Load data from existing parquet or CSV files ---
if os.path.exists("purchase_snapshot.parquet"):
    purchase_df = pd.read_parquet("purchase_snapshot.parquet")
    print("✅ Loaded purchase_snapshot.parquet")
else:
    print("⚠️ purchase_snapshot.parquet not found!")

if os.path.exists("view_snapshot.parquet"):
    view_df = pd.read_parquet("view_snapshot.parquet")
    print("✅ Loaded view_snapshot.parquet")
else:
    print("⚠️ view_snapshot.parquet not found!")

# --- Combine the two snapshots (inner join on product_id if both exist) ---
if "product_id" in purchase_df.columns and "product_id" in view_df.columns:
    data = pd.merge(view_df, purchase_df, on="product_id", how="outer", suffixes=("_view", "_purchase"))
else:
    # fallback if columns differ
    data = pd.concat([purchase_df, view_df], ignore_index=True)

print(f"📊 Combined dataset shape: {data.shape}")

# --- Ensure a timestamp column exists (fallback to index if not) ---
if "timestamp" not in data.columns:
    data["timestamp"] = pd.date_range("2024-01-01", periods=len(data))

# --- Simulate user and product IDs if missing ---
if "user_id" not in data.columns:
    data["user_id"] = np.random.randint(1, 100, size=len(data))
if "product_id" not in data.columns:
    data["product_id"] = np.arange(len(data))

# --- Split into train and test sets ---
data = data.sort_values("timestamp")
split_index = int(0.8 * len(data))
train_data = data.iloc[:split_index]
test_data = data.iloc[split_index:]
test_users = test_data["user_id"].unique().tolist()

# --- Simple recommender baseline ---
recommendations = {}
top_items = train_data["product_id"].value_counts().index[:5].tolist()
for user in test_users:
    recommendations[user] = top_items

# --- Safe metric calculation ---
def safe_mean(values):
    arr = np.array(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    return arr.mean() if len(arr) > 0 else 0.0

hr_values, ndcg_values = [], []
for user in test_users:
    true_items = test_data[test_data["user_id"] == user]["product_id"].tolist()
    recs = recommendations.get(user, [])

    if not true_items:
        continue

    hr = 1.0 if any(item in recs for item in true_items) else 0.0
    ndcg = 0.0
    for i, rec in enumerate(recs[:5]):
        if rec in true_items:
            ndcg += 1 / np.log2(i + 2)
    hr_values.append(hr)
    ndcg_values.append(ndcg)

HR5 = safe_mean(hr_values)
NDCG5 = safe_mean(ndcg_values)

print(f"\n✅ HR@5 = {HR5:.2f}, NDCG@5 = {NDCG5:.2f}")

plt.bar(["HR@5", "NDCG@5"], [HR5, NDCG5])
plt.title("Offline Evaluation Metrics")
plt.ylabel("Score")
plt.savefig("offline_metrics_fixed.png")
plt.show()

import matplotlib.pyplot as plt

# --- Plot metrics ---
plt.bar(["HR@5", "NDCG@5"], [HR5, NDCG5], color=["skyblue", "lightgreen"])
plt.title("Offline Evaluation Metrics")
plt.ylabel("Score")
plt.ylim(0, 1)  # values between 0 and 1
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Save and show the chart
plt.savefig("offline_metrics_fixed.png")
print("📊 Chart saved as offline_metrics_fixed.png")

plt.show()  # this will open a window showing the chart
