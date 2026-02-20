
import os
from typing import Optional
from .base import LLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

class LLMFactory:
    _instance: Optional[LLMProvider] = None
    
    @classmethod
    def create_provider(cls, name: str) -> LLMProvider:
        name = name.lower()
        if name == "ollama":
            url = os.getenv("OLLAMA_URL", "http://llama:11434")
            model = os.getenv("OLLAMA_MODEL", "tinyllama")
            return OllamaProvider(url, model)
        elif name == "openai":
            key = os.getenv("OPENAI_API_KEY", "")
            model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
            return OpenAIProvider(key, model)
        elif name == "docker":
            # Reuse OpenAI provider structure but with Docker Model Runner URL
            key = "unused" # Docker Model Runner doesn't require a key
            model = "hf.co/qwen/qwen2.5-coder-7b-instruct" # Default docker model
            # Override base URL env var for OpenAI provider
            # This is a bit of a hack, but OpenAIProvider likely uses OPENAI_BASE_URL env var or we need to pass it
            # Let's see how OpenAIProvider is implemented.
            # Assuming OpenAIProvider uses standard openai client which respects OPENAI_BASE_URL
            return OpenAIProvider(key, model)
        else:
            raise ValueError(f"Unknown LLM provider: {name}")

    @classmethod
    def get_provider(cls) -> LLMProvider:
        if cls._instance:
            return cls._instance
            
        provider_name = os.getenv("LLM_PROVIDER", "ollama")
        cls._instance = cls.create_provider(provider_name)
        return cls._instance
    
    @classmethod
    def get_default_provider(cls) -> LLMProvider:
        return cls.get_provider()
