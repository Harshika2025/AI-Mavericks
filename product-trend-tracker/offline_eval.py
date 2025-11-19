hr, ndcg = [], []
for _, row in test.iterrows():
    user = row["user_id"]
    actual_item = row["product_id"]
    if user in top_n:
        preds = top_n[user]
        hr.append(hr_at_k(actual_item, preds))
        ndcg.append(ndcg_at_k(actual_item, preds))

HR5 = np.mean(hr)
NDCG5 = np.mean(ndcg)

print(f"\n📊 HR@5 = {HR5:.3f}, NDCG@5 = {NDCG5:.3f}")

import matplotlib.pyplot as plt

plt.bar(["HR@5", "NDCG@5"], [HR5, NDCG5], color=["skyblue", "lightgreen"])
plt.title("Offline Evaluation Metrics")
plt.ylabel("Score")
plt.ylim(0, 1)

# Save chart to file (for your PDF)
plt.savefig("offline_metrics.png", dpi=150)
print("📁 Saved bar chart as offline_metrics.png")
plt.show()
