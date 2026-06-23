from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.errors import (
      ModelNotFoundError,
      ProviderError,
      StreamingNotSupportedError,
  )
from app.providers import MockProvider
from app.registry import create_default_registry
from app.schemas import (
      ChatCompletionRequest,
      ChatCompletionResponse,
      GatewayErrorDetail,
      GatewayErrorResponse,
      ModelInfo,
      ModelListResponse,
  )
from app.servers import ChatService


app = FastAPI()
registry = create_default_registry()
providers = {
      "mock": MockProvider(),
  }
chat_service = ChatService(registry=registry, providers=providers)


# async def health() -> dict[str,str] :
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/models", response_model=ModelListResponse)
def list_models():
    model_items = []

    for model in registry.list_models():
        model_items.append(ModelInfo(id=model.public_model))

    return ModelListResponse(data=model_items)

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
      request: ChatCompletionRequest,
  ) -> ChatCompletionResponse:
      return await chat_service.chat_completion(request)


@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(
      _request: Request,
      exc: ModelNotFoundError,
  ) -> JSONResponse:
    error_response = GatewayErrorResponse(
        error=GatewayErrorDetail(
            message=str(exc),
            type="invalid_request_error",
            param="model",
            code="model_not_found",
        )
    )

    return JSONResponse(
        status_code=404,
        content=error_response.model_dump(),
    )


@app.exception_handler(StreamingNotSupportedError)
async def streaming_not_supported_handler(
      _request: Request,
      exc: StreamingNotSupportedError,
  ) -> JSONResponse:
      error_response = GatewayErrorResponse(
          error=GatewayErrorDetail(
              message=str(exc),
              type="invalid_request_error",
              param="stream",
              code="streaming_not_supported",
          )
      )

      return JSONResponse(
          status_code=400,
          content=error_response.model_dump(),
      )



@app.exception_handler(ProviderError)
async def provider_error_handler(
      _request: Request,
      exc: ProviderError,
  ) -> JSONResponse:
      error_response = GatewayErrorResponse(
          error=GatewayErrorDetail(
              message=str(exc),
              type="provider_error",
              param=None,
              code="provider_error",
          )
      )

      return JSONResponse(
          status_code=502,
          content=error_response.model_dump(),
      )


@app.exception_handler(Exception)
async def internal_error_handler(
      _request: Request,
      _exc: Exception,
  ) -> JSONResponse:
      error_response = GatewayErrorResponse(
          error=GatewayErrorDetail(
              message="Internal server error",
              type="internal_error",
              param=None,
              code="internal_error",
          )
      )

      return JSONResponse(
          status_code=500,
          content=error_response.model_dump(),
      )