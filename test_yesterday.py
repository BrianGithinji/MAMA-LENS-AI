import urllib.request, urllib.error, json, sys

BASE = "https://briangithinji-mama-lens-ai.hf.space"

def post(path, data, token=None):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()}

b = post("/api/v1/auth/login", {"identifier": "+25470214191", "password": "Test1234!"})
token = b.get("access_token")
print("Logged in OK\n")

turns = [
    ("I have a headache", "en"),
    ("yesterday", "en"),
    ("yes it is getting worse", "en"),
]

for msg, lang in turns:
    r = post("/api/v1/avatar/chat", {"message": msg, "language": lang, "session_id": "yesterday-flow"}, token)
    resp = r.get("text_response", r.get("error", "no response"))
    print(f"User  : {msg}")
    print(f"MAMA  : {resp[:200]}")
    print(f"Intent: {r.get('intent','?')}\n")
