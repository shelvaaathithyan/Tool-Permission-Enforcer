import boto3
import os
import json
import mimetypes

s3 = boto3.client("s3", region_name="ap-south-1")
bucket = "crm-frontend-058264313583-ap-south-1"
dist_dir = r"s:\Tool Permission Enforcer\frontend\dist"

# Step 1: Enable Static Website Hosting
print("1. Enabling S3 Static Website Hosting...")
s3.put_bucket_website(
    Bucket=bucket,
    WebsiteConfiguration={
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "index.html"}
    }
)
print("   Website hosting enabled (index.html / error: index.html)")

# Step 2: Disable Block Public Access (required for website hosting)
print("2. Configuring public access settings...")
s3.put_public_access_block(
    Bucket=bucket,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False
    }
)
print("   Public access block disabled for website hosting")

# Step 3: Set bucket policy for public read
print("3. Setting bucket policy for public read...")
policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::%s/*" % bucket
    }]
}
s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
print("   Bucket policy set (s3:GetObject only)")

# Step 4: Upload dist/ contents
print("4. Uploading dist/ contents to S3...")

# Custom MIME types
mime_overrides = {
    ".html": "text/html",
    ".js": "application/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".eot": "application/vnd.ms-fontobject",
    ".map": "application/json",
    ".txt": "text/plain",
    ".xml": "application/xml",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

uploaded = 0
for root, dirs, files in os.walk(dist_dir):
    for fname in files:
        local_path = os.path.join(root, fname)
        # S3 key is relative to dist_dir, using forward slashes
        s3_key = os.path.relpath(local_path, dist_dir).replace("\\", "/")
        
        # Determine content type
        ext = os.path.splitext(fname)[1].lower()
        content_type = mime_overrides.get(ext)
        if not content_type:
            content_type, _ = mimetypes.guess_type(fname)
        if not content_type:
            content_type = "application/octet-stream"
        
        # Set cache headers
        if ext in (".html",):
            cache_control = "no-cache, no-store, must-revalidate"
        elif ext in (".js", ".css"):
            cache_control = "public, max-age=31536000, immutable"
        else:
            cache_control = "public, max-age=86400"
        
        s3.upload_file(
            local_path,
            bucket,
            s3_key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": cache_control
            }
        )
        uploaded += 1
        print("   Uploaded: %s (%s)" % (s3_key, content_type))

print("   Total files uploaded: %d" % uploaded)

# Step 5: Get website endpoint
print()
print("5. S3 Website Endpoint:")
endpoint = "http://%s.s3-website.ap-south-1.amazonaws.com" % bucket
print("   %s" % endpoint)

print()
print("DEPLOYMENT COMPLETE")
