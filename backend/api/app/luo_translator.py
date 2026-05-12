"""
MAMA-LENS AI — Luo (Dholuo) Language Translator
Uses Helsinki-NLP/opus-mt-en-luo and opus-mt-luo-en (MarianMT) for
English <-> Luo translation.
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

EN_TO_LUO_MODEL = "Helsinki-NLP/opus-mt-en-luo"
LUO_TO_EN_MODEL = "Helsinki-NLP/opus-mt-luo-en"


@lru_cache(maxsize=1)
def _load_en_to_luo():
    from transformers import MarianMTModel, MarianTokenizer
    tokenizer = MarianTokenizer.from_pretrained(EN_TO_LUO_MODEL)
    model = MarianMTModel.from_pretrained(EN_TO_LUO_MODEL)
    model.eval()
    return tokenizer, model


@lru_cache(maxsize=1)
def _load_luo_to_en():
    from transformers import MarianMTModel, MarianTokenizer
    tokenizer = MarianTokenizer.from_pretrained(LUO_TO_EN_MODEL)
    model = MarianMTModel.from_pretrained(LUO_TO_EN_MODEL)
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
        logger.error("Luo translation error: %s", e)
        return text


def luo_to_english(text: str) -> str:
    return _translate(text, _load_luo_to_en)


def english_to_luo(text: str) -> str:
    return _translate(text, _load_en_to_luo)


def is_available() -> bool:
    try:
        _load_luo_to_en()
        _load_en_to_luo()
        return True
    except Exception as e:
        logger.warning("Luo translator not available: %s", e)
        return False
