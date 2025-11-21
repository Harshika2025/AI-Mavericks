from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from typing import List

# Assuming you have these classes implemented
class PopularityRecommender:
    def fit(self, df):
        pass  # Implement fitting logic

    def recommend(self, user_id: str) -> List[str]:
        return ["product1", "product2", "product3"]  # Example recommendation

class ItemItemCF:
    def fit(self, df):
        pass  # Implement fitting logic

    def recommend(self, user_id: str) -> List[str]:
        return ["product4", "product5", "product6"]  # Example recommendation

# FastAPI app
app = FastAPI(title="Product Trend Tracker Recommender")

# -----------------------------
# Prometheus instrumentation
# -----------------------------
Instrumentator().instrument(app).expose(app)

REQUEST_COUNT = Counter(
    "api_request_count",
    "Total number of API requests",
    ["endpoint", "method", "status"]
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Latency of API responses",
    ["endpoint"]
)

# ============================
# REQUIRED ENDPOINTS FOR TESTS
# ============================

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/trending_products")
def trending_products(k: int = 10):
    if k <= 0:
        raise HTTPException(status_code=400, detail="k must be > 0")

    products = [f"product{i}" for i in range(1, k + 1)]
    return {"products": products}


@app.post("/feedback")
def feedback(product_id: str, feedback: str):
    return {
        "product_id": product_id,
        "feedback": feedback,
        "status": "received"
    }

# This function loads the latest snapshot of data (for simplicity, we return an empty DataFrame here)
def load_latest_snapshot():
    # Replace with your actual data loading logic
    return []

@app.on_event("startup")
def startup_event():
    global pop_model, cf_model

    # Load data
    df = load_latest_snapshot()

    # Initialize models
    pop_model = PopularityRecommender()
    pop_model.fit(df)

    cf_model = ItemItemCF()
    cf_model.fit(df)

@app.get("/health")
def health():
    return {"status": "healthy", "message": "API is running"}

@app.get("/models")
def models():
    return {"models": ["Popularity", "Item-Item CF", "Neural MF"]}

@app.get("/recommend")
def recommend(user_id: str, model: str = "pop"):
    # measure latency for this endpoint
    with REQUEST_LATENCY.labels("/recommend").time():
        try:
            if model == "cf":
                recs = cf_model.recommend(user_id)
            else:
                recs = pop_model.recommend(user_id)

            # count successful request
            REQUEST_COUNT.labels("/recommend", "GET", "200").inc()

            return {
                "user_id": user_id,
                "model": model,
                "recommendations": recs
            }

        except Exception:
            # count failure
            REQUEST_COUNT.labels("/recommend", "GET", "500").inc()
            raise


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
