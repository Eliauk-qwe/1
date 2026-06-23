from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_models_returns_gateway_mock() -> None:
    response = client.get("/v1/models")

    body = response.json()

    assert response.status_code == 200
    assert body["object"] == "list"
    assert body["data"][0]["id"] == "gateway-mock"