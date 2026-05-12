"""
MAMA-LENS AI — Luo (Dholuo) Language Translator
Uses facebook/nllb-200-distilled-600M (NLLB-200) for
English <-> Luo (Dholuo) translation.
NLLB-200 lang code: luo_Latn
"""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_ID = "facebook/nllb-200-distilled-600M"
LUO_LANG_CODE = "luo_Latn"
ENGLISH_LANG_CODE = "eng_Latn"


@lru_cache(maxsize=1)
def _load_models():
    """Load translation models once and cache them."""
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
    model.eval()
    return tokenizer, model


def _translate(text: str, src_lang: str, tgt_lang: str) -> str:
    try:
        import torch
        tokenizer, model = _load_models()

        tokenizer.src_lang = src_lang
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

        tgt_lang_id = tokenizer.lang_code_to_id.get(tgt_lang) or tokenizer.convert_tokens_to_ids(tgt_lang)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_new_tokens=512,
                num_beams=4,
                early_stopping=True,
            )

        return tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        logger.error("Luo translation error (%s->%s): %s", src_lang, tgt_lang, e)
        return text


def luo_to_english(text: str) -> str:
    """Translate Luo (Dholuo) text to English."""
    return _translate(text, src_lang=LUO_LANG_CODE, tgt_lang=ENGLISH_LANG_CODE)


def english_to_luo(text: str) -> str:
    """Translate English text to Luo (Dholuo)."""
    return _translate(text, src_lang=ENGLISH_LANG_CODE, tgt_lang=LUO_LANG_CODE)


def is_available() -> bool:
    """Check if the translation model can be loaded."""
    try:
        _load_models()
        return True
    except Exception as e:
        logger.warning("Luo translator not available: %s", e)
        return False
