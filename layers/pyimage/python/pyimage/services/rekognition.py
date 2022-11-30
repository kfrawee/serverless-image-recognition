"""
Helper functions for interacting with rekognition service
"""

import logging
import os

import boto3
from botocore.exceptions import ClientError

MAIN_BUCKET = os.getenv("MAIN_BUCKET")
rekognition_client = boto3.client("rekognition")


def label_image(image_s3_key: str):
    try:
        image_labels = rekognition_client.detect_labels(
            Image={"S3Object": {"Bucket": MAIN_BUCKET, "Name": image_s3_key}},
            MaxLabels=5,
        )
        return [label.get("Name") for label in image_labels["Labels"]]
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidImageFormatException":
            raise  # TODO: Handle more errors, i.e. size, ...
        return []
