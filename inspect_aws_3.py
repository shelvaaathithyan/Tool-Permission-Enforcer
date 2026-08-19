import boto3

region = "ap-south-1"
iam = boto3.client("iam", region_name=region)

# Check what policies are attached to tool-permission-enforcer-cli
print("=" * 60)
print("IAM USER: tool-permission-enforcer-cli")
print("=" * 60)

try:
    # Attached managed policies
    policies = iam.list_attached_user_policies(UserName="tool-permission-enforcer-cli")["AttachedPolicies"]
    print("Attached Managed Policies:")
    for p in policies:
        print(f"  {p['PolicyName']} | ARN: {p['PolicyArn']}")
except Exception as e:
    print(f"  Cannot list attached policies: {e}")

try:
    # Inline policies
    inline = iam.list_user_policies(UserName="tool-permission-enforcer-cli")["PolicyNames"]
    print(f"Inline Policies: {inline}")
    for pname in inline:
        doc = iam.get_user_policy(UserName="tool-permission-enforcer-cli", PolicyName=pname)
        import json
        print(f"  Policy {pname}:")
        print(f"    {json.dumps(doc['PolicyDocument'], indent=2)}")
except Exception as e:
    print(f"  Cannot list inline policies: {e}")

print()
print("=" * 60)
print("PERMISSION TESTS")
print("=" * 60)

# Test S3 create bucket
s3 = boto3.client("s3", region_name=region)
test_bucket = "crm-frontend-058264313583-ap-south-1"
try:
    s3.head_bucket(Bucket=test_bucket)
    print(f"S3 head_bucket({test_bucket}): EXISTS")
except Exception as e:
    err_code = getattr(e, "response", {}).get("Error", {}).get("Code", "?")
    print(f"S3 head_bucket({test_bucket}): {err_code}")

# Test elbv2 create
elbv2 = boto3.client("elbv2", region_name=region)
try:
    albs = elbv2.describe_load_balancers()["LoadBalancers"]
    print(f"ELBv2 describe_load_balancers: OK ({len(albs)} ALBs)")
except Exception as e:
    print(f"ELBv2 describe_load_balancers: DENIED")

# Test CloudFront
cf = boto3.client("cloudfront", region_name=region)
try:
    cf.list_distributions()
    print("CloudFront list_distributions: OK")
except Exception as e:
    print(f"CloudFront list_distributions: DENIED")

print()
print("DONE")
