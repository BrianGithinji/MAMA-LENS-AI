"""
MAMA-LENS AI — Swahili (Kiswahili) Language Translator
Uses Helsinki-NLP/opus-mt-en-swc and opus-mt-swc-en (MarianMT) for
English <-> Swahili translation as a fallback/enhancement layer.
Note: Swahili (sw) goes directly to Mistral with a Swahili system prompt.
This module is used when translation enhancement is needed.
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

EN_TO_SW_MODEL = "Helsinki-NLP/opus-mt-en-swc"
SW_TO_EN_MODEL = "Helsinki-NLP/opus-mt-swc-en"


@lru_cache(maxsize=1)
def _load_en_to_sw():
    from transformers import MarianMTModel, MarianTokenizer
    tokenizer = MarianTokenizer.from_pretrained(EN_TO_SW_MODEL)
    model = MarianMTModel.from_pretrained(EN_TO_SW_MODEL)
    model.eval()
    return tokenizer, model


@lru_cache(maxsize=1)
def _load_sw_to_en():
    from transformers import MarianMTModel, MarianTokenizer
    tokenizer = MarianTokenizer.from_pretrained(SW_TO_EN_MODEL)
    model = MarianMTModel.from_pretrained(SW_TO_EN_MODEL)
    model.eval()
    return tokenizer, model


def _translate(text: str, loader_fn) -> str:
    try:
        import torch
        tokenizer, model = loader_fn()
        inputs = tokenizer([text], return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=512, num_beams=4, early_stopping=True)
        return tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        logger.error("Swahili translation error: %s", e)
        return text


def swahili_to_english(text: str) -> str:
    return _translate(text, _load_sw_to_en)


def english_to_swahili(text: str) -> str:
    return _translate(text, _load_en_to_sw)


def is_available() -> bool:
    try:
        _load_sw_to_en()
        _load_en_to_sw()
        return True
    except Exception as e:
        logger.warning("Swahili translator not available: %s", e)
        return False
