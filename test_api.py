"""Quick API test — run with: .venv311\Scripts\python test_api.py"""
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# 1. Health check
req = urllib.request.Request(f"{BASE}/health")
with urllib.request.urlopen(req, timeout=5) as r:
    print("Health:", json.loads(r.read()))

# 2. Register
status, body = post("/api/v1/auth/register", {
    "first_name": "Jane",
    "last_name": "Doe",
    "phone_number": "+254700000099",
    "password": "Test1234!",
    "data_consent_given": True,
})
print(f"\nRegister [{status}]:", body)
