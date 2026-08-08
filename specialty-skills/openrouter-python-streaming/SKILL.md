---
name: openrouter-python-streaming
description: Connect to OpenRouter API and stream responses using LiteLLM in Python. Includes async streaming, retry logic, and multi-provider access to 400+ models.
tags: [openrouter, llm, streaming, python, litellm, async, openai-compatible]
---

# OpenRouter Python Streaming Guide

## Overview

Connect to OpenRouter's unified API and stream LLM responses using LiteLLM. OpenRouter provides access to 400+ models (GPT-4o, Claude, Gemini, Grok, etc.) through a single API key with OpenAI-compatible endpoints.

## Prerequisites

1. Get an API key from [OpenRouter](https://openrouter.ai/keys)
2. Browse available models at [OpenRouter Models](https://openrouter.ai/docs#models)

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "litellm>=1.79.3",
]
```

Or install directly:
```bash
pip install litellm
# or with uv
uv add litellm
```

## Environment Setup

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
MODEL_PROVIDER=openrouter
MODEL=openrouter/openai/gpt-4o-mini
```

## Minimal Streaming Example

```python
import asyncio
import os
from typing import AsyncGenerator
import litellm

async def stream_openrouter(
    messages: list[dict[str, str]],
    model: str = "openrouter/openai/gpt-4o-mini",
) -> AsyncGenerator[str, None]:
    """Stream responses from OpenRouter."""
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        stream=True,
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content

async def main():
    messages = [{"role": "user", "content": "Hello!"}]
    async for text in stream_openrouter(messages):
        print(text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())
```

## Production-Ready LLM Client

```python
import asyncio
import os
import random
from typing import AsyncGenerator, Optional
import litellm
from litellm.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    Timeout,
)

litellm.suppress_debug_info = True
litellm.drop_params = True

RETRYABLE = (RateLimitError, Timeout, APIConnectionError, InternalServerError, APIError)
NON_RETRYABLE = (AuthenticationError, BadRequestError, NotFoundError)

class OpenRouterClient:
    """Async OpenRouter streaming client with retry and backoff."""

    VALID_PREFIXES = (
        "openrouter/",
        "openai/",
        "anthropic/",
        "google/",
        "mistral/",
        "meta-llama/",
        "x-ai/",
    )

    def __init__(
        self,
        model: str = "openrouter/openai/gpt-4o-mini",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        timeout: float = 30.0,
        stream_timeout: float = 5.0,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.stream_timeout = stream_timeout

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

    def _compute_delay(self, attempt: int) -> float:
        """Exponential backoff with jitter."""
        base = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        return base * random.uniform(0.75, 1.25)

    async def stream_completion(
        self,
        messages: list[dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """Stream completion with retry logic."""
        attempt = 0
        while True:
            attempt += 1
            try:
                async for chunk in self._stream_once(messages, max_tokens, temperature):
                    yield chunk
                return
            except NON_RETRYABLE:
                raise
            except RETRYABLE as e:
                if attempt >= self.max_retries:
                    raise
                delay = self._compute_delay(attempt)
                await asyncio.sleep(delay)

    async def _stream_once(
        self,
        messages: list[dict[str, str]],
        max_tokens: Optional[int],
        temperature: float,
    ) -> AsyncGenerator[str, None]:
        """Single streaming attempt."""
        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "timeout": self.timeout,
            "temperature": temperature,
            "api_key": self.api_key,
        }
        if max_tokens:
            request_kwargs["max_tokens"] = max_tokens

        response = await litellm.acompletion(**request_kwargs)

        first_chunk = True
        async for chunk in response:
            if first_chunk:
                first_chunk = False
            content = self._extract_content(chunk)
            if content:
                yield content

    def _extract_content(self, chunk) -> str:
        """Extract text from streaming chunk."""
        try:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    return delta.content

            if isinstance(chunk, dict):
                choices = chunk.get("choices", [])
                if choices:
                    content = choices[0].get("delta", {}).get("content")
                    if content:
                        return content
            return ""
        except (AttributeError, KeyError, IndexError):
            return ""
```

## Usage Patterns

### Basic Chat

```python
async def chat():
    client = OpenRouterClient(model="openrouter/openai/gpt-4o")
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Explain async in Python briefly."},
    ]

    async for chunk in client.stream_completion(messages):
        print(chunk, end="", flush=True)
```

### Multi-Turn Conversation

```python
async def conversation():
    client = OpenRouterClient()
    history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break

        history.append({"role": "user", "content": user_input})

        response = ""
        print("Assistant: ", end="")
        async for chunk in client.stream_completion(history):
            print(chunk, end="", flush=True)
            response += chunk
        print()

        history.append({"role": "assistant", "content": response})
```

### Using OpenAI SDK Directly

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Non-streaming
completion = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(completion.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### With Usage Statistics

```python
async def stream_with_usage():
    """Stream and get token usage in final chunk."""
    response = await litellm.acompletion(
        model="openrouter/openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}],
        stream=True,
        stream_options={"include_usage": True},
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    async for chunk in response:
        if hasattr(chunk, "usage") and chunk.usage:
            print(f"\nTokens: {chunk.usage}")
        elif chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
```

## Model Configuration

### Popular OpenRouter Models

```python
# Format: openrouter/<provider>/<model>
MODELS = {
    # OpenAI
    "openrouter/openai/gpt-4o": "Latest GPT-4",
    "openrouter/openai/gpt-4o-mini": "Fast, cheap GPT-4",
    "openrouter/openai/o1-preview": "Reasoning model",

    # Anthropic
    "openrouter/anthropic/claude-3.5-sonnet": "Best Claude",
    "openrouter/anthropic/claude-3-opus": "Most capable Claude",

    # Google
    "openrouter/google/gemini-2.0-flash-exp": "Fast Gemini",
    "openrouter/google/gemini-pro-1.5": "Long context",

    # xAI
    "openrouter/x-ai/grok-4-fast": "Grok 4",

    # Meta
    "openrouter/meta-llama/llama-3.1-405b-instruct": "Largest Llama",
    "openrouter/meta-llama/llama-3.1-70b-instruct": "Strong Llama",

    # Free models (rate limited)
    "openrouter/meta-llama/llama-3.2-3b-instruct:free": "Free tier",
}
```

### Provider Abstraction Pattern

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelProvider:
    name: str
    display_name: str
    default_model: str
    model_prefixes: tuple[str, ...]
    api_base: Optional[str] = None
    api_key_env: Optional[str] = None

PROVIDERS = {
    "openrouter": ModelProvider(
        name="openrouter",
        display_name="OpenRouter",
        default_model="openrouter/openai/gpt-4o-mini",
        model_prefixes=("openrouter/",),
        api_key_env="OPENROUTER_API_KEY",
    ),
    "ollama": ModelProvider(
        name="ollama",
        display_name="Ollama (Local)",
        default_model="ollama/llama3.1",
        model_prefixes=("ollama/",),
        api_base="http://localhost:11434",
    ),
}

def infer_provider(model: str) -> Optional[ModelProvider]:
    """Infer provider from model name prefix."""
    for provider in PROVIDERS.values():
        for prefix in provider.model_prefixes:
            if model.startswith(prefix):
                return provider
    return None
```

## Error Handling

```python
from litellm.exceptions import (
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
)

async def safe_stream(client: OpenRouterClient, messages: list):
    try:
        async for chunk in client.stream_completion(messages):
            yield chunk
    except AuthenticationError:
        raise ValueError("Invalid OPENROUTER_API_KEY")
    except RateLimitError:
        raise RuntimeError("Rate limited - wait or upgrade plan")
    except APIConnectionError:
        raise ConnectionError("Cannot connect to OpenRouter")
    except Exception as e:
        raise RuntimeError(f"LLM error: {e}")
```

## OpenRouter-Specific Features

### Custom Headers for Attribution

```python
# Track usage on OpenRouter leaderboard
response = await litellm.acompletion(
    model="openrouter/openai/gpt-4o",
    messages=messages,
    stream=True,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    extra_headers={
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "Your App Name",
    },
)
```

### Model Routing and Fallbacks

```python
# OpenRouter handles routing automatically
# Use model groups for automatic fallback
response = await litellm.acompletion(
    model="openrouter/openai/gpt-4o",  # Falls back if unavailable
    messages=messages,
    stream=True,
)
```

## Quick Start Checklist

1. Get API key: [openrouter.ai/keys](https://openrouter.ai/keys)
2. Set env: `export OPENROUTER_API_KEY=sk-or-v1-...`
3. Add dependency: `pip install litellm`
4. Copy minimal example above
5. Run: `python your_script.py`

## Key Points

- **LiteLLM** provides unified interface; prefix models with `openrouter/`
- **API Key**: Set `OPENROUTER_API_KEY` env var
- **Model format**: `openrouter/<provider>/<model>`
- **Base URL**: `https://openrouter.ai/api/v1` (handled by LiteLLM)
- **SSE streaming**: Use `stream=True`, handle `[DONE]` terminator
- **Error handling**: Check `finish_reason: "error"` for mid-stream errors
- **Usage stats**: Pass `stream_options={"include_usage": True}`
- Use **async generators** for streaming
- Implement **exponential backoff** for rate limits and transient errors
