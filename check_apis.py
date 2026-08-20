import requests
import json

ALB = "http://crm-backend-alb-1047061765.ap-south-1.elb.amazonaws.com"
LOGIN_URL = f"{ALB}/api/v1/auth/login"

r_login = requests.post(LOGIN_URL, data={"username": "admin@example.com", "password": "demo123"})
if r_login.status_code != 200:
    print("Login failed:", r_login.text)
    exit(1)

token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("1. /api/v1/admin/dashboard-stats")
r1 = requests.get(f"{ALB}/api/v1/admin/dashboard-stats", headers=headers)
print("Status:", r1.status_code)
print("Body:", json.dumps(r1.json(), indent=2)[:500])

print("\n2. /api/v1/crm/customers?page=1&page_size=5")
r2 = requests.get(f"{ALB}/api/v1/crm/customers?page=1&page_size=5", headers=headers)
print("Status:", r2.status_code)
print("Body keys:", list(r2.json().keys()))

print("\n3. /api/v1/admin/users")
r3 = requests.get(f"{ALB}/api/v1/admin/users", headers=headers)
print("Status:", r3.status_code)
if isinstance(r3.json(), list):
    print("Body length:", len(r3.json()))
    if len(r3.json()) > 0:
        print("First item keys:", list(r3.json()[0].keys()))
else:
    print("Body:", r3.json())
