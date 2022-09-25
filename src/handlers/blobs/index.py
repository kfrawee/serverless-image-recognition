"""
Handler for blobs CRUDS (post and get) operations.
    - create_blob
    - get_blob
"""

import json
from http import HTTPStatus
from datetime import datetime
import ulid

from marshmallow import ValidationError
from .schemas import CreateBlobSchema

from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.helpers import logger


create_blob_schema = CreateBlobSchema()


@lambda_decorator
def create_blob(event, _):
    """
    Handles requests of POST /blobs endpoint.

    Args:
        event (dict): Invocation information for the lambda handler.
        _ (dict): Unused context information for the lambda handler.

    Returns:
        dict: blob_id with a pre-singed url to upload the image and a timestamp.
    """
    data = event.get("body") or {}
    try:
        clear_data = create_blob_schema.load(data)
    except ValidationError as e:
        logger.debug("Received invalid request body.")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": {"message": f"Invalid request body: {e.normalized_messages()}"},
        }

    now = datetime.now()
    blob_id = ulid.from_timestamp(now)
    upload_url = (
        "https://www.example.com/upload"  # from s3 helpers, create a pre-signed url
    )

    response_body = {"blob_id": blob_id, "create_on": now, "upload_url": upload_url}
    if callback_url := clear_data.get("callback_url"):
        response_body.update(callback_url=callback_url)

    # update table with invocation details
    # using blob_id as a pk and sk (partition key)
    # started_on
    # callback_url (if exists)

    return {"statusCode": HTTPStatus.CREATED, "body": response_body}
