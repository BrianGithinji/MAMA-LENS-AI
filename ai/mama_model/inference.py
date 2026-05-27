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
# HF Hub repo — set HF_MODEL_ID env var on Render, or falls back to base model
_HF_MODEL_ID = os.environ.get("HF_MODEL_ID", "BrianGithinji/mama-flan-t5")

# Cache dir for Render (ephemeral but persists within a deploy session)
_HF_CACHE_DIR = os.environ.get("HF_HOME", "/tmp/hf_cache")

# Singleton
_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    local_weights = _FINETUNED_PATH / "model.safetensors"

    if _FINETUNED_PATH.exists() and local_weights.exists():
        # Local fine-tuned weights found (dev machine)
        model_path = str(_FINETUNED_PATH)
        logger.info("Loading local fine-tuned MAMA model: %s", model_path)
    elif _HF_MODEL_ID and _HF_MODEL_ID != "BrianGithinji/mama-flan-t5":
        # Custom HF repo set via env var
        model_path = _HF_MODEL_ID
        logger.info("Loading MAMA model from HF Hub (env): %s", model_path)
    else:
        # Try HF Hub fine-tuned repo, fall back to base model
        try:
            from huggingface_hub import repo_exists
            if repo_exists(_HF_MODEL_ID):
                model_path = _HF_MODEL_ID
                logger.info("Loading MAMA model from HF Hub: %s", model_path)
            else:
                model_path = _BASE_MODEL
                logger.warning("HF Hub repo not found (%s), using base model", _HF_MODEL_ID)
        except Exception:
            model_path = _BASE_MODEL
            logger.warning("HF Hub check failed, using base model: %s", _BASE_MODEL)

    _tokenizer = AutoTokenizer.from_pretrained(model_path, cache_dir=_HF_CACHE_DIR)
    _model = AutoModelForSeq2SeqLM.from_pretrained(model_path, cache_dir=_HF_CACHE_DIR)
    _model.eval()
    logger.info("MAMA model loaded: %s", model_path)


def generate(
    prompt: str,
    max_new_tokens: int = 300,
    temperature: float = 0.7,
    num_beams: int = 4,
    conversation_history: Optional[list] = None,
) -> str:
    """
    Generate a maternal health response for the given prompt.

    Args:
        prompt: The current user message.
        max_new_tokens: Maximum tokens to generate.
        temperature: Sampling temperature (lower = more focused).
        num_beams: Beam search width.
        conversation_history: List of {role, content} dicts for context.

    Returns:
        Generated response string.
    """
    _load_model()

    import torch

    # Build context-aware prompt from conversation history
    context_parts = []
    if conversation_history:
        # Include last 4 turns (2 user + 2 assistant) to stay within token limit
        for turn in conversation_history[-4:]:
            role_label = "Patient" if turn["role"] == "user" else "MAMA"
            context_parts.append(f"{role_label}: {turn['content']}")

    context_str = "\n".join(context_parts)
    if context_str:
        full_prompt = f"maternal health conversation:\n{context_str}\nPatient: {prompt}\nMAMA:"
    else:
        full_prompt = f"maternal health: {prompt}"

    inputs = _tokenizer(
        full_prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True,
    )

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
            temperature=temperature,
            do_sample=temperature > 0,
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
