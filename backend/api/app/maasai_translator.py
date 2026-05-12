"""
MAMA-LENS AI — Maasai Language Translator
Uses NorthernTribe-Research/maasai-en-mt for English <-> Maasai translation.
Translates user Maasai input to English for Mistral, then back to Maasai for response.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_ID = "NorthernTribe-Research/maasai-en-mt"


@lru_cache(maxsize=1)
def _load_models():
    """Load translation models once and cache them."""
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
    model.eval()
    return tokenizer, model


def _translate(text: str, src_lang: str, tgt_lang: str) -> str:
    try:
        tokenizer, model = _load_models()
        import torch

        # Set source language token if tokenizer supports it
        if hasattr(tokenizer, "src_lang"):
            tokenizer.src_lang = src_lang

        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        with torch.no_grad():
            # Force target language token if available
            forced_bos = None
            if hasattr(tokenizer, "lang_code_to_id") and tgt_lang in tokenizer.lang_code_to_id:
                forced_bos = tokenizer.lang_code_to_id[tgt_lang]

            kwargs = dict(max_new_tokens=512, num_beams=4, early_stopping=True)
            if forced_bos is not None:
                kwargs["forced_bos_token_id"] = forced_bos

            output = model.generate(**inputs, **kwargs)

        return tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        logger.error("Maasai translation error (%s->%s): %s", src_lang, tgt_lang, e)
        return text  # Return original text on failure


def maasai_to_english(text: str) -> str:
    """Translate Maasai text to English."""
    return _translate(text, src_lang="maa", tgt_lang="en")


def english_to_maasai(text: str) -> str:
    """Translate English text to Maasai."""
    return _translate(text, src_lang="en", tgt_lang="maa")


def is_available() -> bool:
    """Check if the translation model can be loaded."""
    try:
        _load_models()
        return True
    except Exception as e:
        logger.warning("Maasai translator not available: %s", e)
        return False
