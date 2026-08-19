import boto3

region = "ap-south-1"
ec2 = boto3.client("ec2", region_name=region)
cf = boto3.client("cloudfront", region_name=region)
sm = boto3.client("secretsmanager", region_name=region)
s3 = boto3.client("s3", region_name=region)

# Check RDS security group
print("=" * 60)
print("RDS SECURITY GROUP (sg-03e040eb9cd959f07)")
print("=" * 60)
sg_resp = ec2.describe_security_groups(GroupIds=["sg-03e040eb9cd959f07"])
for sg in sg_resp["SecurityGroups"]:
    print(f"  SG: {sg['GroupId']} | Name: {sg['GroupName']}")
    for rule in sg["IpPermissions"]:
        from_port = rule.get("FromPort", "all")
        to_port = rule.get("ToPort", "all")
        sources = [r["CidrIp"] for r in rule.get("IpRanges", [])]
        sg_sources = [r["GroupId"] for r in rule.get("UserIdGroupPairs", [])]
        print(f"    Inbound: {from_port}-{to_port} | CIDRs: {sources} | SGs: {sg_sources}")

# Check CloudFront
print()
print("=" * 60)
print("CLOUDFRONT DISTRIBUTIONS")
print("=" * 60)
try:
    cf_list = cf.list_distributions()
    items = cf_list.get("DistributionList", {}).get("Items", [])
    if not items:
        print("  No CloudFront distributions found")
    else:
        for d in items:
            print(f"  Distribution: {d['Id']} | Domain: {d['DomainName']} | Status: {d['Status']}")
except Exception as e:
    print(f"  Error: {e}")

# Check S3 - try to access a specific bucket
print()
print("=" * 60)
print("S3 BUCKETS (trying specific names)")
print("=" * 60)
for name in ["crm-frontend-058264313583-ap-south-1", "crm-frontend", "crm-frontend-prod"]:
    try:
        s3.head_bucket(Bucket=name)
        print(f"  EXISTS: {name}")
    except Exception as e:
        err_code = getattr(e, "response", {}).get("Error", {}).get("Code", "Unknown")
        if err_code == "404":
            print(f"  NOT FOUND: {name}")
        elif err_code == "403":
            print(f"  EXISTS (no access): {name}")
        else:
            print(f"  {name}: {err_code} - {e}")

# Secrets Manager
print()
print("=" * 60)
print("SECRETS MANAGER")
print("=" * 60)
try:
    secrets = sm.list_secrets()["SecretList"]
    for s_item in secrets:
        print(f"  Secret: {s_item['Name']} | ARN: {s_item['ARN']}")
    if not secrets:
        print("  No secrets found")
except Exception as e:
    print(f"  Error: {e}")

# Check Internet Gateway for VPC
print()
print("=" * 60)
print("INTERNET GATEWAY")
print("=" * 60)
igws = ec2.describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": ["vpc-07591541292b69c42"]}])
for igw in igws["InternetGateways"]:
    print(f"  IGW: {igw['InternetGatewayId']}")

# Check all subnets in VPC
print()
print("=" * 60)
print("ALL SUBNETS IN VPC")
print("=" * 60)
all_subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": ["vpc-07591541292b69c42"]}])["Subnets"]
for sn in all_subnets:
    print(f"  {sn['SubnetId']} | AZ: {sn['AvailabilityZone']} | CIDR: {sn['CidrBlock']} | MapPublicIp: {sn.get('MapPublicIpOnLaunch')}")

print()
print("INSPECTION PART 2 COMPLETE")
