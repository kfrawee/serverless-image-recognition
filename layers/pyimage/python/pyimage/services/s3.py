"""
Helper functions for interacting with s3 service
"""

import os
import logging

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client(
    "s3",
    config=boto3.session.Config(
        s3={"addressing_style": "path"}, signature_version="s3v4"
    ),
)


MAIN_BUCKET = os.getenv("MAIN_BUCKET")
MAIN_DIR = "blobs"


def generate_presigned_url(blob_id: str, Bucket=MAIN_BUCKET, expiration=60 * 60) -> str:
    """Generate presigned url for image upload"""
    try:
        blob_key = f"{MAIN_DIR}/{blob_id}/{blob_id}"
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": Bucket, "Key": blob_key},
            ExpiresIn=expiration,
            HttpMethod="PUT",
        )
    except ClientError as e:
        logging.error(e)
        return None

    return presigned_url
