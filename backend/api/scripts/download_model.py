"""Pre-download the MAMA flan-t5 model to HF cache at build time."""
import os, sys

model_id = os.environ.get("HF_MODEL_ID", "BrianGithinji/mama-flan-t5").strip()
cache_dir = os.environ.get("HF_HOME", "/tmp/hf_cache")

print(f"Downloading {model_id} -> {cache_dir}", flush=True)

try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
    AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=cache_dir)
    print("MAMA model cached successfully.", flush=True)
except Exception as e:
    print(f"WARNING: model download failed: {e}", flush=True)
    print("Server will use rule-based fallback on first request.", flush=True)
    sys.exit(0)  # Don't fail the build — fallback is available
