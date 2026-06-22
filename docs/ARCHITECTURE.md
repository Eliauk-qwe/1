# System Architecture

## 1. Architecture Goal

This document defines the architecture of the LLM inference gateway and performance benchmarking platform.

The architecture should support gradual development from a single Mock Provider to multiple real inference providers without requiring the whole system to be rewritten.

The design prioritizes:

* Clear module responsibilities
* OpenAI API compatibility
* Asynchronous request handling
* Transparent streaming
* Provider extensibility
* Testability
* Observability
* Progressive implementation

The first version should remain simple. Components such as Redis, PostgreSQL, Prometheus, Grafana, and Kubernetes must not be introduced until a specification requires them.

## 2. System Context

The gateway is positioned between upstream applications and downstream inference providers.

```text
┌───────────────────────────────────────┐
│          Upstream Applications        │
│                                       │
│ OpenAI SDK / MaxKB / RAGFlow / Custom │
└───────────────────┬───────────────────┘
                    │
                    │ OpenAI-Compatible API
                    ▼
┌───────────────────────────────────────┐
│         LLM Inference Gateway         │
│                                       │
│ API / Routing / Resilience / Metrics  │
└───────────────────┬───────────────────┘
                    │
                    │ Provider Requests
                    ▼
┌───────────────────────────────────────┐
│        Downstream Model Services      │
│                                       │
│ Mock / vLLM / SGLang / Cloud Models   │
└───────────────────────────────────────┘
```

Upstream applications should not need to know:

* The real provider address
* The provider authentication method
* The actual deployed model name
* The provider failure state
* The routing policy
* The internal monitoring system

The gateway hides these details behind one unified API.

## 3. High-Level Components

The planned system contains the following logical components:

```text
Client
  │
  ▼
API Layer
  │
  ▼
Application Service
  │
  ▼
Model Router
  │
  ▼
Provider Adapter
  │
  ▼
Downstream Inference Service
```

Cross-cutting capabilities will be added around this request path:

```text
Authentication
Rate Limiting
Timeout
Retry
Circuit Breaker
Logging
Metrics
Tracing
```

These capabilities must not be mixed directly into provider-specific implementations unless they are truly provider-specific.

## 4. Layer Responsibilities

## 4.1 API Layer

The API layer is responsible for:

* Exposing HTTP endpoints
* Receiving client requests
* Validating external request structures
* Extracting headers and request metadata
* Calling the application service
* Returning OpenAI-compatible responses
* Converting known application errors into HTTP responses

Example endpoints include:

* `GET /health`
* `GET /v1/models`
* `POST /v1/chat/completions`

The API layer must not:

* Contain provider-specific URLs
* Directly decide retry strategies
* Directly implement model routing policies
* Access databases through raw queries
* Contain benchmark calculations
* Contain vLLM-specific branches

The API layer should remain thin.

## 4.2 Schema Layer

The schema layer defines external request and response structures.

It is responsible for:

* OpenAI-compatible request models
* OpenAI-compatible response models
* Validation of required fields
* Validation of field types
* Structured error response models

Examples include:

* `ChatMessage`
* `ChatCompletionRequest`
* `ChatCompletionResponse`
* `ModelListResponse`
* `GatewayErrorResponse`

External API schemas should be separated from internal domain models when their responsibilities become different.

The gateway should not depend permanently on downstream provider response formats.

## 4.3 Application Service Layer

The application service coordinates one complete use case.

For a chat completion request, it may:

1. Receive a validated request from the API layer.
2. Ask the router to resolve the requested model.
3. Obtain the selected provider.
4. Call the provider adapter.
5. Collect request statistics.
6. Return an internal result to the API layer.

This layer represents business flow rather than HTTP details.

It must not:

* Parse raw HTTP requests
* Know FastAPI response objects
* Hard-code provider configuration
* Implement provider-specific HTTP formats

## 4.4 Model Registry

The model registry stores the gateway's public model definitions.

A model registration may contain:

```text
Public model name
Provider name
Upstream model name
Enabled status
Optional routing metadata
```

Example:

```text
Public model: qwen-local
Provider: local-vllm
Upstream model: Qwen/Qwen3-8B
```

The client uses `qwen-local`, while the downstream provider receives `Qwen/Qwen3-8B`.

The first milestone may use an in-memory model registry.

Persistent database storage should only be added when required by a later specification.

## 4.5 Model Router

The router decides which provider should handle a request.

The first routing strategy is static routing:

```text
Public model name
        │
        ▼
Registered provider
```

Later routing strategies may include:

* Round-robin
* Weighted round-robin
* Least concurrency
* Lowest recent latency
* Provider health-aware routing
* Failure fallback
* Tenant-based routing

Routing policy and provider communication must remain separate.

The router selects a provider. The provider adapter performs the request.

## 4.6 Provider Adapter Layer

The provider adapter hides differences between model-serving systems.

A provider adapter is responsible for:

* Building the downstream request
* Mapping public model names to upstream model names
* Adding provider authentication
* Sending asynchronous HTTP requests
* Parsing provider responses
* Reading streaming responses
* Mapping provider errors into gateway errors
* Checking provider health

A conceptual provider interface may include:

```python
class ModelProvider:
    async def list_models(self):
        ...

    async def chat_completion(self, request):
        ...

    async def stream_chat_completion(self, request):
        ...

    async def health_check(self):
        ...
```

The first milestone uses a Mock Provider.

Later providers may include:

* OpenAI-compatible HTTP Provider
* vLLM Provider
* SGLang Provider
* Cloud Model Provider

Where possible, vLLM and SGLang should reuse a general OpenAI-compatible provider instead of duplicating large amounts of code.

## 4.7 Resilience Layer

The resilience layer will manage request reliability.

Planned capabilities include:

* Connection timeout
* Read timeout
* First-token timeout
* Overall request deadline
* Retry
* Provider fallback
* Circuit breaking
* Concurrency control

These capabilities should be added one at a time through separate specifications.

Streaming and non-streaming requests require different failure handling.

Before the first streamed chunk is sent, the gateway may still return a normal structured error.

After streaming has begun, the gateway cannot safely replace the HTTP response with a normal JSON error response.

## 4.8 Observability Layer

The observability layer records what happens during requests.

It includes:

* Structured logs
* Request identifiers
* Metrics
* Provider health information
* Inference timing information
* Error classification

Important request timestamps include:

```text
Request received time
Provider request start time
First output chunk time
Request completion time
```

These timestamps can be used to calculate:

* Gateway processing time
* Time to First Token
* End-to-end latency
* Time per Output Token
* Token throughput

Logs and metrics have different purposes:

```text
Logs:
Explain what happened to an individual request.

Metrics:
Show the overall health and performance of the system.
```

Sensitive information such as API keys and complete prompts must not be logged by default.

## 4.9 Benchmarking Module

The benchmarking module is logically separate from the online gateway request path.

It acts as a client of:

* The gateway
* A direct inference provider

Its responsibilities include:

* Loading test prompts
* Generating concurrent requests
* Controlling request rate
* Recording streaming event times
* Calculating latency and throughput
* Generating comparison reports

The benchmarking module should not be imported into the gateway API request path.

The intended comparison is:

```text
Benchmark Client
      ├──────────► Direct vLLM
      │
      └──────────► Gateway ─────────► vLLM
```

This allows measurement of gateway overhead.

## 5. Non-Streaming Request Flow

A non-streaming chat request should follow this path:

```text
1. Client sends POST /v1/chat/completions.
2. API layer receives the HTTP request.
3. Schema layer validates the request.
4. A request ID is created.
5. Application service receives the validated request.
6. Router resolves the public model name.
7. Model registry returns the provider mapping.
8. Provider adapter receives the internal request.
9. Provider adapter calls the downstream service.
10. Provider adapter converts the downstream response.
11. Application service records request results.
12. API layer returns an OpenAI-compatible JSON response.
```

Diagram:

```text
Client
  │
  ▼
FastAPI Route
  │
  ▼
Request Validation
  │
  ▼
Chat Service
  │
  ▼
Model Router
  │
  ▼
Provider Adapter
  │
  ▼
Downstream Provider
  │
  ▼
OpenAI-Compatible Response
```

## 6. Streaming Request Flow

Streaming will be implemented in a later specification.

The intended flow is:

```text
1. Client sends stream=true.
2. Gateway opens a streaming request to the provider.
3. Provider sends the first SSE chunk.
4. Gateway immediately forwards that chunk.
5. Later chunks are forwarded without full-response buffering.
6. Client cancellation closes the upstream connection.
7. Provider and HTTP resources are released.
```

Correct behavior:

```text
Provider chunk arrives
        │
        ▼
Gateway forwards immediately
        │
        ▼
Client receives incrementally
```

Incorrect behavior:

```text
Gateway collects all chunks
        │
        ▼
Gateway waits for completion
        │
        ▼
Gateway returns everything together
```

The gateway must remain transparent and should add as little buffering as possible.

## 7. Error Flow

Errors should be classified rather than returned as raw Python exceptions.

Planned error categories include:

* Validation error
* Model not found
* Provider not found
* Provider authentication failure
* Provider rate limit
* Provider timeout
* Provider unavailable
* Invalid provider response
* Internal gateway error

A normal error flow is:

```text
Provider error
      │
      ▼
Provider-specific parsing
      │
      ▼
Gateway domain error
      │
      ▼
OpenAI-compatible HTTP error response
```

Internal stack traces must never be exposed to clients.

The request ID should be included in logs and, where appropriate, in error responses.

## 8. Configuration Architecture

Configuration should be separated from source code.

Planned configuration values include:

* Gateway host and port
* Provider base URLs
* Provider API keys
* Timeout values
* Model mappings
* Logging level
* Feature flags

Secrets must be read from environment variables or secret-management systems.

A later configuration may look like:

```yaml
providers:
  local-vllm:
    type: openai_compatible
    base_url: http://localhost:8001/v1
    api_key: ${VLLM_API_KEY}

models:
  qwen-local:
    provider: local-vllm
    upstream_model: Qwen/Qwen3-8B
```

The first milestone should use the smallest configuration necessary for a Mock Provider.

## 9. Dependency Direction

Dependencies should point inward toward stable interfaces.

Preferred direction:

```text
API Layer
    │
    ▼
Application Service
    │
    ▼
Domain Interfaces
    ▲
    │
Provider Implementations
```

The application service should depend on a provider interface, not directly on a concrete vLLM class.

This allows:

* Mock providers in tests
* New providers without changing API routes
* Provider replacement
* Easier unit testing

## 10. Initial Package Structure

The first milestone should use a small structure:

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
├── test_health.py
├── test_models.py
└── test_chat.py
```

This structure is intentionally small.

It should not be expanded into many directories before the code actually requires clearer separation.

After the project grows, it may evolve into:

```text
app/
├── api/
├── schemas/
├── services/
├── providers/
├── routing/
├── resilience/
├── observability/
├── storage/
└── core/
```

Architecture should guide code organization, but unnecessary directory complexity should be avoided.

## 11. First Milestone Architecture

The first milestone contains only:

```text
OpenAI SDK
     │
     ▼
FastAPI API
     │
     ▼
Chat Service
     │
     ▼
In-Memory Registry
     │
     ▼
Mock Provider
```

Included:

* Health endpoint
* Model listing endpoint
* Non-streaming chat completions
* One Mock Provider
* One registered mock model
* OpenAI-compatible JSON responses
* Structured errors
* Automated tests

Excluded:

* SSE streaming
* Real HTTP providers
* Redis
* PostgreSQL
* Authentication
* Rate limiting
* Retry
* Circuit breaker
* Metrics backend
* Dashboard

## 12. Architecture Evolution

The system should evolve in the following order:

```text
Mock Provider
      │
      ▼
Non-Streaming Gateway
      │
      ▼
Streaming SSE
      │
      ▼
OpenAI-Compatible HTTP Provider
      │
      ▼
Multiple Providers and Static Routing
      │
      ▼
Timeout and Retry
      │
      ▼
Rate Limiting and Circuit Breaking
      │
      ▼
Logs and Metrics
      │
      ▼
Benchmarking Platform
      │
      ▼
MaxKB and RAGFlow Integration
      │
      ▼
Performance-Aware Routing
```

Each step should have its own specification and tests.

## 13. Architecture Rules

The following rules must remain true:

1. FastAPI routes remain thin.
2. Provider-specific behavior stays inside provider adapters.
3. Routing policy is separate from provider communication.
4. Benchmark code does not enter the online request path.
5. Secrets and provider URLs are not hard-coded.
6. External errors are converted into gateway errors.
7. New infrastructure is introduced only when required.
8. Streaming responses are forwarded incrementally.
9. Every important request can be identified by a request ID.
10. Performance claims must be supported by measurements.
