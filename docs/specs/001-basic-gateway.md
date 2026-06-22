# Specification 001: Basic Non-Streaming Gateway

## 1. Status

```text
Status: Draft
Milestone: 1
Implementation: Not started
```

This specification defines the first runnable version of the LLM inference gateway.

The implementation must remain limited to the scope of this document.

## 2. Goal

Implement the first complete request path:

```text
OpenAI Python SDK
        |
        v
FastAPI Gateway
        |
        v
Application Service
        |
        v
In-Memory Model Registry
        |
        v
Mock Provider
        |
        v
OpenAI-Compatible JSON Response
```

The purpose of this milestone is to verify:

* The FastAPI application can start.
* OpenAI-compatible requests can be validated.
* A model can be resolved through an in-memory registry.
* A provider can generate a response.
* The response follows the expected OpenAI structure.
* Errors are returned in a consistent structure.
* The behavior can be tested without a real GPU or model server.

## 3. In Scope

This milestone must implement:

* `GET /health`
* `GET /v1/models`
* `POST /v1/chat/completions`
* Non-streaming chat completions only
* One in-memory model registry
* One Mock Provider
* One public mock model
* OpenAI-compatible response structures
* Structured gateway errors
* Unit tests
* API integration tests
* Basic local startup instructions

## 4. Out of Scope

This milestone must not implement:

* `stream=true`
* Server-Sent Events
* vLLM integration
* SGLang integration
* Cloud model integration
* External HTTP provider calls
* Authentication
* API Key validation
* Redis
* PostgreSQL
* Database migrations
* Rate limiting
* Token rate limiting
* Concurrency limiting
* Timeout policies
* Retry
* Fallback
* Circuit breaking
* Prometheus
* Grafana
* OpenTelemetry
* Benchmark execution
* Frontend interfaces
* Docker Compose
* Kubernetes

Do not add placeholder implementations for these features.

## 5. Technical Requirements

Use:

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* pytest
* FastAPI `TestClient` or an equivalent supported test client

The application code must use type annotations for public functions and important interfaces.

No real secret or API Key is required in this milestone.

## 6. Initial Package Structure

The implementation should begin with this small structure:

```text
app/
├── __init__.py
├── main.py
├── schemas.py
├── services.py
├── providers.py
├── registry.py
└── errors.py

tests/
├── __init__.py
├── test_health.py
├── test_models.py
└── test_chat.py
```

The implementation may add a small number of files when clearly justified.

Do not create the final large directory structure early.

## 7. Model Definition

The gateway must expose one public model:

```text
Public model name: gateway-mock
Provider name: mock
Upstream model name: gateway-mock
```

The model must be stored in an in-memory registry.

The model registry must be separate from the FastAPI route implementation.

## 8. Mock Provider Behavior

The Mock Provider must not call any external service.

It receives a validated chat request and returns a deterministic response.

Recommended response behavior:

```text
Mock response: Echo: <latest user message>
```

Example input:

```json
{
  "model": "gateway-mock",
  "messages": [
    {
      "role": "user",
      "content": "Hello gateway"
    }
  ]
}
```

Example assistant content:

```text
Echo: Hello gateway
```

The exact wording may remain deterministic and simple.

The Mock Provider must also support an intentional failure path for testing.

The failure mechanism must be explicit and documented. For example, a specific latest user message such as:

```text
trigger_provider_error
```

may cause the Mock Provider to raise a gateway provider error.

Do not use random failures.

## 9. Endpoint: Health Check

### Request

```http
GET /health
```

### Successful Response

Status code:

```text
200 OK
```

Response body:

```json
{
  "status": "ok"
}
```

### Requirements

* The endpoint must not call the provider.
* The endpoint must not require authentication.
* The endpoint must remain fast and deterministic.

## 10. Endpoint: List Models

### Request

```http
GET /v1/models
```

### Successful Response

Status code:

```text
200 OK
```

Example response:

```json
{
  "object": "list",
  "data": [
    {
      "id": "gateway-mock",
      "object": "model",
      "created": 0,
      "owned_by": "gateway"
    }
  ]
}
```

### Requirements

* The endpoint must read models from the registry.
* The model list must not be hard-coded directly inside the route function.
* The response must contain the `gateway-mock` model.
* The `created` value may be a fixed integer for this milestone.

## 11. Endpoint: Chat Completions

### Request

```http
POST /v1/chat/completions
Content-Type: application/json
```

### Minimum Supported Request Fields

```json
{
  "model": "gateway-mock",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ]
}
```

The request schema must support:

* `model`
* `messages`
* `temperature`
* `max_tokens`
* `stream`

### Field Requirements

#### `model`

* Required
* Must be a non-empty string
* Must match a registered model

#### `messages`

* Required
* Must contain at least one message
* Each message must contain:

  * `role`
  * `content`

Initially supported roles:

* `system`
* `user`
* `assistant`

#### `temperature`

* Optional
* Default may be `1.0`
* Must use a reasonable validation range

Recommended range:

```text
0.0 to 2.0
```

#### `max_tokens`

* Optional
* When present, it must be a positive integer

#### `stream`

* Optional
* Default must be `false`
* When `true`, the gateway must reject the request because streaming belongs to the next specification

## 12. Successful Chat Response

Status code:

```text
200 OK
```

Example response:

```json
{
  "id": "chatcmpl-example",
  "object": "chat.completion",
  "created": 0,
  "model": "gateway-mock",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Echo: Hello"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### Requirements

* `id` must be a non-empty string.
* `object` must be `chat.completion`.
* `model` must match the public model requested by the client.
* `choices` must contain one assistant response.
* `finish_reason` must be `stop`.
* Token counts may be zero in this milestone.
* The response must not expose internal provider objects.

## 13. Request Processing Flow

The implementation must follow this logical flow:

```text
1. FastAPI receives the HTTP request.
2. Pydantic validates the external request.
3. The route calls the chat application service.
4. The service asks the registry to resolve the requested model.
5. The registry returns the model registration.
6. The service obtains the Mock Provider.
7. The Mock Provider generates a deterministic response.
8. The service creates the gateway response.
9. The API returns an OpenAI-compatible JSON response.
```

The FastAPI route must remain thin.

It must not contain:

* Mock response generation
* Model registry data
* Provider-selection branches
* Provider-error simulation logic

## 14. Error Response Format

All gateway-controlled errors should use a consistent structure.

Recommended format:

```json
{
  "error": {
    "message": "Readable error message",
    "type": "gateway_error_type",
    "param": null,
    "code": "machine_readable_code"
  }
}
```

Internal stack traces must not be included in responses.

## 15. Required Error Cases

## 15.1 Invalid Request

Examples:

* Missing `model`
* Empty `messages`
* Invalid role
* Invalid `temperature`
* Non-positive `max_tokens`

Expected status:

```text
422 Unprocessable Entity
```

FastAPI validation may be used, but the response behavior must be documented in the implementation summary.

## 15.2 Model Not Found

Example request:

```json
{
  "model": "unknown-model",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ]
}
```

Expected status:

```text
404 Not Found
```

Expected error code:

```text
model_not_found
```

## 15.3 Streaming Not Supported

Example request:

```json
{
  "model": "gateway-mock",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "stream": true
}
```

Expected status:

```text
400 Bad Request
```

Expected error code:

```text
streaming_not_supported
```

## 15.4 Provider Failure

When the documented Mock Provider failure condition is triggered:

Expected status:

```text
502 Bad Gateway
```

Expected error code:

```text
provider_error
```

The raw internal exception must not be exposed.

## 15.5 Unexpected Internal Error

Unexpected errors must return:

```text
500 Internal Server Error
```

Expected error code:

```text
internal_error
```

The response must not include a stack trace.

The full exception may be logged locally, but sensitive request contents should not be logged by default.

## 16. Application Startup

The project must provide a clear startup command.

Recommended command:

```bash
uvicorn app.main:app --reload
```

After startup, the following request must succeed:

```bash
curl http://127.0.0.1:8000/health
```

Expected result:

```json
{
  "status": "ok"
}
```

## 17. OpenAI SDK Compatibility Check

The implementation must be compatible with a basic OpenAI Python SDK call.

Example:

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

Expected content:

```text
Echo: Hello gateway
```

The gateway does not need to validate the API Key in this milestone.

The SDK requires a value, but the gateway may ignore it for now.

## 18. Testing Requirements

## 18.1 Health Tests

Test:

* `/health` returns status code 200.
* Response body equals `{"status": "ok"}`.

## 18.2 Model Tests

Test:

* `/v1/models` returns status code 200.
* Response object is `list`.
* The response contains `gateway-mock`.

## 18.3 Successful Chat Tests

Test:

* A valid request returns status code 200.
* The response object is `chat.completion`.
* The assistant role is returned.
* The assistant content contains the deterministic Mock Provider response.
* The public model name is returned.

## 18.4 Validation Tests

Test at least:

* Missing model
* Empty messages
* Invalid role
* Invalid temperature
* Invalid max tokens

## 18.5 Model Error Test

Test:

* An unknown model returns status code 404.
* Error code equals `model_not_found`.

## 18.6 Streaming Rejection Test

Test:

* `stream=true` returns status code 400.
* Error code equals `streaming_not_supported`.

## 18.7 Provider Failure Test

Test:

* The documented Mock Provider failure condition returns status code 502.
* Error code equals `provider_error`.
* Internal exception details are not exposed.

## 19. Documentation Requirements

The root `README.md` must include:

* Project name
* Current milestone
* Python version
* Environment setup
* Dependency installation
* Application startup command
* Test command
* Health-check example
* Chat-completion example
* Current limitations

Do not describe unimplemented features as already available.

## 20. Definition of Done

This specification is complete only when:

* The required files are implemented.
* The FastAPI application starts.
* `/health` works.
* `/v1/models` returns `gateway-mock`.
* Non-streaming `/v1/chat/completions` works.
* The Mock Provider response is deterministic.
* Unknown models return a structured 404 error.
* `stream=true` is rejected clearly.
* Provider failures return a structured 502 error.
* The OpenAI Python SDK compatibility check succeeds.
* Automated tests pass.
* The actual test commands and results are reported.
* The README reflects only implemented behavior.
* No out-of-scope feature has been added.

## 21. Known Limitations

This milestone intentionally has the following limitations:

* Only one mock model is available.
* No real inference engine is connected.
* Streaming is unsupported.
* Token counts are placeholders.
* Authentication is not enforced.
* Registry data is lost when the application stops.
* No traffic governance is implemented.
* No production monitoring is implemented.
* No performance benchmarking is implemented.

These limitations are expected and must not be treated as defects in this milestone.
