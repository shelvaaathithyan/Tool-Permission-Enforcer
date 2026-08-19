import boto3

ec2 = boto3.client("ec2", region_name="ap-south-1")

ecs_sg = "sg-041c60f740df52a85"
alb_sg = "sg-0d65d21fc50be5bdc"

# Add inbound rule: TCP 8000 from ALB SG
print("Adding inbound rule: TCP 8000 from ALB SG...")
try:
    ec2.authorize_security_group_ingress(
        GroupId=ecs_sg,
        IpPermissions=[{
            "IpProtocol": "tcp",
            "FromPort": 8000,
            "ToPort": 8000,
            "UserIdGroupPairs": [{"GroupId": alb_sg, "Description": "Allow traffic from ALB"}]
        }]
    )
    print("SUCCESS: Added TCP 8000 from ALB SG to ECS SG")
except Exception as e:
    if "Duplicate" in str(e) or "already exists" in str(e):
        print("Rule already exists, skipping")
    else:
        print("ERROR:", e)

# Verify current rules
print()
print("Current ECS SG inbound rules:")
sg_resp = ec2.describe_security_groups(GroupIds=[ecs_sg])
for rule in sg_resp["SecurityGroups"][0]["IpPermissions"]:
    from_port = rule.get("FromPort", "all")
    to_port = rule.get("ToPort", "all")
    cidrs = [r["CidrIp"] for r in rule.get("IpRanges", [])]
    sgs = [r["GroupId"] for r in rule.get("UserIdGroupPairs", [])]
    print("  Port %s-%s | CIDRs: %s | SGs: %s" % (from_port, to_port, cidrs, sgs))
