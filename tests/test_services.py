import pytest

from app.providers import MockProvider
from app.registry import create_default_registry
from app.schemas import ChatCompletionRequest
from app.servers import ChatService
from app.errors import StreamingNotSupportedError

@pytest.mark.anyio
async def test_chat_service_returns_chat_completion_response() -> None:
      registry = create_default_registry()
      providers = {
          "mock": MockProvider(),
      }
      service = ChatService(registry=registry, providers=providers)

      request = ChatCompletionRequest(
          model="gateway-mock",
          messages=[
              {
                  "role": "user",
                  "content": "Hello service",
              }
          ],
      )

      response = await service.chat_completion(request)

      assert response.object == "chat.completion"
      assert response.model == "gateway-mock"
      assert response.choices[0].message.role == "assistant"
      assert response.choices[0].message.content == "Echo: Hello service"


@pytest.mark.anyio
async def test_chat_service_rejects_streaming_requests() -> None:
      registry = create_default_registry()
      providers = {
          "mock": MockProvider(),
      }
      service = ChatService(registry=registry, providers=providers)

      request = ChatCompletionRequest(
          model="gateway-mock",
          messages=[
              {
                  "role": "user",
                  "content": "Hello service",
              }
          ],
          stream=True,
      )

      with pytest.raises(StreamingNotSupportedError):
          await service.chat_completion(request)