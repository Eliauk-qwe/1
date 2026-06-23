from app.schemas import ChatCompletionRequest
import pytest 
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_request_accepts_valid_payload() -> None:
    request = ChatCompletionRequest(
        model="gateway-mock",
        messages=[
            {
                "role": "user",
                "content": "Hello gateway",
            }
        ],
    )

    assert request.model == "gateway-mock"
    assert request.messages[0].role == "user"
    assert request.stream is False


def test_chat_request_rejects_empty_messages() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gateway-mock",
            messages=[],
        )

def test_chat_request_rejects_invalid_role() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gateway-mock",
            messages=[
                {
                    "role": "developer",
                    "content": "Hello",
                }
            ],
        )


def test_chat_request_rejects_invalid_temperature() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gateway-mock",
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            temperature=3.0,
        )

def test_chat_request_rejects_invalid_max_tokens() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gateway-mock",
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            max_tokens=0,
        )

def test_chat_completions_returns_mock_response() -> None:
      response = client.post(
          "/v1/chat/completions",
          json={
              "model": "gateway-mock",
              "messages": [
                  {
                      "role": "user",
                      "content": "Hello HTTP",
                  }
              ],
          },
      )

      body = response.json()

      assert response.status_code == 200
      assert body["object"] == "chat.completion"
      assert body["model"] == "gateway-mock"
      assert body["choices"][0]["message"]["role"] == "assistant"
      assert body["choices"][0]["message"]["content"] == "Echo: Hello HTTP"


def test_chat_completions_returns_404_for_unknown_model() -> None:
      response = client.post(
          "/v1/chat/completions",
          json={
              "model": "unknown-model",
              "messages": [
                  {
                      "role": "user",
                      "content": "Hello HTTP",
                  }
              ],
          },
      )

      body = response.json()

      assert response.status_code == 404
      assert body["error"]["code"] == "model_not_found"
      assert body["error"]["param"] == "model"


def test_chat_completions_rejects_streaming_requests() -> None:
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "gateway-mock",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello HTTP",
                    }
                ],
                "stream": True,
            },
        )

        body = response.json()

        assert response.status_code == 400
        assert body["error"]["code"] == "streaming_not_supported"
        assert body["error"]["param"] == "stream"



def test_chat_completions_returns_502_for_provider_error() -> None:
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "gateway-mock",
                "messages": [
                    {
                        "role": "user",
                        "content": "trigger_provider_error",
                    }
                ],
            },
        )

        body = response.json()

        assert response.status_code == 502
        assert body["error"]["code"] == "provider_error"
        assert body["error"]["type"] == "provider_error"