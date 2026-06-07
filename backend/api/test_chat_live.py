import urllib.request, json

base = "https://briangithinji-mama-lens-ai.hf.space"

# Send first message
def chat(session_id, message):
    payload = json.dumps({
        "session_id": session_id,
        "message": message,
        "language": "en",
        "channel": "app"
    }).encode()
    req = urllib.request.Request(
        f"{base}/api/v1/avatar/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:300]}
    except Exception as e:
        return {"error": str(e)}

sid = "debug-session-001"
print("=== Turn 1 ===")
r1 = chat(sid, "I have a headache")
print(json.dumps(r1, indent=2))

print("\n=== Turn 2 ===")
r2 = chat(sid, "started yesterday")
print(json.dumps(r2, indent=2))
