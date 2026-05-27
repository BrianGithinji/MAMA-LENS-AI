"""
Run this ONCE locally to upload your fine-tuned MAMA model to HuggingFace Hub.

Usage:
    cd ai/mama_model
    pip install huggingface_hub
    python upload_to_hub.py

You need a HuggingFace account and write token from:
    https://huggingface.co/settings/tokens
"""

from huggingface_hub import HfApi, login
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "mama-flan-t5"
REPO_ID = "BrianGithinji/mama-flan-t5"   # change username if needed

def main():
    print("=== MAMA-LENS AI — Upload fine-tuned model to HuggingFace Hub ===\n")

    token = input("Paste your HuggingFace WRITE token: ").strip()
    login(token=token)

    api = HfApi()

    # Create repo if it doesn't exist
    try:
        api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True, private=False)
        print(f"Repo ready: https://huggingface.co/{REPO_ID}")
    except Exception as e:
        print(f"Repo creation note: {e}")

    # Upload all files in mama-flan-t5/
    print(f"\nUploading from: {MODEL_DIR}")
    files = list(MODEL_DIR.glob("*"))
    print(f"Files to upload: {[f.name for f in files]}\n")

    for f in files:
        if f.is_file():
            print(f"  Uploading {f.name} ({f.stat().st_size / 1e6:.1f} MB)...")
            api.upload_file(
                path_or_fileobj=str(f),
                path_in_repo=f.name,
                repo_id=REPO_ID,
                repo_type="model",
            )
            print(f"  ✅ {f.name} uploaded")

    print(f"\n✅ Done! Model available at: https://huggingface.co/{REPO_ID}")
    print(f"\nAdd this to Render environment variables:")
    print(f"  HF_MODEL_ID = {REPO_ID}")

if __name__ == "__main__":
    main()
