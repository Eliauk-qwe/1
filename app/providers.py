from app.schemas import ChatCompletionRequest
from app.errors import ProviderError

# ChatCompletionRequest 应该表示用户发来的聊天请求
class MockProvider:
    async def chat_completion(self, request: ChatCompletionRequest) -> str:
        
        latest_message = request.messages[-1]

        for message in reversed(request.messages):
            if message.role == "user":
                latest_message = message
                break
        if latest_message.content == "trigger_provider_error":
              raise ProviderError()

        return f"Echo: {latest_message.content}"