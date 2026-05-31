"""
MAMA-LENS AI — Fine-tuning pipeline for google/flan-t5-base
Model: google/flan-t5-base (247M params, runs on CPU, Python 3.11 compatible)
Task: Seq2Seq text generation for maternal health Q&A
Languages: English, Swahili, Maasai (Maa), Luo (Dholuo), Kikuyu (Gikuyu)

Primary dataset: MOTHER (Maternal Online Technology for Health Care)
  - 503 validated Q&A pairs from rural/semi-urban Uganda
  - Medical personnel validated answers
  - Harvard Dataverse: https://doi.org/10.7910/DVN/EZLCH3
  - Download CSV and place at: ai/mama_model/mother_dataset/MOTHER_dataset.csv

Supplementary dataset: training_data.json (local multilingual pairs)

Usage:
    python finetune.py                    # train
    python finetune.py --epochs 5         # more epochs
    python finetune.py --output ./mama-flan-t5  # custom output dir
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_MODEL = "google/flan-t5-base"
DATA_FILE = Path(__file__).parent / "training_data.json"
MOTHER_DIR = Path(__file__).parent / "mother_dataset"
DEFAULT_OUTPUT = Path(__file__).parent / "mama-flan-t5"


def _load_mother_dataset() -> List[Dict[str, str]]:
    """
    Load the MOTHER dataset from Harvard Dataverse files.
    Extracts from two sources and merges:
      1. mother_question_and_answer_pairs_data.json  — 501 direct Q&A pairs
      2. mother_intents_patterns_responses_data.json — intents with multiple
         pattern/response variants (expands training coverage significantly)
    """
    if not MOTHER_DIR.exists():
        return []

    records: List[Dict[str, str]] = []

    # ── Source 1: direct Q&A pairs ─────────────────────────────────────────
    qa_path = MOTHER_DIR / "mother_question_and_answer_pairs_data.json"
    if qa_path.exists():
        with open(qa_path, encoding="utf-8") as f:
            qa_data = json.load(f)
        for item in qa_data:
            q = item.get("question", "").strip()
            a = item.get("answer", "").strip()
            if q and a:
                records.append({"input": f"maternal health: {q}", "output": a})
        logger.info("Loaded %d Q&A pairs from %s", len(records), qa_path.name)

    # ── Source 2: intents with pattern/response variants ───────────────────
    intents_path = MOTHER_DIR / "mother_intents_patterns_responses_data.json"
    if intents_path.exists():
        with open(intents_path, encoding="utf-8") as f:
            intents_data = json.load(f)
        intents_list = intents_data.get("intents", [])
        extra = 0
        for intent in intents_list:
            patterns = intent.get("patterns", [])
            responses = intent.get("responses", [])
            if not patterns or not responses:
                continue
            # Pair each pattern with the first (canonical) response
            canonical = responses[0]
            for pattern in patterns:
                p = pattern.strip()
                if p:
                    records.append({"input": f"maternal health: {p}", "output": canonical})
                    extra += 1
        logger.info("Loaded %d pattern→response pairs from %s", extra, intents_path.name)

    return records


def load_all_data() -> List[Dict[str, str]]:
    """Merge MOTHER dataset + local multilingual training_data.json."""
    mother = _load_mother_dataset()
    with open(DATA_FILE, encoding="utf-8") as f:
        local = json.load(f)

    combined = mother + local
    logger.info(
        "Dataset: %d MOTHER + %d local = %d total examples",
        len(mother), len(local), len(combined)
    )
    return combined


def finetune(epochs: int = 3, output_dir: Path = DEFAULT_OUTPUT) -> None:
    from datasets import Dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForSeq2SeqLM,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        DataCollatorForSeq2Seq,
    )

    logger.info("Loading base model: %s", BASE_MODEL)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)

    raw = load_all_data()
    logger.info("Total training examples: %d", len(raw))

    dataset = Dataset.from_list(raw)

    def tokenize(batch):
        model_inputs = tokenizer(
            batch["input"],
            max_length=256,
            truncation=True,
            padding="max_length",
        )
        labels = tokenizer(
            batch["output"],
            max_length=256,
            truncation=True,
            padding="max_length",
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = dataset.map(tokenize, batched=True, remove_columns=["input", "output"])

    args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=4,
        learning_rate=3e-4,
        warmup_steps=20,
        weight_decay=0.01,
        logging_steps=20,
        save_strategy="steps",
        save_steps=100,
        predict_with_generate=True,
        fp16=False,       # CPU-safe
        use_cpu=True,     # set False if GPU available
        report_to="none",
    )

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        data_collator=collator,
        processing_class=tokenizer,
    )

    logger.info("Starting fine-tuning for %d epochs...", epochs)
    trainer.train()

    model.config.tie_word_embeddings = False
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    logger.info("Model saved to: %s", output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune MAMA flan-t5 model")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    finetune(epochs=args.epochs, output_dir=Path(args.output))
