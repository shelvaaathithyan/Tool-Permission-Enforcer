import requests
import json

ALB_DNS = "crm-backend-alb-1047061765.ap-south-1.elb.amazonaws.com"
BASE = "http://" + ALB_DNS

print("=" * 60)
print("BACKEND VERIFICATION THROUGH ALB")
print("=" * 60)

# Test 1: /docs
print("\n1. GET /docs")
r = requests.get(BASE + "/docs", timeout=10)
print("   Status:", r.status_code)

# Test 2: /openapi.json
print("\n2. GET /openapi.json")
r = requests.get(BASE + "/openapi.json", timeout=10)
print("   Status:", r.status_code)

# Test 3: /health
print("\n3. GET /health")
r = requests.get(BASE + "/health", timeout=10)
print("   Status:", r.status_code, "Body:", r.json())

# Test 4: /api/v1/crm/customers
print("\n4. GET /api/v1/crm/customers?page=1&page_size=20")
r = requests.get(BASE + "/api/v1/crm/customers?page=1&page_size=20", timeout=10)
print("   Status:", r.status_code)
data = r.json()
print("   Total customers:", data.get("total", "N/A"))

# Test 5: Auth login
print("\n5. POST /api/v1/auth/login")
r = requests.post(BASE + "/api/v1/auth/login", data={"username": "ravi.s@example.com", "password": "demo123"}, timeout=10)
print("   Status:", r.status_code)
if r.status_code == 200:
    token = r.json()["access_token"]
    print("   JWT obtained: YES (not printing)")

    # Test 6: Agent invoke
    print("\n6. POST /api/v1/agent/invoke")
    r2 = requests.post(
        BASE + "/api/v1/agent/invoke",
        headers={"Authorization": "Bearer " + token},
        json={"prompt": "who works in XYXY Company?"},
        timeout=30
    )
    print("   Status:", r2.status_code)
    if r2.status_code == 200:
        resp = r2.json()
        print("   AI Status:", resp.get("status"))
        print("   Decision:", resp.get("decision"))
        items = resp.get("result", {}).get("items", [])
        print("   Results count:", len(items))
    else:
        print("   Body:", r2.text[:200])
else:
    print("   Login failed:", r.text[:200])

print("\n" + "=" * 60)
print("ALB VERIFICATION COMPLETE")
print("=" * 60)
