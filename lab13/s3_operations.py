import boto3
from botocore.config import Config
from pathlib import Path

BUCKET_NAME = "daniyar-s3-lab-2026-xyz"
KEY = "uploads/report.csv"
REGION = "eu-north-1"

BASE_DIR = Path(__file__).resolve().parent
REPORT_PATH = BASE_DIR / "report.csv"
DOWNLOADED_REPORT_PATH = BASE_DIR / "downloaded_report.csv"

cfg = Config(
    region_name=REGION,
    signature_version="s3v4",
    s3={"addressing_style": "virtual"},
)

s3 = boto3.client("s3", config=cfg)

print("=== START S3 OPERATIONS ===")

# Upload with metadata
s3.upload_file(
    str(REPORT_PATH),
    BUCKET_NAME,
    KEY,
    ExtraArgs={
        "Metadata": {
            "department": "analytics",
            "owner": "daniyar",
        }
    },
)

print(f"Uploaded {REPORT_PATH}")

# Download file
s3.download_file(
    BUCKET_NAME,
    KEY,
    str(DOWNLOADED_REPORT_PATH),
)

print(f"Downloaded file to {DOWNLOADED_REPORT_PATH}")

# List objects with pagination
paginator = s3.get_paginator("list_objects_v2")

for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="uploads/"):
    for obj in page.get("Contents", []):
        print("File:", obj["Key"])
        print("Size:", obj["Size"])
        print("Last Modified:", obj["LastModified"])
        print("------")

# Generate presigned URL (valid for 2 hours)
url = s3.generate_presigned_url(
    "get_object",
    Params={
        "Bucket": BUCKET_NAME,
        "Key": KEY,
    },
    ExpiresIn=7200,
)

print("Presigned URL:", url)

input("Open the URL in your browser, then press Enter...")

# Delete object
s3.delete_object(
    Bucket=BUCKET_NAME,
    Key=KEY,
)

print("File deleted")
print("=== DONE ===")