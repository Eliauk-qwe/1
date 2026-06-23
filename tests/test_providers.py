import pytest

from app.providers import MockProvider
from app.schemas import ChatCompletionRequest
from app.errors import ProviderError


@pytest.mark.anyio
async def test_mock_provider_echoes_latest_message() -> None:
    provider = MockProvider()
    request = ChatCompletionRequest(
        model="gateway-mock",
        messages=[
            {
                "role": "user",
                "content": "Hello gateway",
            }
        ],
    )

    content = await provider.chat_completion(request)

    assert content == "Echo: Hello gateway"

@pytest.mark.anyio
async def test_mock_provider_uses_latest_user_message() -> None:
      provider = MockProvider()
      request = ChatCompletionRequest(
          model="gateway-mock",
          messages=[
              {
                  "role": "user",
                  "content": "First user message",
              },
              {
                  "role": "assistant",
                  "content": "Previous answer",
              },
          ],
      )

      content = await provider.chat_completion(request)

      assert content == "Echo: First user message"

@pytest.mark.anyio
async def test_mock_provider_raises_provider_error() -> None:
      provider = MockProvider()
      request = ChatCompletionRequest(
          model="gateway-mock",
          messages=[
              {
                  "role": "user",
                  "content": "trigger_provider_error",
              }
          ],
      )

      with pytest.raises(ProviderError):
          await provider.chat_completion(request)