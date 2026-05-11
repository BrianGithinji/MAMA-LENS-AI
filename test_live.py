import urllib.request, urllib.error, json, time

BASE = "https://mama-lens-ai.onrender.com"
phone = f"+2547{int(time.time()) % 10000000:07d}"

def post(path, data):
    b = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=b,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {"error": str(e)}

print(f"Phone: {phone}")

# 1. Register
s, b = post("/api/v1/auth/register", {
    "first_name": "Test", "last_name": "User",
    "phone_number": phone, "password": "Test1234!",
    "data_consent_given": True
})
print(f"REGISTER [{s}]: {json.dumps(b)[:300]}")

# 2. Login with phone
s, b = post("/api/v1/auth/login", {"identifier": phone, "password": "Test1234!"})
print(f"LOGIN    [{s}]: {json.dumps(b)[:300]}")

# 3. Login with wrong password
s, b = post("/api/v1/auth/login", {"identifier": phone, "password": "wrongpass"})
print(f"WRONG PW [{s}]: {json.dumps(b)[:200]}")
