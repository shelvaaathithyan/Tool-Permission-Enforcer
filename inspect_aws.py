import boto3
import json

region = "ap-south-1"
ecs = boto3.client("ecs", region_name=region)
ec2 = boto3.client("ec2", region_name=region)
elbv2 = boto3.client("elbv2", region_name=region)
s3 = boto3.client("s3", region_name=region)
cf = boto3.client("cloudfront", region_name=region)
rds = boto3.client("rds", region_name=region)
iam = boto3.client("iam", region_name=region)
sm = boto3.client("secretsmanager", region_name=region)

print("=" * 60)
print("1. ECS CLUSTER")
print("=" * 60)
clusters = ecs.describe_clusters(clusters=["crm-cluster"])["clusters"]
for c in clusters:
    print(f"  Name: {c['clusterName']}")
    print(f"  Status: {c['status']}")
    print(f"  Running Tasks: {c['runningTasksCount']}")
    print(f"  Pending Tasks: {c['pendingTasksCount']}")

print()
print("=" * 60)
print("2. ECS SERVICE")
print("=" * 60)
svcs = ecs.describe_services(cluster="crm-cluster", services=["crm-backend-service"])["services"]
svc = svcs[0]
print(f"  Name: {svc['serviceName']}")
print(f"  Status: {svc['status']}")
print(f"  Desired: {svc['desiredCount']}")
print(f"  Running: {svc['runningCount']}")
print(f"  Pending: {svc['pendingCount']}")
print(f"  Task Definition: {svc['taskDefinition']}")
print(f"  Launch Type: {svc['launchType']}")
nc = svc.get("networkConfiguration", {}).get("awsvpcConfiguration", {})
subnets = nc.get("subnets", [])
sgs = nc.get("securityGroups", [])
print(f"  Subnets: {subnets}")
print(f"  Security Groups: {sgs}")
print(f"  Assign Public IP: {nc.get('assignPublicIp')}")
print(f"  Load Balancers: {svc.get('loadBalancers', [])}")
for d in svc.get("deployments", []):
    print(f"  Deployment: status={d['status']} taskDef={d['taskDefinition']} desired={d['desiredCount']} running={d['runningCount']}")

print()
print("=" * 60)
print("3. CURRENT PRIMARY TASK DEFINITION")
print("=" * 60)
td_arn = svc["taskDefinition"]
td_resp = ecs.describe_task_definition(taskDefinition=td_arn)["taskDefinition"]
print(f"  Family: {td_resp['family']}")
print(f"  Revision: {td_resp['revision']}")
print(f"  CPU: {td_resp.get('cpu')}")
print(f"  Memory: {td_resp.get('memory')}")
print(f"  Execution Role: {td_resp.get('executionRoleArn')}")
print(f"  Task Role: {td_resp.get('taskRoleArn')}")
for cd in td_resp["containerDefinitions"]:
    print(f"  Container: {cd['name']}")
    print(f"    Image: {cd['image']}")
    ports = cd.get("portMappings", [])
    for p in ports:
        print(f"    Port: {p.get('containerPort')} / {p.get('protocol')}")
    env_names = [e["name"] for e in cd.get("environment", [])]
    print(f"    Env vars (names only): {env_names}")
    secret_names = [s["name"] for s in cd.get("secrets", [])]
    print(f"    Secrets (names only): {secret_names}")

print()
print("=" * 60)
print("4. ECS TASK NETWORKING / VPC")
print("=" * 60)
subnet_resp = ec2.describe_subnets(SubnetIds=subnets)
vpc_id = None
for sn in subnet_resp["Subnets"]:
    vpc_id = sn["VpcId"]
    print(f"  Subnet: {sn['SubnetId']} | AZ: {sn['AvailabilityZone']} | VPC: {sn['VpcId']} | CIDR: {sn['CidrBlock']}")
print(f"  VPC ID: {vpc_id}")

print()
print("=" * 60)
print("5. ECS SECURITY GROUP")
print("=" * 60)
sg_resp = ec2.describe_security_groups(GroupIds=sgs)
for sg in sg_resp["SecurityGroups"]:
    print(f"  SG: {sg['GroupId']} | Name: {sg['GroupName']}")
    for rule in sg["IpPermissions"]:
        from_port = rule.get("FromPort", "all")
        to_port = rule.get("ToPort", "all")
        sources = [r["CidrIp"] for r in rule.get("IpRanges", [])]
        sg_sources = [r["GroupId"] for r in rule.get("UserIdGroupPairs", [])]
        print(f"    Inbound: {from_port}-{to_port} | CIDRs: {sources} | SGs: {sg_sources}")

print()
print("=" * 60)
print("6. RDS INSTANCES")
print("=" * 60)
rds_instances = rds.describe_db_instances()["DBInstances"]
for db in rds_instances:
    print(f"  DB: {db['DBInstanceIdentifier']}")
    print(f"    Engine: {db['Engine']} {db.get('EngineVersion')}")
    print(f"    Status: {db['DBInstanceStatus']}")
    print(f"    Endpoint: {db['Endpoint']['Address']}:{db['Endpoint']['Port']}")
    print(f"    VPC: {db.get('DBSubnetGroup', {}).get('VpcId')}")
    rds_sgs = [sg["VpcSecurityGroupId"] for sg in db.get("VpcSecurityGroups", [])]
    print(f"    Security Groups: {rds_sgs}")

print()
print("=" * 60)
print("7. EXISTING ALBs")
print("=" * 60)
albs = elbv2.describe_load_balancers()["LoadBalancers"]
if not albs:
    print("  No ALBs found")
else:
    for alb in albs:
        print(f"  ALB: {alb['LoadBalancerName']} | DNS: {alb['DNSName']} | State: {alb['State']['Code']} | Type: {alb['Type']} | Scheme: {alb['Scheme']}")

print()
print("=" * 60)
print("8. EXISTING TARGET GROUPS")
print("=" * 60)
tgs = elbv2.describe_target_groups()["TargetGroups"]
if not tgs:
    print("  No Target Groups found")
else:
    for tg in tgs:
        print(f"  TG: {tg['TargetGroupName']} | Port: {tg.get('Port')} | Protocol: {tg.get('Protocol')} | TargetType: {tg.get('TargetType')} | VPC: {tg.get('VpcId')}")

print()
print("=" * 60)
print("9. EXISTING S3 BUCKETS")
print("=" * 60)
buckets = s3.list_buckets()["Buckets"]
if not buckets:
    print("  No S3 buckets found")
else:
    for b in buckets:
        print(f"  Bucket: {b['Name']}")

print()
print("=" * 60)
print("10. EXISTING CLOUDFRONT DISTRIBUTIONS")
print("=" * 60)
cf_list = cf.list_distributions()
items = cf_list.get("DistributionList", {}).get("Items", [])
if not items:
    print("  No CloudFront distributions found")
else:
    for d in items:
        print(f"  Distribution: {d['Id']} | Domain: {d['DomainName']} | Status: {d['Status']} | Enabled: {d['Enabled']}")

print()
print("=" * 60)
print("11. VPC SUBNETS (all in ECS VPC)")
print("=" * 60)
if vpc_id:
    all_subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
    for sn in all_subnets:
        print(f"  Subnet: {sn['SubnetId']} | AZ: {sn['AvailabilityZone']} | CIDR: {sn['CidrBlock']} | MapPublicIp: {sn.get('MapPublicIpOnLaunch')}")

print()
print("=" * 60)
print("12. SECRETS MANAGER")
print("=" * 60)
try:
    secrets = sm.list_secrets()["SecretList"]
    for s in secrets:
        print(f"  Secret: {s['Name']} | ARN: {s['ARN']}")
except Exception as e:
    print(f"  Error listing secrets: {e}")

print()
print("INSPECTION COMPLETE")
