import requests

ALB = "http://crm-backend-alb-1047061765.ap-south-1.elb.amazonaws.com"
LOGIN_URL = f"{ALB}/api/v1/auth/login"
CUSTOMERS_URL = f"{ALB}/api/v1/crm/customers?page=1&page_size=50"
USERS_URL = f"{ALB}/api/v1/admin/users"

print("Logging in as admin@example.com to verify seeded data...")
r_login = requests.post(LOGIN_URL, data={"username": "admin@example.com", "password": "demo123"})
if r_login.status_code != 200:
    print("Login failed:", r_login.text)
    exit(1)

token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Fetching customers...")
r_cust = requests.get(CUSTOMERS_URL, headers=headers)
if r_cust.status_code == 200:
    cust_data = r_cust.json()
    print(f"Total customers returned by API: {cust_data.get('total')}")
else:
    print(f"Failed to fetch customers: {r_cust.status_code} {r_cust.text}")

print("Fetching users (Admin endpoint)...")
r_users = requests.get(USERS_URL, headers=headers)
if r_users.status_code == 200:
    users_data = r_users.json()
    print(f"Total users returned by API: {len(users_data)}")
else:
    print(f"Failed to fetch users: {r_users.status_code} {r_users.text}")

print("Verification complete.")
