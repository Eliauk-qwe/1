# LLM Inference Gateway and Benchmarking Platform

## 1. Project Background

Large language model applications often need to access multiple model-serving backends, such as self-hosted vLLM or SGLang instances and OpenAI-compatible cloud model services.

These backends may use similar APIs, but they can differ in:

* Model names
* Authentication methods
* Request parameters
* Error formats
* Availability
* Performance
* Deployment environments

If every upstream application connects directly to every model backend, the system becomes difficult to manage.

Authentication, routing, retries, monitoring, and performance measurement may be implemented repeatedly in different applications.

This project introduces a unified inference gateway between AI applications and model-serving backends.

## 2. Project Goal

The goal of this project is to build an OpenAI-compatible LLM inference gateway and performance benchmarking platform.

The platform provides a unified API for upstream applications and forwards requests to one or more downstream model-serving backends.

It is responsible for:

* Protocol compatibility
* Provider adaptation
* Model routing
* Traffic governance
* Failure handling
* Request observability
* Inference performance benchmarking

## 3. System Position

The project is positioned between upstream AI applications and downstream inference engines.

```text
OpenAI SDK / MaxKB / RAGFlow / Custom Applications
                         |
                         v
              LLM Inference Gateway
                         |
                         v
        vLLM / SGLang / Cloud Model Services
```

Upstream applications only need to use the OpenAI-compatible API exposed by the gateway.

They do not need to know the real provider address, authentication method, model deployment location, or routing strategy.

## 4. Target Users

The intended users include:

* Developers building applications with the OpenAI SDK
* Teams deploying models through vLLM or SGLang
* Users connecting MaxKB or RAGFlow to self-hosted models
* Engineers comparing inference performance across models and backends
* AI infrastructure learners studying model-serving systems

## 5. Core Capabilities

The planned platform includes the following capabilities.

### 5.1 OpenAI-Compatible API

The gateway exposes OpenAI-compatible endpoints so existing SDKs and AI applications can connect with minimal changes.

Initial endpoints include:

* `GET /health`
* `GET /v1/models`
* `POST /v1/chat/completions`

### 5.2 Provider Adaptation

The gateway hides differences between downstream providers.

Planned providers include:

* Mock Provider
* vLLM
* SGLang
* OpenAI-compatible cloud services

### 5.3 Model Registration and Routing

The gateway maps public model names to actual providers and upstream model names.

Future routing strategies may include:

* Static routing
* Round-robin routing
* Weighted routing
* Least-concurrency routing
* Latency-aware routing
* Failure fallback

### 5.4 Traffic Governance

The gateway will gradually support:

* API authentication
* Request rate limiting
* Token rate limiting
* Concurrency control
* Timeout control
* Retry policies
* Circuit breaking
* Provider fallback

### 5.5 Observability

The gateway will collect request-level logs and system-level metrics.

Important metrics include:

* Request count
* Success rate
* Error rate
* End-to-end latency
* Time to First Token
* Time per Output Token
* Token throughput
* Current concurrency
* Provider health status

### 5.6 Performance Benchmarking

The benchmarking module will generate inference workloads and measure the performance of the gateway and downstream providers.

It will support comparisons such as:

* Direct vLLM access versus gateway access
* Different concurrency levels
* Different models
* Different providers
* Streaming versus non-streaming requests
* Short prompts versus long RAG contexts

## 6. Project Scope

This project focuses on model-serving access and governance.

It includes:

* OpenAI-compatible request handling
* HTTP request forwarding
* Streaming response forwarding
* Provider abstraction
* Model routing
* Resilience mechanisms
* Metrics and logging
* Benchmark workload generation
* Benchmark report generation

## 7. Out of Scope

The following features are not part of this project:

* Document parsing
* Vector databases
* Knowledge-base management
* RAG retrieval implementation
* Agent workflow implementation
* Model training
* Model fine-tuning
* Model quantization
* GPU kernel development
* Internal KV Cache implementation
* A general-purpose chat application

MaxKB and RAGFlow are treated as external upstream applications.

vLLM and SGLang are treated as external downstream inference engines.

## 8. Relationship with Existing Projects

### vLLM and SGLang

vLLM and SGLang perform the actual model inference.

This project does not replace them. It provides a governance and compatibility layer in front of them.

### MaxKB and RAGFlow

MaxKB and RAGFlow provide knowledge-base, RAG, and application-building capabilities.

They can connect to this gateway through an OpenAI-compatible API.

### LiteLLM and Other AI Gateways

Existing AI gateway projects provide important architectural references.

This project has a narrower learning and engineering focus:

* Self-hosted inference engines
* Transparent streaming forwarding
* Inference-specific metrics
* Integrated performance benchmarking
* Measurable gateway overhead
* Routing experiments based on runtime performance

## 9. Project Differentiation

The main distinguishing feature is the combination of an inference gateway and a performance benchmarking platform.

The project will not only forward requests but also answer questions such as:

* How much latency does the gateway add?
* How does concurrency affect TTFT?
* Which provider currently has lower latency?
* When should requests be routed to a backup provider?
* How do long RAG contexts affect performance?
* What is the P95 latency under a given workload?
* How many output tokens can the system generate per second?

## 10. Development Principles

The project follows these principles:

* Build one verified request path before adding infrastructure.
* Implement one specification at a time.
* Prefer simple and testable designs.
* Separate API, provider, routing, resilience, and observability responsibilities.
* Do not introduce Redis, databases, dashboards, or Kubernetes before they are required.
* Measure behavior instead of assuming performance.
* Do not claim that a feature works without running relevant tests.

## 11. First Development Milestone

The first milestone is a minimal runnable request path:

```text
OpenAI Python SDK
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

The first milestone includes:

* `GET /health`
* `GET /v1/models`
* Non-streaming `POST /v1/chat/completions`
* One mock model
* OpenAI-compatible response structures
* Structured error responses
* Unit and integration tests

The first milestone does not include:

* Streaming
* Real vLLM integration
* Authentication
* Redis
* Database storage
* Rate limiting
* Retry
* Circuit breaking
* Dashboard

## 12. Final Demonstration

The completed platform should demonstrate:

1. An OpenAI SDK client calling multiple inference backends through one gateway.
2. MaxKB or RAGFlow accessing a self-hosted model through the gateway.
3. Streaming responses passing through the gateway incrementally.
4. Automatic fallback when one provider becomes unavailable.
5. Request and inference metrics displayed through monitoring tools.
6. Benchmark comparisons between direct backend access and gateway access.
7. Performance changes under different concurrency levels and prompt lengths.
