"""Model catalog sources — live and static."""

from .ollama import detect_pulled_models, is_ollama_available

__all__ = ["detect_pulled_models", "is_ollama_available"]
