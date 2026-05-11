"""Test risk assessment against live Render API"""
import urllib.request, urllib.error, json, time

BASE = "https://mama-lens-ai.onrender.com"  # production

def post(path, data, token=None):
    b = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=b, headers=headers, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {"error": str(e)}

def get(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers)
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# 1. Register
phone = f"+2547{int(time.time()) % 10000000:07d}"
s, b = post("/api/v1/auth/register", {
    "first_name": "Test", "last_name": "Risk",
    "phone_number": phone, "password": "Test1234!",
    "data_consent_given": True
})
print(f"Register [{s}]:", "OK" if s == 201 else b)
token = b.get("access_token", "")

# 2. Risk assessment
s, b = post("/api/v1/risk/assess", {
    "age": 28, "gestational_age_weeks": 28,
    "systolic_bp": 118, "diastolic_bp": 76,
    "blood_glucose": 88, "heart_rate": 82,
    "hemoglobin": 11.5, "weight_kg": 65, "height_cm": 162,
    "previous_miscarriages": 0, "stress_level": 4,
    "nutrition_status": "good", "language": "sw"
}, token=token)
print(f"Risk Assessment [{s}]:")
if s == 201:
    print(f"  risk_level: {b.get('overall_risk_level')}")
    print(f"  risk_score: {b.get('overall_risk_score')}")
    print(f"  is_emergency: {b.get('is_emergency')}")
    print(f"  recommendations: {len(b.get('recommendations', []))} items")
else:
    print(f"  ERROR: {json.dumps(b)[:500]}")
