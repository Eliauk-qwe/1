from fastapi.testclient import TestClient

from app.main import app


def test_unexpected_error_returns_internal_error_response() -> None:
      @app.get("/__test__/unexpected-error")
      def unexpected_error() -> None:
          raise RuntimeError("secret internal detail")

      client = TestClient(app, raise_server_exceptions=False)

      response = client.get("/__test__/unexpected-error")

      body = response.json()

      assert response.status_code == 500
      assert body["error"]["code"] == "internal_error"
      assert body["error"]["type"] == "internal_error"
      assert "secret internal detail" not in body["error"]["message"]