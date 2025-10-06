from fastapi.testclient import TestClient
from service.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_trending_products_default():
    response = client.get("/trending_products")
    data = response.json()
    assert response.status_code == 200
    assert len(data["products"]) == 10

def test_trending_products_custom_k():
    response = client.get("/trending_products?k=5")
    data = response.json()
    assert response.status_code == 200
    assert len(data["products"]) == 5

def test_invalid_k_value():
    response = client.get("/trending_products?k=0")
    assert response.status_code == 400

def test_feedback():
    response = client.post("/feedback", params={"product_id": "P1", "feedback": "Great product!"})
    assert response.status_code == 200
    assert response.json()["product_id"] == "P1"
