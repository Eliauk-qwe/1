from app.registry import ModelRegistry
from app.schemas import (
    ChatChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatResponseMessage,
)
from app.errors import ModelNotFoundError
from app.errors import ModelNotFoundError, StreamingNotSupportedError

# ChatService 里面拿着两张东西：

#   1. registry
#      负责回答：用户请求的模型叫什么？这个模型该交给哪个 provider？

#   2. providers
#      负责回答：这个 provider 名字对应哪个实际处理对象？

class ChatService:
    def __init__(self, registry: ModelRegistry, providers: dict):
        self.registry = registry
        self.providers = providers


    # 负责处理一次聊天请求
    async def chat_completion(self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        if request.stream:
            raise StreamingNotSupportedError()
            
        model = self.registry.get_model(request.model)
        if model is None:
            raise ModelNotFoundError(model=request.model)

        provider = self.providers[model.provider_name]
        content = await provider.chat_completion(request)

        return ChatCompletionResponse(
            id="chatcmpl-mock",
            model=model.public_model,
            choices=[
                ChatChoice(
                    message=ChatResponseMessage(content=content),
                )
            ],
        )