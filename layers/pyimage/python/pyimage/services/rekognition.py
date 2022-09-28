"""
Helper functions for interacting with rekognition service
"""

import os
import logging
import boto3


MAIN_BUCKET = os.getenv("MAIN_BUCKET")
rekognition_client = boto3.client("rekognition")


def label_image(image_s3_key: str):
    image_labels = rekognition_client.detect_labels(
        Image={"S3Object": {{"Bucket": MAIN_BUCKET, "Name": image_s3_key}}},
        MaxLabels=5,
    )
    print(50 * "+")
    logging.debug(image_labels)
    print(50 * "+")

    return [label.get("name") for label in image_labels.get("Labels", {})]
