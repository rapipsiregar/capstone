"""
IndoBERT Model Loader Service.
Reads model weights location from environment variables (.env),
loads models and tokenizers once on-demand (singleton pattern),
and provides descriptive error messages if model files are missing.
"""

import os
import torch
from typing import Tuple, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_CACHED_TRUST_MODEL = None
_CACHED_TRUST_TOKENIZER = None
_CACHED_ASPECT_MODEL = None
_CACHED_ASPECT_TOKENIZER = None


def get_configured_device() -> torch.device:
    """Returns configured torch device (defaults to cuda if available)."""
    env_device = os.environ.get("TORCH_DEVICE", "")
    if env_device:
        return torch.device(env_device)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_trust_model_path() -> str:
    """Gets the path or HuggingFace repo for the trust classification model."""
    return os.environ.get("INDOBERT_TRUST_MODEL_PATH", "models/indobert_trust")


def get_aspect_model_path() -> str:
    """Gets the path or HuggingFace repo for the aspect classification model."""
    return os.environ.get("INDOBERT_ASPECT_MODEL_PATH", "models/indobert_aspect")


def load_model_and_tokenizer(
    model_path: str,
    device: Optional[torch.device] = None,
) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """
    Loads a sequence classification model and tokenizer from local path or HF repo.
    Raises FileNotFoundError with a clear message if local path does not exist.
    """
    is_local_path = os.path.exists(model_path) or "/" in model_path or "\\" in model_path
    if is_local_path and not os.path.exists(model_path):
        raise FileNotFoundError(
            f"IndoBERT model weights not found at '{model_path}'. "
            f"Please verify the directory exists or check your .env configuration."
        )

    target_device = device or get_configured_device()

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path).to(target_device)
        model.eval()
        return model, tokenizer
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load IndoBERT model from '{model_path}': {str(exc)}"
        ) from exc


def get_trust_model(
    force_reload: bool = False,
) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """Loads and caches the fine-tuned trust sentiment classifier."""
    global _CACHED_TRUST_MODEL, _CACHED_TRUST_TOKENIZER

    if force_reload or _CACHED_TRUST_MODEL is None or _CACHED_TRUST_TOKENIZER is None:
        path = get_trust_model_path()
        model, tokenizer = load_model_and_tokenizer(path)
        _CACHED_TRUST_MODEL = model
        _CACHED_TRUST_TOKENIZER = tokenizer

    return _CACHED_TRUST_MODEL, _CACHED_TRUST_TOKENIZER


def get_aspect_model(
    force_reload: bool = False,
) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """Loads and caches the fine-tuned aspect communication classifier."""
    global _CACHED_ASPECT_MODEL, _CACHED_ASPECT_TOKENIZER

    if force_reload or _CACHED_ASPECT_MODEL is None or _CACHED_ASPECT_TOKENIZER is None:
        path = get_aspect_model_path()
        model, tokenizer = load_model_and_tokenizer(path)
        _CACHED_ASPECT_MODEL = model
        _CACHED_ASPECT_TOKENIZER = tokenizer

    return _CACHED_ASPECT_MODEL, _CACHED_ASPECT_TOKENIZER


def reset_cached_models() -> None:
    """Clears cached model singletons from memory."""
    global _CACHED_TRUST_MODEL, _CACHED_TRUST_TOKENIZER
    global _CACHED_ASPECT_MODEL, _CACHED_ASPECT_TOKENIZER
    _CACHED_TRUST_MODEL = None
    _CACHED_TRUST_TOKENIZER = None
    _CACHED_ASPECT_MODEL = None
    _CACHED_ASPECT_TOKENIZER = None
