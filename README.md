# LLM Inference Gateway

当前里程碑：`001-basic-gateway`，基础非流式网关。

这个项目当前实现的是一个最小可运行的 OpenAI-compatible LLM gateway。上游客户端不直接调用真实大模型服务，而是先调用这个 gateway。gateway 负责校验请求、解析用户请求的公开模型名、调用确定性的 `MockProvider`，最后返回 OpenAI 风格的 JSON 响应。

当前请求链路：

```text
Client / OpenAI SDK
    -> FastAPI API layer
    -> ChatService
    -> ModelRegistry
    -> MockProvider
    -> OpenAI-compatible JSON response
```

这个里程碑只使用一个 mock model，不连接 vLLM、SGLang、Redis、数据库，也不实现认证、限流、重试、dashboard 或 streaming。

## 环境要求

- Python 3.12
- FastAPI
- Pydantic
- Uvicorn
- pytest
- OpenAI Python SDK

## 环境准备

创建并激活虚拟环境：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

安装项目和开发依赖：

```bash
pip install -e ".[dev]"
```

## 启动网关

```bash
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

期望响应：

```json
{
  "status": "ok"
}
```

## 当前支持的接口

### `GET /health`

返回一个简单、固定的健康检查响应。

这个接口不调用 registry，也不调用 provider。它只证明 FastAPI 应用可以启动并响应请求。

### `GET /v1/models`

返回当前注册的公开模型列表。

```bash
curl http://127.0.0.1:8000/v1/models
```

当前只有一个模型：

```text
gateway-mock
```

### `POST /v1/chat/completions`

执行一次非流式 mock 聊天补全。

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gateway-mock",
    "messages": [
      {
        "role": "user",
        "content": "Hello gateway"
      }
    ]
  }'
```

期望 assistant 内容：

```text
Echo: Hello gateway
```

`MockProvider` 会优先使用最后一条 `role=user` 的消息。如果没有 user 消息，就使用最后一条消息。

## OpenAI Python SDK 示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="unused-test-key",
)

response = client.chat.completions.create(
    model="gateway-mock",
    messages=[
        {
            "role": "user",
            "content": "Hello gateway",
        }
    ],
)

print(response.choices[0].message.content)
```

期望输出：

```text
Echo: Hello gateway
```

OpenAI SDK 要求必须传一个 `api_key`，但当前里程碑不校验这个 key。

## 错误响应结构

gateway 可控错误统一使用下面的结构：

```json
{
  "error": {
    "message": "Readable error message",
    "type": "error_type",
    "param": null,
    "code": "machine_readable_code"
  }
}
```

当前已实现的错误路径：

| 场景 | HTTP 状态码 | 错误码 |
| --- | ---: | --- |
| 请求未知模型 | `404` | `model_not_found` |
| 请求 `stream=true` | `400` | `streaming_not_supported` |
| Mock provider 故意失败 | `502` | `provider_error` |
| 未预期内部异常 | `500` | `internal_error` |

Mock provider 的失败路径通过下面这条最新 user 消息触发：

```text
trigger_provider_error
```

这样做是为了让 provider 失败路径可重复、可测试，而不是依赖随机失败。

## 当前架构

当前代码规模很小，但每个文件都有明确职责。

```text
app/main.py
  API 层。
  定义 FastAPI routes，并把已知异常转换成 HTTP 响应。

app/schemas.py
  Schema 层。
  定义外部请求结构、成功响应结构和错误响应结构。

app/servers.py
  Application Service 层。
  负责协调一次 chat completion 的业务流程。

app/registry.py
  Model Registry 层。
  保存公开模型定义，并根据模型名查询模型注册信息。

app/providers.py
  Provider 层。
  当前只实现确定性的 MockProvider。

app/errors.py
  Domain Error 层。
  定义 gateway 自己可控的异常类型。
```

主要依赖方向：

```text
main.py
  -> schemas.py
  -> servers.py
      -> registry.py
      -> providers.py
      -> errors.py
```

这里的核心思想是：不同层只做自己该做的事。

`main.py` 可以知道 HTTP 状态码，因为它是 API 层。`ChatService` 不应该返回 `JSONResponse`，因为它是业务流程代码，不应该依赖 HTTP 细节。`MockProvider` 不应该返回 HTTP 502，因为 provider 层只知道“provider 失败了”，不应该决定 HTTP 如何表达这个失败。

## 我们是如何一步一步构建的

这个项目是按小步骤逐层搭起来的。

1. 定义模型列表响应 schema。

   `ModelInfo` 表示一个公开模型。

   `ModelListResponse` 表示 `/v1/models` 返回的模型列表响应。

2. 构建内存模型注册表。

   `ModelRegistration` 表示一条模型映射：

   ```text
   public_model -> provider_name -> upstream_model
   ```

   `ModelRegistry` 内部把模型列表转换成字典，这样可以通过公开模型名快速查询模型。

3. 添加默认 mock 模型。

   `create_default_registry()` 注册：

   ```text
   public_model: gateway-mock
   provider_name: mock
   upstream_model: gateway-mock
   ```

4. 添加 `GET /health`。

   这是最小健康检查接口，用来证明 FastAPI app 能启动并响应。

5. 添加 `GET /v1/models`。

   这个 route 从 `ModelRegistry` 读取模型，而不是在 route 里硬编码模型列表。

   这样做的原因是：API 层不应该保存模型注册数据，模型数据应该属于 registry 层。

6. 定义 chat 请求和响应 schema。

   `ChatCompletionRequest` 负责校验请求。

   `ChatCompletionResponse` 负责定义 OpenAI-compatible 响应结构。

   例如空 `messages`、非法 `role`、非法 `temperature`、非法 `max_tokens` 由 Pydantic/FastAPI 校验。

7. 构建 `MockProvider`。

   `MockProvider.chat_completion()` 返回：

   ```text
   Echo: <latest user message>
   ```

   这个方法使用 `async def`，是为了让 mock provider 和未来真实 HTTP provider 的调用方式一致。

8. 构建 `ChatService`。

   `ChatService` 接收两个依赖：

   ```text
   ModelRegistry
   providers mapping
   ```

   例如：

   ```python
   providers = {
       "mock": MockProvider(),
   }
   ```

   这叫依赖注入。`ChatService` 不自己创建 `MockProvider`，而是由外部把 provider 交给它。

   这样以后测试时可以替换 provider，未来接真实 provider 时也不用重写 route。

9. 接入 `POST /v1/chat/completions`。

   route 保持很薄：

   ```text
   接收 HTTP 请求
   -> 交给 Pydantic 校验
   -> 调用 ChatService
   -> 返回响应
   ```

   route 不负责查模型，不负责调用 provider，也不负责拼 mock 回复。

10. 添加 domain errors。

    当前有：

    ```text
    ModelNotFoundError
    StreamingNotSupportedError
    ProviderError
    ```

    这些错误表达“业务上发生了什么问题”，但它们本身不是 HTTP 响应。

11. 添加 API exception handlers。

    `main.py` 把 domain errors 转换成 HTTP 响应：

    ```text
    ModelNotFoundError -> 404 model_not_found
    StreamingNotSupportedError -> 400 streaming_not_supported
    ProviderError -> 502 provider_error
    Exception -> 500 internal_error
    ```

12. 分层添加测试。

    测试不是只测最终 HTTP 接口，而是分层验证：

    ```text
    schemas.py      请求校验
    providers.py    MockProvider 正常和失败行为
    servers.py      ChatService 业务流程
    main.py         HTTP routes 和错误响应
    OpenAI SDK      外部 SDK 兼容性
    ```

## 为什么这样架构

这个项目的核心架构思想是：职责分离。

API 层应该保持薄。它负责 HTTP path、请求解析、HTTP response 和 exception handler。它不应该包含 mock 回复生成逻辑、模型查询细节或 provider 分支判断。

Service 层负责一次完整用例。对于 chat completion，它的流程是：

```text
检查当前业务规则
-> 解析用户请求的模型
-> 找到对应 provider
-> 调用 provider
-> 构建响应对象
```

Registry 层负责模型查询。这样模型映射不会散落在多个 route 函数里。

Provider 层负责下游行为。当前只有 `MockProvider`，但以后可以新增真实 OpenAI-compatible HTTP provider，而不需要重写 API route。

Error 层给错误命名。`ModelNotFoundError` 比通用的 `ValueError` 更清楚，因为它表达了具体业务含义。API 层就可以根据具体错误类型返回稳定的 HTTP 状态码和错误码。

## 运行测试

运行完整测试：

```bash
pytest
```

当前测试覆盖：

- `/health`
- `/v1/models`
- chat request validation
- 正常 mock chat completion
- unknown model error
- streaming rejection
- provider failure
- internal error fallback
- OpenAI Python SDK compatibility

OpenAI SDK 兼容性测试会启动一个临时本地 `uvicorn` 服务，并用官方 `OpenAI` client 调用它。

## 当前限制

- 当前只有一个 mock model：`gateway-mock`。
- 当前没有连接真实推理引擎。
- 当前不支持 streaming，`stream=true` 会返回结构化错误。
- token 统计目前是占位值，全部为 `0`。
- API key 当前只是为了兼容 SDK 入参，不做校验。
- registry 当前只存在内存中，应用重启后会重新创建。
- 当前没有 authentication、authorization、rate limiting、retry、fallback、circuit breaking、monitoring backend、dashboard、Redis、database、Docker Compose、Kubernetes 或 benchmarking runner。

这些限制是 `001-basic-gateway` 这个里程碑的预期范围，不是缺陷。
