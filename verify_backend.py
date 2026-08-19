import requests
import boto3

ALB_DNS = "crm-backend-alb-1047061765.ap-south-1.elb.amazonaws.com"
BASE = "http://" + ALB_DNS

results = {}

# Test 1: GET /docs
print("1. GET /docs")
try:
    r = requests.get(BASE + "/docs", timeout=10)
    results["docs"] = r.status_code
    print("   Status:", r.status_code)
except Exception as e:
    results["docs"] = "ERROR"
    print("   ERROR:", e)

# Test 2: GET /openapi.json
print("2. GET /openapi.json")
try:
    r = requests.get(BASE + "/openapi.json", timeout=10)
    results["openapi"] = r.status_code
    print("   Status:", r.status_code)
except Exception as e:
    results["openapi"] = "ERROR"
    print("   ERROR:", e)

# Test 3: GET /api/v1/crm/customers
print("3. GET /api/v1/crm/customers?page=1&page_size=20")
try:
    r = requests.get(BASE + "/api/v1/crm/customers?page=1&page_size=20", timeout=10)
    results["customers"] = r.status_code
    data = r.json()
    print("   Status:", r.status_code)
    print("   Total customers:", data.get("total", "N/A"))
except Exception as e:
    results["customers"] = "ERROR"
    print("   ERROR:", e)

# Test 4: POST /api/v1/auth/login
print("4. POST /api/v1/auth/login")
token = None
try:
    r = requests.post(BASE + "/api/v1/auth/login", data={"username": "ravi.s@example.com", "password": "demo123"}, timeout=10)
    results["login"] = r.status_code
    print("   Status:", r.status_code)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("   JWT obtained: YES (not printed)")
    else:
        print("   Body:", r.text[:200])
except Exception as e:
    results["login"] = "ERROR"
    print("   ERROR:", e)

# Test 5: POST /api/v1/agent/invoke
print("5. POST /api/v1/agent/invoke")
if token:
    try:
        r = requests.post(
            BASE + "/api/v1/agent/invoke",
            headers={"Authorization": "Bearer " + token},
            json={"prompt": "who works in XYXY Company?"},
            timeout=30
        )
        results["agent"] = r.status_code
        print("   Status:", r.status_code)
        if r.status_code == 200:
            resp = r.json()
            print("   AI Status:", resp.get("status"))
            print("   Decision:", resp.get("decision"))
            items = resp.get("result", {}).get("items", [])
            print("   Results count:", len(items))
        else:
            print("   Body:", r.text[:200])
    except Exception as e:
        results["agent"] = "ERROR"
        print("   ERROR:", e)
else:
    results["agent"] = "SKIPPED (no token)"
    print("   SKIPPED (login failed)")

# Test 6: ECS Target Health
print("6. ECS Target Health")
elbv2 = boto3.client("elbv2", region_name="ap-south-1")
tg_arn = "arn:aws:elasticloadbalancing:ap-south-1:058264313583:targetgroup/crm-backend-tg/bc312a2f3fb370ed"
health = elbv2.describe_target_health(TargetGroupArn=tg_arn)
for t in health["TargetHealthDescriptions"]:
    state = t["TargetHealth"]["State"]
    ip = t["Target"]["Id"]
    port = t["Target"]["Port"]
    print("   Target %s:%s -> %s" % (ip, port, state))
    results["target_health"] = state

# Test 7: ECS Service Stability
print("7. ECS Service Stability")
ecs = boto3.client("ecs", region_name="ap-south-1")
svcs = ecs.describe_services(cluster="crm-cluster", services=["crm-backend-service"])["services"]
svc = svcs[0]
print("   Service:", svc["serviceName"])
print("   Status:", svc["status"])
print("   Desired:", svc["desiredCount"])
print("   Running:", svc["runningCount"])
print("   Pending:", svc["pendingCount"])
print("   Task Definition:", svc["taskDefinition"].split("/")[-1])
lb = svc.get("loadBalancers", [])
if lb:
    print("   Load Balancer: attached (container %s:%s)" % (lb[0]["containerName"], lb[0]["containerPort"]))
for d in svc.get("deployments", []):
    print("   Deployment: status=%s desired=%s running=%s rollout=%s" % (
        d["status"], d["desiredCount"], d["runningCount"], d.get("rolloutState", "N/A")))
results["ecs_status"] = svc["status"]
results["ecs_desired"] = svc["desiredCount"]
results["ecs_running"] = svc["runningCount"]
results["ecs_pending"] = svc["pendingCount"]

# Summary
print()
print("=" * 50)
print("SUMMARY")
print("=" * 50)
all_pass = True
checks = [
    ("GET /docs", results.get("docs") == 200),
    ("GET /openapi.json", results.get("openapi") == 200),
    ("GET /customers", results.get("customers") == 200),
    ("POST /auth/login", results.get("login") == 200),
    ("POST /agent/invoke", results.get("agent") == 200),
    ("Target health", results.get("target_health") == "healthy"),
    ("ECS stable", results.get("ecs_status") == "ACTIVE" and results.get("ecs_running") == 1 and results.get("ecs_pending") == 0),
]
for name, passed in checks:
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_pass = False
    print("  %s: %s" % (name, status))
print()
print("OVERALL:", "ALL PASS" if all_pass else "SOME FAILURES")
