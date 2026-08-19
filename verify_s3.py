import requests

S3_URL = "http://crm-frontend-058264313583-ap-south-1.s3-website.ap-south-1.amazonaws.com"

print("=" * 60)
print("S3 FRONTEND VERIFICATION")
print("=" * 60)

# Test 1: GET /
print("\n1. GET /")
try:
    r = requests.get(S3_URL + "/", timeout=10)
    print("   Status:", r.status_code)
    print("   Contains 'index.html' content:", "<!DOCTYPE" in r.text or "<html" in r.text or "<div" in r.text)
except Exception as e:
    print("   ERROR:", e)

# Test 2: GET /index.html
print("\n2. GET /index.html")
try:
    r = requests.get(S3_URL + "/index.html", timeout=10)
    print("   Status:", r.status_code)
except Exception as e:
    print("   ERROR:", e)

# Test 3: SPA routing - GET /login
print("\n3. GET /login (SPA routing)")
try:
    r = requests.get(S3_URL + "/login", timeout=10)
    print("   Status:", r.status_code)
    print("   Returns index.html:", "<!DOCTYPE" in r.text or "<html" in r.text or "<div" in r.text)
except Exception as e:
    print("   ERROR:", e)

# Test 4: SPA routing - GET /customers
print("\n4. GET /customers (SPA routing)")
try:
    r = requests.get(S3_URL + "/customers", timeout=10)
    print("   Status:", r.status_code)
except Exception as e:
    print("   ERROR:", e)

# Test 5: SPA routing - GET /ai-assistant
print("\n5. GET /ai-assistant (SPA routing)")
try:
    r = requests.get(S3_URL + "/ai-assistant", timeout=10)
    print("   Status:", r.status_code)
except Exception as e:
    print("   ERROR:", e)

# Test 6: Check no localhost in served JS
print("\n6. Check JS bundle for localhost:8000")
try:
    r = requests.get(S3_URL + "/assets/index-oc6CT5XY.js", timeout=10)
    print("   Status:", r.status_code)
    print("   Contains localhost:8000:", "localhost:8000" in r.text)
    print("   Contains ALB URL:", "crm-backend-alb" in r.text)
except Exception as e:
    print("   ERROR:", e)

# Test 7: Backend still accessible through ALB
print("\n7. Backend health check through ALB")
ALB = "http://crm-backend-alb-1047061765.ap-south-1.elb.amazonaws.com"
try:
    r = requests.get(ALB + "/health", timeout=10)
    print("   Status:", r.status_code, "Body:", r.json())
except Exception as e:
    print("   ERROR:", e)

print("\n" + "=" * 60)
print("FRONTEND URL:")
print(S3_URL)
print("=" * 60)
