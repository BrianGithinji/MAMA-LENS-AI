"""Pre-download the MAMA flan-t5 model to HF cache at build time."""
import os, sys

model_id = os.environ.get("HF_MODEL_ID", "BrianGithinji/mama-flan-t5").strip()
cache_dir = os.environ.get("HF_HOME", "/tmp/hf_cache")
token = os.environ.get("HF_API_TOKEN", "").strip() or None

print(f"Downloading {model_id} -> {cache_dir}", flush=True)

try:
    from transformers import AutoTokenizer, T5ForConditionalGeneration
    AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir, token=token)
    T5ForConditionalGeneration.from_pretrained(model_id, cache_dir=cache_dir, token=token, low_cpu_mem_usage=True)
    print("MAMA model cached successfully.", flush=True)
except Exception as e:
    print(f"WARNING: model download failed: {e}", flush=True)
    sys.exit(0)
