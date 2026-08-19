import boto3

ecs = boto3.client("ecs", region_name="ap-south-1")

tg_arn = "arn:aws:elasticloadbalancing:ap-south-1:058264313583:targetgroup/crm-backend-tg/bc312a2f3fb370ed"

try:
    resp = ecs.update_service(
        cluster="crm-cluster",
        service="crm-backend-service",
        loadBalancers=[{
            "targetGroupArn": tg_arn,
            "containerName": "crm-backend",
            "containerPort": 8000
        }],
        forceNewDeployment=True
    )
    svc = resp["service"]
    print("Service:", svc["serviceName"])
    print("Status:", svc["status"])
    print("Desired:", svc["desiredCount"])
    print("Load Balancers:", svc["loadBalancers"])
    for d in svc.get("deployments", []):
        print("  Deployment: status=%s desired=%s running=%s" % (d["status"], d["desiredCount"], d["runningCount"]))
    print("SUCCESS: Load balancer attached to ECS service")
except Exception as e:
    print("ERROR:", e)
