#FastAPI backend serving trending product data and health checks.

from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import random

app = FastAPI(
    title="Product Trend Tracker API",
    description="Tracks trending products based on simulated events.",
    version="0.1.0"
)

# In-memory mock data for trending products
mock_trends = [
    {"product_id": f"P{i}", "score": random.randint(50, 500)} for i in range(1, 21)
]

@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/trending_products")
def get_trending_products(k: int = 10):
    """Return top-k trending products."""
    if k <= 0:
        raise HTTPException(status_code=400, detail="k must be > 0")
    top_products = sorted(mock_trends, key=lambda x: x["score"], reverse=True)[:k]
    return {"top_k": k, "products": top_products}

@app.get("/metrics")
def get_metrics():
    """Return dummy Prometheus-style metrics."""
    metrics = {
        "api_latency_ms_p95": 120,
        "uptime_seconds": 123456,
        "requests_total": 890
    }
    return metrics

@app.post("/feedback")
def post_feedback(product_id: str, feedback: str):
    """Accept user feedback for a product."""
    if not product_id or not feedback:
        raise HTTPException(status_code=400, detail="Invalid feedback data")
    return {"message": "Feedback received", "product_id": product_id, "feedback": feedback}
