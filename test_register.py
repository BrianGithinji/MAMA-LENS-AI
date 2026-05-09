"""
MAMA-LENS AI — Full Auth Flow Test
Tests: register → verify OTP → login → get profile → risk assessment
"""
import urllib.request
import urllib.error
import json
import time

BASE = "http://127.0.0.1:8002"
PHONE = f"+2547110{int(time.time()) % 100000:05d}"  # unique phone each run

def req(method, path, data=None, token=None):
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=15)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

print("=" * 55)
print("  MAMA-LENS AI — Backend Integration Test")
print("=" * 55)
print(f"  Using phone: {PHONE}")

# 1. Health
s, b = req("GET", "/health")
print(f"\n[1] Health Check .............. {s} {'✅' if s==200 else '❌'}")

# 2. Register
s, b = req("POST", "/api/v1/auth/register", {
    "first_name": "Amina",
    "last_name": "Wanjiku",
    "phone_number": PHONE,
    "password": "Mama2026!",
    "data_consent_given": True,
    "preferred_language": "sw",
    "country": "Kenya"
})
print(f"[2] Register .................. {s} {'✅' if s==201 else '❌'}")
if s == 201:
    user_id = b["user_id"]
    access_token = b["access_token"]
    refresh_token = b["refresh_token"]
    print(f"    user_id: {user_id[:8]}...")
    print(f"    token:   {access_token[:20]}...")
    print(f"    status:  active (no OTP required)")
else:
    print(f"    ERROR: {b}")
    exit(1)

# 3. Skipped — no OTP verification required
print(f"[3] OTP Verification .......... SKIPPED ✅ (removed by design)")

# 4. Get profile
s, b = req("GET", "/api/v1/users/me", token=access_token)
print(f"[4] Get Profile ............... {s} {'✅' if s==200 else '❌'}")
if s == 200:
    print(f"    name: {b['first_name']} {b['last_name']}")
    print(f"    role: {b['role']}")
    print(f"    status: {b['status']}")

# 5. Create pregnancy profile
s, b = req("POST", "/api/v1/pregnancy/", {
    "status": "pregnant",
    "gestational_age_weeks": 28,
    "gravida": 2,
    "para": 1,
    "previous_miscarriages": 0
}, token=access_token)
print(f"[5] Create Pregnancy .......... {s} {'✅' if s==201 else '❌'}")
if s == 201:
    print(f"    profile_id: {b['id'][:8]}...")

# 6. Risk assessment
s, b = req("POST", "/api/v1/risk/assess", {
    "age": 28,
    "gestational_age_weeks": 28,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "blood_glucose": 88,
    "heart_rate": 82,
    "hemoglobin": 11.5,
    "weight_kg": 65,
    "height_cm": 162,
    "previous_miscarriages": 0,
    "stress_level": 4,
    "nutrition_status": "good",
    "language": "sw"
}, token=access_token)
print(f"[6] Risk Assessment ........... {s} {'✅' if s==201 else '❌'}")
if s == 201:
    print(f"    risk_level: {b['overall_risk_level']}")
    print(f"    risk_score: {b['overall_risk_score']:.2f}")
    print(f"    is_emergency: {b['is_emergency']}")
    print(f"    recommendations: {len(b['recommendations'])} items")
else:
    print(f"    ERROR: {b}")

# 7. Find nearby facilities
s, b = req("GET", "/api/v1/facilities/nearby?latitude=-1.2921&longitude=36.8219&radius_km=50")
print(f"[7] Nearby Facilities ......... {s} {'✅' if s==200 else '❌'}")
if s == 200:
    print(f"    found: {len(b)} facilities")
    if b:
        print(f"    nearest: {b[0]['name']} ({b[0]['distance_km']} km)")

# 8. Login
s, b = req("POST", "/api/v1/auth/login", {
    "identifier": PHONE,
    "password": "Mama2026!"
})
print(f"[8] Login ..................... {s} {'✅' if s==200 else '❌'}")
if s == 200:
    print(f"    new token: {b['access_token'][:20]}...")

# 9. Danger signs education
s, b = req("GET", "/api/v1/education/danger-signs?language=sw")
print(f"[9] Danger Signs (Swahili) .... {s} {'✅' if s==200 else '❌'}")
if s == 200:
    print(f"    title: {b['title']}")
    print(f"    signs: {len(b['signs'])} items")

# 10. Log vitals
s, b = req("POST", "/api/v1/health-records/vitals", {
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "heart_rate": 82,
    "hemoglobin": 11.5,
    "weight_kg": 65,
    "source": "manual"
}, token=access_token)
print(f"[10] Log Vitals ............... {s} {'✅' if s==201 else '❌'}")
if s == 201:
    print(f"    is_hypertensive: {b['is_hypertensive']}")
    print(f"    bp_display: {b['bp_display']}")

print("\n" + "=" * 55)
print("  All tests complete!")
print("=" * 55)
