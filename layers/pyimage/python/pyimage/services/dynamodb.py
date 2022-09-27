"""
Helper functions for interacting with dynamodb service
"""

import os
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from boto3.dynamodb.types import TypeDeserializer

from ..utils.invocation_statuses import InvocationStatus

MAIN_TABLE = os.getenv("MAIN_TABLE")
dynamodb_client = boto3.resource("dynamodb")


class MainTable:
    def __init__(self) -> None:
        self._table = dynamodb_client.Table(MAIN_TABLE)

    def put_invocation(
        self,
        blob_id: str,
        invocation_status: InvocationStatus,
        started_on=str(datetime.now()),
        completed_on=None,
        **data
    ):
        item = {
            "pk": blob_id,
            "sk": blob_id,
            "invocation_status": invocation_status,
            "started_on": started_on,
            "completed_on": completed_on,
            **data,
        }

        self._table.put_item(Item=item)

    def get_invocation(self, blob_id: str):
        return self._table.get_item(Key={"pk": blob_id, "sk": blob_id}).get("Item", {})

    def update_invocation(self, blob_id, **updated_data):
        pass
