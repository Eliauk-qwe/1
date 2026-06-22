# Project Instructions

## Project Overview

This repository implements an OpenAI-compatible LLM inference gateway and performance benchmarking platform for self-hosted inference engines.

The gateway sits between upstream AI applications and downstream model-serving systems.

Upstream clients may include:

* OpenAI SDK clients
* MaxKB
* RAGFlow
* Custom AI applications

Downstream providers may include:

* Mock providers used for testing
* vLLM
* SGLang
* OpenAI-compatible cloud model services

## Project Responsibilities

This project is responsible for:

* OpenAI-compatible API endpoints
* Provider adaptation
* Model registration and routing
* Streaming SSE forwarding
* Authentication and authorization
* Rate limiting and concurrency control
* Timeout, retry, fallback, and circuit breaking
* Request logging and metrics
* Token usage statistics
* Inference performance benchmarking

## Architecture Boundaries

Do not implement the following features in this repository unless an approved specification explicitly requires them:

* RAG document parsing
* Vector databases
* Knowledge-base management
* Agent workflows
* Model training
* Model fine-tuning
* GPU kernel implementation
* KV Cache internals
* A general-purpose chat frontend

MaxKB and RAGFlow are external upstream clients.

vLLM and SGLang are external downstream inference engines.

## Engineering Workflow

Before modifying code:

1. Read the relevant documents under `docs/`.
2. Read the specification for the current task under `docs/specs/`.
3. Explain the request flow and affected modules.
4. Identify unclear requirements before making architectural assumptions.
5. Do not modify unrelated files.

During implementation:

1. Keep changes limited to the current specification.
2. Separate API, provider, routing, resilience, storage, and observability responsibilities.
3. Add or update tests for all changed behavior.
4. Do not add infrastructure that is outside the current development stage.
5. Prefer the simplest correct implementation that can be extended later.

After implementation:

1. Run the relevant tests.
2. Report the commands that were executed.
3. Summarize changed files.
4. Explain important design decisions.
5. List remaining limitations honestly.
6. Do not claim success when tests have not been run or have failed.

## Technical Conventions

* Use Python 3.12.
* Use FastAPI for the HTTP API.
* Use Pydantic for external request validation.
* Use `httpx.AsyncClient` for asynchronous upstream HTTP requests.
* Use type annotations for public functions and important internal interfaces.
* Use asynchronous code for request handling and provider communication.
* Do not hard-code provider URLs, API keys, timeouts, or model mappings.
* Never commit secrets or real API keys.
* Never log authorization headers or complete API keys.
* Avoid logging full prompts or responses by default.
* Keep external API schemas separate from internal domain models.
* Keep provider-specific behavior out of the API layer.
* Avoid unrelated refactoring in feature commits.

## Testing Requirements

Every implemented feature should include tests for:

* Normal behavior
* Invalid input
* Provider errors
* Boundary conditions relevant to the feature

Streaming features must also verify:

* Chunks are forwarded incrementally
* Resources are closed correctly
* Client cancellation is handled
* Errors before and after the first streamed chunk are distinguished

## Definition of Done

A task is complete only when:

* The implementation matches the current specification.
* The normal path and important failure paths are tested.
* Relevant tests pass.
* Configuration and secrets are not hard-coded.
* Documentation is updated when behavior changes.
* No unrelated functionality is included.
* Remaining limitations are clearly documented.

## Current Development Rule

Implement one specification at a time.

The first development target is:

`docs/specs/001-basic-gateway.md`

Do not implement streaming, databases, Redis, authentication, rate limiting, retries, dashboards, or real model providers until their corresponding specifications are approved.
