from fastapi.testclient import TestClient
from recommender_api import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
