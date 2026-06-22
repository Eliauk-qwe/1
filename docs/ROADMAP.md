# Project Roadmap

## 1. Roadmap Purpose

This roadmap divides the LLM inference gateway and benchmarking platform into small, verifiable milestones.

Each milestone should produce a runnable and testable result.

Development must follow these rules:

* Implement one milestone at a time.
* Write or approve the related specification before coding.
* Do not implement features from later milestones early.
* Run relevant tests before marking a milestone complete.
* Commit completed milestones separately.
* Update this roadmap when the actual development order changes.

## 2. Current Status

Current project stage:

```text
Documentation and architecture preparation
```

Completed:

* Repository initialization
* `AGENTS.md`
* `docs/PROJECT.md`
* `docs/ARCHITECTURE.md`

Current target:

```text
Milestone 1: Basic Non-Streaming Gateway
```

Current specification:

```text
docs/specs/001-basic-gateway.md
```

---

## 3. Milestone 0: Repository Foundation

### Goal

Establish the project rules, scope, architecture, and development workflow before writing application code.

### Deliverables

* `AGENTS.md`
* `README.md`
* `docs/PROJECT.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/specs/`
* `docs/adr/`
* `.gitignore`
* `.env.example`

### Completion Criteria

* Project scope is clearly defined.
* Architecture boundaries are documented.
* The development order is documented.
* Codex can identify the current specification.
* No application functionality is implemented yet.

### Status

In progress.

---

## 4. Milestone 1: Basic Non-Streaming Gateway

### Goal

Build the first complete and testable request path:

```text
OpenAI SDK
    |
    v
FastAPI Gateway
    |
    v
Mock Provider
    |
    v
OpenAI-Compatible Response
```

### Scope

Implement:

* `GET /health`
* `GET /v1/models`
* `POST /v1/chat/completions`
* Non-streaming requests only
* One in-memory model registry
* One Mock Provider
* Structured gateway errors
* Unit and integration tests

### Out of Scope

Do not implement:

* SSE streaming
* Real vLLM or SGLang integration
* Authentication
* Redis
* Database storage
* Rate limiting
* Retry
* Circuit breaking
* Dashboard

### Completion Criteria

* The application starts successfully.
* `/health` returns a valid response.
* `/v1/models` returns the registered mock model.
* The OpenAI Python SDK can call `/v1/chat/completions`.
* Unsupported models return a structured error.
* Provider errors return a structured error.
* Tests pass.

### Specification

```text
docs/specs/001-basic-gateway.md
```

### Status

Not started.

---

## 5. Milestone 2: SSE Streaming

### Goal

Support OpenAI-compatible streaming chat completions.

### Scope

Implement:

* `stream=true`
* Server-Sent Events
* Incremental chunk delivery
* OpenAI-compatible streaming chunks
* Final `[DONE]` marker
* Client cancellation handling
* Resource cleanup
* Streaming tests

### Completion Criteria

* Chunks reach the client incrementally.
* The complete response is not buffered before returning.
* Client cancellation closes provider resources.
* Errors before the first chunk return structured HTTP errors.
* Streaming tests pass.

### Planned Specification

```text
docs/specs/002-streaming-sse.md
```

### Status

Not started.

---

## 6. Milestone 3: OpenAI-Compatible HTTP Provider

### Goal

Replace the Mock Provider with a reusable asynchronous HTTP provider.

### Scope

Implement:

* `httpx.AsyncClient`
* Configurable provider base URL
* Configurable API Key
* Configurable timeout
* Non-streaming upstream requests
* Streaming upstream requests
* Provider error mapping
* Provider health checks

### Initial Target

The first real downstream service should be:

```text
vLLM OpenAI-compatible server
```

### Completion Criteria

* The gateway successfully forwards requests to vLLM.
* Provider URLs and secrets are not hard-coded.
* Both streaming and non-streaming requests work.
* Provider errors are translated into gateway errors.
* Integration tests pass.

### Planned Specification

```text
docs/specs/003-openai-compatible-provider.md
```

### Status

Not started.

---

## 7. Milestone 4: Multiple Providers and Static Routing

### Goal

Allow one gateway instance to access multiple model providers.

### Scope

Implement:

* Provider registry
* Model registry
* Public model names
* Upstream model name mapping
* Static model-to-provider routing
* Provider enable and disable state
* Configuration validation

### Example

```text
qwen-local
    |
    v
local-vllm
    |
    v
Qwen/Qwen3-8B
```

### Completion Criteria

* Multiple providers can be configured.
* Multiple public models can be listed.
* Requests are sent to the correct provider.
* Unknown models return a structured error.
* Routing tests pass.

### Planned Specification

```text
docs/specs/004-static-routing.md
```

### Status

Not started.

---

## 8. Milestone 5: Timeout, Retry, and Fallback

### Goal

Improve gateway reliability when downstream providers fail.

### Scope

Implement gradually:

* Connection timeout
* Read timeout
* First-token timeout
* Retry policy
* Retryable error classification
* Provider fallback
* Basic circuit breaker

### Important Rule

A streaming request must not be retried after response chunks have already been sent to the client.

### Completion Criteria

* Retryable and non-retryable errors are distinguished.
* Requests can fall back to a backup provider.
* Failed providers can be temporarily removed from routing.
* Tests cover timeout and failure scenarios.

### Planned Specifications

```text
docs/specs/005-timeout-retry.md
docs/specs/006-fallback-circuit-breaker.md
```

### Status

Not started.

---

## 9. Milestone 6: Authentication and Traffic Control

### Goal

Control who can access the gateway and how much traffic each user may generate.

### Scope

Implement:

* Gateway API Keys
* API Key validation
* Requests per minute limits
* Tokens per minute limits
* Per-key concurrency limits
* Per-model concurrency limits
* Structured rate-limit errors

### Initial Storage

The first version may use in-memory storage.

Redis should only be introduced when distributed state is required.

### Completion Criteria

* Invalid API Keys are rejected.
* Request limits are enforced.
* Concurrency limits are enforced.
* Secrets are not exposed in logs.
* Traffic-control tests pass.

### Planned Specification

```text
docs/specs/007-auth-rate-limit.md
```

### Status

Not started.

---

## 10. Milestone 7: Logging and Metrics

### Goal

Make gateway behavior measurable and observable.

### Scope

Implement:

* Request ID
* Structured logs
* Request duration
* Provider duration
* Status and error classification
* Input and output token counts
* TTFT
* TPOT
* Current concurrency
* Request throughput
* Provider health metrics

### External Tools

Later integration may include:

* Prometheus
* Grafana
* OpenTelemetry

These tools should not be introduced before the internal metric model is clear.

### Completion Criteria

* Every request has a request ID.
* Logs do not expose secrets.
* Important latency metrics are recorded.
* Streaming timing is measured correctly.
* Metrics tests pass.

### Planned Specification

```text
docs/specs/008-observability.md
```

### Status

Not started.

---

## 11. Milestone 8: Performance Benchmarking Tool

### Goal

Build a benchmarking client for inference workloads.

### Scope

Implement:

* JSONL prompt datasets
* Configurable concurrency
* Configurable request count
* Configurable request rate
* Streaming and non-streaming workloads
* TTFT measurement
* TPOT measurement
* End-to-end latency
* Requests per second
* Tokens per second
* P50, P95, and P99 percentiles
* Error statistics
* JSON and Markdown reports

### Comparison Scenarios

The benchmark should support:

```text
Direct vLLM
versus
Gateway → vLLM
```

It should also compare:

* Different concurrency levels
* Different prompt lengths
* Different models
* Different providers
* Streaming and non-streaming requests

### Completion Criteria

* Benchmark results are reproducible.
* Failed requests are reported honestly.
* Percentile calculations are tested.
* Gateway overhead can be measured.

### Planned Specification

```text
docs/specs/009-benchmark-runner.md
```

### Status

Not started.

---

## 12. Milestone 9: MaxKB and RAGFlow Integration

### Goal

Verify that the gateway can serve real upstream AI applications.

### Scope

Implement and document:

* MaxKB gateway configuration
* RAGFlow gateway configuration
* OpenAI-compatible model connection
* Streaming compatibility verification
* Long-context request testing
* Error and timeout behavior
* Integration examples

### Completion Criteria

* MaxKB can call a downstream model through the gateway.
* RAGFlow can call a downstream model through the gateway.
* Gateway metrics distinguish upstream applications where possible.
* Long-context behavior is benchmarked.
* Integration instructions are documented.

### Planned Specification

```text
docs/specs/010-maxkb-ragflow-integration.md
```

### Status

Not started.

---

## 13. Milestone 10: Performance-Aware Routing

### Goal

Use runtime measurements to improve provider selection.

### Possible Strategies

* Round-robin
* Weighted round-robin
* Least active requests
* Lowest recent TTFT
* Lowest recent failure rate
* Health-aware routing
* Cost-aware routing

### Completion Criteria

* Routing strategies implement a common interface.
* Strategy decisions are observable.
* Routing performance can be benchmarked.
* A simple static strategy remains available.
* Dynamic routing does not hide failures.

### Planned Specification

```text
docs/specs/011-performance-aware-routing.md
```

### Status

Not started.

---

## 14. Optional Future Work

The following features may be considered only after the main roadmap is complete:

* PostgreSQL configuration storage
* Redis distributed rate limiting
* Web management console
* Kubernetes deployment
* Service discovery
* Distributed tracing
* Multi-tenant quotas
* Cost accounting
* Canary routing
* Automatic provider scaling

These features are not current project requirements.

---

## 15. Development Order

The required order is:

```text
Repository Foundation
        |
        v
Basic Non-Streaming Gateway
        |
        v
SSE Streaming
        |
        v
Real HTTP Provider
        |
        v
Multiple Providers and Static Routing
        |
        v
Timeout, Retry, and Fallback
        |
        v
Authentication and Traffic Control
        |
        v
Logging and Metrics
        |
        v
Benchmarking Tool
        |
        v
MaxKB and RAGFlow Integration
        |
        v
Performance-Aware Routing
```

A later milestone must not be implemented before the important behavior of earlier milestones has been tested.

---

## 16. Immediate Next Step

The next task is to complete and approve:

```text
docs/specs/001-basic-gateway.md
```

After the specification is complete, Codex should enter planning mode and propose an implementation plan before modifying application code.
