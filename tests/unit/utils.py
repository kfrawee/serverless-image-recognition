import os

import boto3

REGION = os.getenv("REGION")
TABLE_NAME = os.getenv("MAIN_TABLE")
BUCKET_NAME = os.getenv("MAIN_BUCKET")


def create_table():
    """Create Main Table"""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)

    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "pk",
                "AttributeType": "S",
            },
            {
                "AttributeName": "sk",
                "AttributeType": "S",
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    return table


def create_bucket():
    """Create Main Bucket"""
    s3 = boto3.resource("s3", region_name=REGION)
    bucket = s3.create_bucket(Bucket=BUCKET_NAME)

    return bucket
