from pydantic import BaseModel, Field
from typing import Literal

# 在定义 /v1/models 接口返回给用户的 JSON 格式。
class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "gateway"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]
#   {
#     "object": "list",
#     "data": [
#       {
#         "id": "gateway-mock",
#         "object": "model",
#         "created": 0,
#         "owned_by": "gateway"
#       }
#     ]
#   }

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = Field(min_length=1)
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    stream: bool = False


class ChatResponseMessage(BaseModel):
    role: str = "assistant"
    content: str

class ChatChoice(BaseModel):
    index: int = 0
    message: ChatResponseMessage
    finish_reason: str = "stop"

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = 0
    model: str
    choices: list[ChatChoice]
    usage: UsageInfo = Field(default_factory=UsageInfo)


#   {
#     "error": {
#       "message": "...",
#       "type": "...",
#       "param": "model",
#       "code": "model_not_found"
#     }
#   }

class GatewayErrorDetail(BaseModel):
      message: str
      type: str
      param: str | None = None
      code: str


class GatewayErrorResponse(BaseModel):
      error: GatewayErrorDetail