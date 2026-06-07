from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os, httpx

load_dotenv()
token = os.environ.get("HF_API_TOKEN", "")
model = "BrianGithinji/mama-flan-t5"
prompt = "maternal health: Hello I am 28 weeks pregnant"

print("huggingface_hub version:")
import huggingface_hub; print(huggingface_hub.__version__)

# Test 1: text2text_generation
print("\nTest 1: text2text_generation")
try:
    c = InferenceClient(model=model, token=token)
    r = c.text2text_generation(prompt, max_new_tokens=50)
    print("OK:", repr(r))
except Exception as e:
    print("FAIL:", e)

# Test 2: httpx direct to api-inference
print("\nTest 2: httpx api-inference.huggingface.co")
try:
    resp = httpx.post(
        f"https://api-inference.huggingface.co/models/{model}",
        json={"inputs": prompt, "parameters": {"max_new_tokens": 50}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    print(resp.status_code, resp.text[:300])
except Exception as e:
    print("FAIL:", e)

# Test 3: httpx router models (no suffix)
print("\nTest 3: router.huggingface.co/hf-inference/models")
try:
    resp = httpx.post(
        f"https://router.huggingface.co/hf-inference/models/{model}",
        json={"inputs": prompt, "parameters": {"max_new_tokens": 50}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    print(resp.status_code, resp.text[:300])
except Exception as e:
    print("FAIL:", e)
