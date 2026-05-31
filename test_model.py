"""Test the fine-tuned MAMA model via the live API. Run: python test_model.py"""
import urllib.request, urllib.error, json, sys

BASE = "https://mama-lens-ai.onrender.com"

def request(method, path, data=None, token=None):
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# ── Login ──────────────────────────────────────────────────────────────────
status, body = request("POST", "/api/v1/auth/login", {
    "identifier": "+25470214191", "password": "Test1234!"
})
if status != 200:
    print(f"Login failed [{status}]: {body}")
    sys.exit(1)
token = body["access_token"]
print("Logged in OK\n")

# ── Test prompts ───────────────────────────────────────────────────────────
prompts = [
    ("Hello, I am 28 weeks pregnant",               "en", 28),
    ("What should I eat during pregnancy?",          "en", None),
    ("Ninajisikia huzuni sana leo",                  "sw", None),
    ("I have a severe headache and blurred vision",  "en", 32),
    ("I am bleeding heavily",                        "en", None),
    ("Mtoto wangu hasogei",                          "sw", 30),
]

for i, (msg, lang, weeks) in enumerate(prompts, 1):
    payload = {"message": msg, "language": lang, "session_id": "model-test"}
    if weeks:
        payload["gestational_age_weeks"] = weeks

    status, r = request("POST", "/api/v1/avatar/chat", payload, token)
    print(f"[{i}] {msg}")
    if status != 200:
        print(f"    ERROR {status}: {r}\n")
        continue
    print(f"    MAMA     : {r['text_response']}")
    print(f"    Intent   : {r['intent']}  |  Emergency: {r['is_emergency']}  |  Emotion: {r['emotion_detected']}\n")
