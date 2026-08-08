---
name: ollama-python-streaming
description: Connect to local Ollama LLM and stream responses using LiteLLM in Python. Includes async streaming, retry logic, and thinking model support.
tags: [ollama, llm, streaming, python, litellm, async]
---

# Ollama Python Streaming Guide

## Overview

Connect to a local Ollama instance and stream LLM responses using LiteLLM as the abstraction layer. LiteLLM provides a unified interface that works with Ollama, OpenAI, Anthropic, and other providers with consistent request/response handling.

## Prerequisites

```bash
# Install and start Ollama
brew install ollama
ollama serve

# Pull the recommended model
ollama pull gpt-oss:20b
```

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
MODEL_PROVIDER=ollama
MODEL=ollama/gpt-oss:20b

# Thinking model config (gpt-oss supports low/medium/high)
OLLAMA_THINKING=low
OLLAMA_HIDE_THINKING=true
```

## Minimal Streaming Example

```python
import asyncio
from typing import AsyncGenerator
import litellm

async def stream_ollama(
    messages: list[dict[str, str]],
    model: str = "ollama/gpt-oss:20b",
) -> AsyncGenerator[str, None]:
    """Stream responses from local Ollama."""
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        stream=True,
        api_base="http://localhost:11434",
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content

async def main():
    messages = [{"role": "user", "content": "Hello!"}]
    async for text in stream_ollama(messages):
        print(text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())
```

## Production-Ready LLM Client

```python
import asyncio
import random
from typing import AsyncGenerator, Optional
import litellm
from litellm import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    Timeout,
)

RETRYABLE = (RateLimitError, Timeout, APIConnectionError, InternalServerError, APIError)
NON_RETRYABLE = (AuthenticationError, BadRequestError, NotFoundError)

class LLMClient:
    def __init__(
        self,
        model: str = "ollama/gpt-oss:20b",
        api_base: str = "http://localhost:11434",
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        timeout: float = 30.0,
        stream_timeout: float = 5.0,
    ):
        self.model = model
        self.api_base = api_base
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.stream_timeout = stream_timeout

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
        }
        if self.api_base:
            request_kwargs["api_base"] = self.api_base
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
        """Extract text from various chunk formats."""
        try:
            # Standard format
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    return delta.content

            # Dict format (some providers)
            if isinstance(chunk, dict):
                choices = chunk.get("choices", [])
                if choices:
                    content = choices[0].get("delta", {}).get("content")
                    if content:
                        return content

                # Ollama thinking model format
                if "thinking" in chunk:
                    if chunk.get("response"):
                        return chunk["response"]
                    return ""

            return ""
        except (AttributeError, KeyError, IndexError):
            return ""
```

## Usage Patterns

### Basic Chat

```python
async def chat():
    client = LLMClient(model="ollama/gpt-oss:20b")
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
    client = LLMClient()
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

### With Timeout Handling

```python
async def stream_with_timeout(client: LLMClient, messages: list, timeout: float = 30.0):
    """Stream with overall timeout."""
    async def collect():
        result = []
        async for chunk in client.stream_completion(messages):
            result.append(chunk)
            yield chunk
        return result

    try:
        async for chunk in asyncio.timeout(timeout)(collect()):
            yield chunk
    except asyncio.TimeoutError:
        raise TimeoutError(f"Stream exceeded {timeout}s")
```

## Model Configuration

### Supported Ollama Models

```python
# Format: ollama/<model-name>
MODELS = {
    "ollama/gpt-oss:20b",   # Recommended - with thinking support
    "ollama/llama3.1",
    "ollama/mistral",
}
```

### Thinking Model Support

For models with thinking/reasoning capabilities (like gpt-oss):

```python
def build_ollama_extra_body(model: str) -> dict:
    """Configure Ollama thinking behavior."""
    extra_body = {}

    # Hide thinking tokens in output
    extra_body["hidethinking"] = True

    # Enable/configure thinking
    if "gpt-oss" in model.lower():
        # gpt-oss uses low/medium/high
        extra_body["think"] = "low"  # or "medium", "high"
    else:
        extra_body["think"] = False  # Boolean for other models

    return extra_body

# Usage with extra_body
response = await litellm.acompletion(
    model="ollama/gpt-oss:20b",
    messages=messages,
    stream=True,
    api_base="http://localhost:11434",
    extra_body=build_ollama_extra_body("ollama/gpt-oss:20b"),
)
```

## Provider Abstraction Pattern

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
    "ollama": ModelProvider(
        name="ollama",
        display_name="Ollama (Local)",
        default_model="ollama/gpt-oss:20b",
        model_prefixes=("ollama/",),
        api_base="http://localhost:11434",
        api_key_env=None,
    ),
    "openai": ModelProvider(
        name="openai",
        display_name="OpenAI",
        default_model="gpt-4",
        model_prefixes=("gpt-",),
        api_key_env="OPENAI_API_KEY",
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
from litellm import (
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
)

async def safe_stream(client: LLMClient, messages: list):
    try:
        async for chunk in client.stream_completion(messages):
            yield chunk
    except APIConnectionError:
        # Ollama not running or network issue
        raise ConnectionError("Cannot connect to Ollama. Is it running?")
    except RateLimitError:
        # Shouldn't happen with local Ollama, but handle for other providers
        raise RuntimeError("Rate limited")
    except Exception as e:
        raise RuntimeError(f"LLM error: {e}")
```

## Quick Start Checklist

1. Install Ollama: `brew install ollama`
2. Start server: `ollama serve`
3. Pull model: `ollama pull gpt-oss:20b`
4. Add dependency: `pip install litellm`
5. Copy minimal example above
6. Run: `python your_script.py`

## Key Points

- **LiteLLM** provides unified interface across providers
- **Recommended model**: `ollama/gpt-oss:20b` (with thinking support)
- **Model format**: `ollama/<model-name>`
- **Default endpoint**: `http://localhost:11434`
- **No API key** needed for local Ollama
- Use **async generators** for streaming
- Implement **exponential backoff** for retries
- Configure **thinking levels** (low/medium/high) for gpt-oss models
