"""Pre-download the MAMA flan-t5 model files to HF cache at build time.
Downloads files only — does not load weights into memory (avoids safetensors bug).
"""
import os, sys

model_id = os.environ.get("HF_MODEL_ID", "BrianGithinji/mama-flan-t5").strip()
cache_dir = os.environ.get("HF_HOME", "/tmp/hf_cache")
token = os.environ.get("HF_API_TOKEN", "").strip() or None

print(f"Downloading {model_id} -> {cache_dir}", flush=True)

try:
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id=model_id,
        cache_dir=cache_dir,
        token=token,
        ignore_patterns=["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
    )
    print("MAMA model files downloaded successfully.", flush=True)
except Exception as e:
    print(f"WARNING: model download failed: {e}", flush=True)
    sys.exit(0)
