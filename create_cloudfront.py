import boto3
import json
import time

cf = boto3.client("cloudfront")
s3 = boto3.client("s3", region_name="ap-south-1")
bucket = "crm-frontend-058264313583-ap-south-1"

# Step 1: Create Origin Access Control
print("Creating Origin Access Control...")
try:
    oac_resp = cf.create_origin_access_control(
        OriginAccessControlConfig={
            "Name": "crm-frontend-oac",
            "Description": "OAC for CRM frontend S3 bucket",
            "SigningProtocol": "sigv4",
            "SigningBehavior": "always",
            "OriginAccessControlOriginType": "s3"
        }
    )
    oac_id = oac_resp["OriginAccessControl"]["Id"]
    print("OAC ID:", oac_id)
except Exception as e:
    if "already exists" in str(e).lower():
        # List OACs and find ours
        oacs = cf.list_origin_access_controls()["OriginAccessControlList"]["Items"]
        oac_id = next(o["Id"] for o in oacs if o["Name"] == "crm-frontend-oac")
        print("OAC already exists:", oac_id)
    else:
        print("OAC ERROR:", e)
        raise

# Step 2: Create CloudFront Distribution
print("Creating CloudFront distribution...")
origin_domain = "%s.s3.ap-south-1.amazonaws.com" % bucket

dist_config = {
    "CallerReference": "crm-frontend-%d" % int(time.time()),
    "Comment": "CRM Frontend Distribution",
    "DefaultRootObject": "index.html",
    "Enabled": True,
    "Origins": {
        "Quantity": 1,
        "Items": [{
            "Id": "S3-crm-frontend",
            "DomainName": origin_domain,
            "OriginAccessControlId": oac_id,
            "S3OriginConfig": {
                "OriginAccessIdentity": ""
            }
        }]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-crm-frontend",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",  # CachingOptimized
        "Compress": True,
        "ForwardedValues": None
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            },
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            }
        ]
    },
    "PriceClass": "PriceClass_200",
    "ViewerCertificate": {
        "CloudFrontDefaultCertificate": True,
        "MinimumProtocolVersion": "TLSv1.2_2021"
    },
    "HttpVersion": "http2"
}

# Remove ForwardedValues since we're using CachePolicyId
del dist_config["DefaultCacheBehavior"]["ForwardedValues"]

try:
    dist_resp = cf.create_distribution(DistributionConfig=dist_config)
    dist = dist_resp["Distribution"]
    dist_id = dist["Id"]
    dist_domain = dist["DomainName"]
    print("Distribution ID:", dist_id)
    print("Distribution Domain:", dist_domain)
    print("Distribution Status:", dist["Status"])
except Exception as e:
    print("DISTRIBUTION ERROR:", e)
    raise

# Step 3: Add S3 bucket policy to allow CloudFront OAC
print()
print("Setting S3 bucket policy for CloudFront OAC...")
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "AllowCloudFrontOAC",
        "Effect": "Allow",
        "Principal": {
            "Service": "cloudfront.amazonaws.com"
        },
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::%s/*" % bucket,
        "Condition": {
            "StringEquals": {
                "AWS:SourceArn": "arn:aws:cloudfront::058264313583:distribution/%s" % dist_id
            }
        }
    }]
}

# Need to temporarily allow bucket policy setting
s3.put_public_access_block(
    Bucket=bucket,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False
    }
)

s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(bucket_policy))
print("Bucket policy set!")

print()
print("SUMMARY:")
print("  OAC_ID:", oac_id)
print("  DISTRIBUTION_ID:", dist_id)
print("  CLOUDFRONT_DOMAIN:", dist_domain)
print("  S3_BUCKET:", bucket)
