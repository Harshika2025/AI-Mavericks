import time
import pandas as pd
import numpy as np
from collections import defaultdict
from pyarrow import parquet as pq

# ===============================
# LOAD VIEW + PURCHASE DATA
# ===============================

def load_data():
    view_df = pq.read_table("view_snapshot.parquet").to_pandas()
    purchase_df = pq.read_table("purchase_snapshot.parquet").to_pandas()

    # Add an interaction weight column for combining signals
    view_df["interaction_type"] = "view"
    view_df["weight"] = 1

    purchase_df["interaction_type"] = "purchase"
    purchase_df["weight"] = 3   # purchases count more than views

    # combine into a single dataset
    df = pd.concat([view_df, purchase_df], ignore_index=True)

    # sort by timestamp to ensure recency order per user
    df = df.sort_values(by=["user_id", "timestamp"])

    return df

# ===============================
# TRAIN/TEST SPLIT (Last-event split)
# ===============================
def create_train_test_split(df):
    test_rows = df.groupby("user_id").tail(1)
    train_rows = df.drop(test_rows.index)
    return train_rows, test_rows

# ===============================
# POPULARITY MODEL
# ===============================

class PopularityRecommender:
    def __init__(self):
        self.popularity = None

    def fit(self, train_df):
        self.popularity = (
            train_df.groupby("product_id")["weight"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

    def recommend(self, user_id, k=5):
        return self.popularity[:k]

# ===============================
# ITEM-ITEM COLLABORATIVE FILTERING
# ===============================

class ItemItemCF:
    def __init__(self):
        self.similarity = None
        self.user_items = None

    def fit(self, train_df):
        self.user_items = train_df.groupby("user_id")["product_id"].apply(set)

        item_cooccur = defaultdict(lambda: defaultdict(int))
        for items in self.user_items.values:  # ✅ FIXED
            for i in items:
                for j in items:
                    if i != j:
                        item_cooccur[i][j] += 1

        self.similarity = item_cooccur

    def recommend(self, user_id, k=5):
        if user_id not in self.user_items:
            return []

        seen = self.user_items[user_id]
        scores = defaultdict(int)

        for item in seen:
            for similar_item, sim_score in self.similarity[item].items():
                scores[similar_item] += sim_score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ranked_items = [item for item, score in ranked if item not in seen]

        return ranked_items[:k]

# ===============================
# METRICS
# ===============================

def hr_at_k(recommended, ground_truth):
    return 1.0 if ground_truth in recommended else 0.0

def ndcg_at_k(recommended, ground_truth):
    if ground_truth in recommended:
        rank = recommended.index(ground_truth) + 1
        return 1 / np.log2(rank + 2)
    return 0.0

# ===============================
# EVALUATE MODELS
# ===============================

def evaluate_models(train_df, test_df):
    results = []
    truth = dict(zip(test_df["user_id"], test_df["product_id"]))

    # Popularity
    pop = PopularityRecommender()
    t0 = time.perf_counter()
    pop.fit(train_df)
    pop_train_time = time.perf_counter() - t0

    pop_hits, pop_ndcgs, latency = [], [], []
    for user, gt in truth.items():
        start = time.perf_counter()
        recs = pop.recommend(user, 5)
        latency.append(time.perf_counter() - start)
        pop_hits.append(hr_at_k(recs, gt))
        pop_ndcgs.append(ndcg_at_k(recs, gt))

    results.append({
        "model": "Popularity",
        "hr@5": np.mean(pop_hits),
        "ndcg@5": np.mean(pop_ndcgs),
        "train_time_sec": pop_train_time,
        "infer_latency_ms": np.mean(latency) * 1000,
        "model_size": "tiny (list-of-ids)"
    })

    # Item-Item CF
    cf = ItemItemCF()
    t0 = time.perf_counter()
    cf.fit(train_df)
    cf_train_time = time.perf_counter() - t0

    cf_hits, cf_ndcgs, latency = [], [], []
    for user, gt in truth.items():
        start = time.perf_counter()
        recs = cf.recommend(user, 5)
        latency.append(time.perf_counter() - start)
        cf_hits.append(hr_at_k(recs, gt))
        cf_ndcgs.append(ndcg_at_k(recs, gt))

    results.append({
        "model": "ItemItemCF",
        "hr@5": np.mean(cf_hits),
        "ndcg@5": np.mean(cf_ndcgs),
        "train_time_sec": cf_train_time,
        "infer_latency_ms": np.mean(latency) * 1000,
        "model_size": "small (dict-of-dicts)"
    })

    return pd.DataFrame(results)

# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    df = load_data()
    train_df, test_df = create_train_test_split(df)
    comparison = evaluate_models(train_df, test_df)
    print("\nMODEL COMPARISON RESULTS (Top-5 Ranking):\n")
    print(comparison.to_string(index=False))
