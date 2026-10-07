from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "health" in data

def test_fact_check_valid(mocker):
    # Mock the graph execution for tests
    mocker.patch("app.api.routes.fact_check_graph.ainvoke", return_value={"final_results": []})
    response = client.post("/api/fact-check", json={"text": "Drinking hot water cures viral infections."})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_fact_check_invalid_empty():
    response = client.post("/api/fact-check", json={"text": ""})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_INPUT"
