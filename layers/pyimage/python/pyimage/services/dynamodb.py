"""
Helper functions for interacting with dynamodb service
"""

import os
import logging
from datetime import datetime

import boto3

from ..utils.invocation_statuses import InvocationStatus
from ..utils.constants import DYNAMODB_RESERVED_WORDS

MAIN_TABLE = os.getenv("MAIN_TABLE")
dynamodb_client = boto3.resource("dynamodb")


def generate_update_item_params(new_data):
    if not new_data:
        return

    expression_attribute_values = {}
    expression_attribute_names = {}
    update_expression = "SET "
    for iteration, (key, value) in enumerate(new_data.items()):
        if iteration != 0:
            # So, it is not the first iteration, so we need to add comma.
            update_expression += ", "
        attribute_key = f":{key}"
        if key.lower() in DYNAMODB_RESERVED_WORDS:
            expression_attribute_names[f"#{key}"] = key
            update_expression += f"#{key} = {attribute_key}"
        else:
            update_expression += f"{key} = {attribute_key}"
        expression_attribute_values[attribute_key] = value

    update_item_params = {
        "UpdateExpression": update_expression,
        "ExpressionAttributeValues": expression_attribute_values,
    }
    if expression_attribute_names:
        update_item_params.update(ExpressionAttributeNames=expression_attribute_names)

    return update_item_params


class MainTable:
    def __init__(self) -> None:
        self._table = dynamodb_client.Table(MAIN_TABLE)

    def put_invocation(
        self,
        blob_id: str,
        invocation_status: InvocationStatus,
        started_on=str(datetime.now()),
        completed_on=None,
        **data,
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

    def update_invocation(self, blob_id, **new_data):
        if not new_data:
            return
        return self._table.update_item(
            Key={"pk": blob_id, "sk": blob_id}, **generate_update_item_params(new_data)
        )
