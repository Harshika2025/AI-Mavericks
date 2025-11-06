# STEP 3 — Subpopulation breakdown (web vs app)
group_metrics = df_online.groupby("source").agg({
    "clicks": "sum",
    "watched_within_5min": "sum",
    "recommendations_served": "sum",
    "latency_ms": "mean"
})
group_metrics["CTR"] = group_metrics["clicks"] / group_metrics["recommendations_served"]
group_metrics["WatchRate"] = group_metrics["watched_within_5min"] / group_metrics["recommendations_served"]

print("\n📈 Subpopulation metrics:\n")
print(group_metrics[["CTR", "WatchRate", "latency_ms"]])
# STEP 4 — Save visualization
plt.bar(["CTR", "Watch Rate"], [CTR, watch_rate], color=["deepskyblue", "lightgreen"])
plt.title("Online Evaluation KPIs")
plt.ylabel("Rate")
plt.ylim(0, 1)
plt.savefig("online_eval_metrics.png", dpi=150)
print("\n📁 Saved bar chart as online_eval_metrics.png")
