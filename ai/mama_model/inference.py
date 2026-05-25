"""
MAMA-LENS AI — Local Model Inference Engine
Loads the fine-tuned google/flan-t5-base model for offline maternal health responses.
Falls back to the base model if the fine-tuned model is not yet available.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_FINETUNED_PATH = Path(__file__).parent / "mama-flan-t5"
_BASE_MODEL = "google/flan-t5-base"

# Singleton — loaded once on first use
_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    model_path = str(_FINETUNED_PATH) if _FINETUNED_PATH.exists() else _BASE_MODEL
    logger.info("Loading MAMA model from: %s", model_path)

    _tokenizer = AutoTokenizer.from_pretrained(model_path)
    _model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    _model.eval()
    logger.info("MAMA model loaded successfully.")


def generate(
    prompt: str,
    max_new_tokens: int = 300,
    temperature: float = 0.7,
    num_beams: int = 4,
) -> str:
    """
    Generate a maternal health response for the given prompt.

    Args:
        prompt: The input text prefixed with 'maternal health: '
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature (lower = more focused)
        num_beams: Beam search width (higher = better quality, slower)

    Returns:
        Generated response string.
    """
    _load_model()

    import torch

    # Prefix ensures the model stays in maternal health domain
    if not prompt.startswith("maternal health:"):
        prompt = f"maternal health: {prompt}"

    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        max_length=256,
        truncation=True,
    )

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            early_stopping=True,
            no_repeat_ngram_size=3,
        )

    return _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def is_available() -> bool:
    """Check if transformers + torch are installed."""
    try:
        import transformers
        import torch
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_prompts = [
        "Hello, I am 20 weeks pregnant",
        "Ninajisikia huzuni sana leo",
        "I have a severe headache and blurred vision",
        "What should I eat during pregnancy?",
        "Mtoto wangu hasogei",
    ]
    for p in test_prompts:
        print(f"\nInput: {p}")
        print(f"MAMA: {generate(p)}")
