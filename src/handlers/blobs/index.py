"""
Handler for blobs CRUDS (post and get) operations.
    - create_blob
    - get_blob
"""

from http import HTTPStatus
from datetime import datetime, timezone
import ulid

from marshmallow import ValidationError

from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.helpers import logger
from pyimage.utils.invocation_statuses import InvocationStatus
from pyimage.utils.schemas import CreateBlobRequestSchema, CreateOrGetBlobResponseSchema
from pyimage.utils.error_messages import INVALID_IMAGE_FORMAT

from pyimage.services.s3 import generate_presigned_url
from pyimage.services.dynamodb import MainTable

create_blob_request_schema = CreateBlobRequestSchema()
create_or_get_blob_response_schema = CreateOrGetBlobResponseSchema()

main_table = MainTable()


@lambda_decorator
def create_blob(event, _):
    """
    Handles requests of POST /blobs endpoint.

    Args:
        event (dict): Invocation information for the lambda handler.
        _ (dict): Unused context information for the lambda handler.

    Returns:
        dict: blob_id with a pre-singed url to upload the image.
    """
    data = event.get("body") or {}
    try:
        clear_data = create_blob_request_schema.load(data)
    except ValidationError as e:
        logger.debug("Received invalid request body.")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": {"message": f"Invalid request body: {e.normalized_messages()}"},
        }

    now = datetime.now(timezone.utc)
    blob_id = str(ulid.from_timestamp(now))
    invocation_status = InvocationStatus.ACTION_REQUIRED.value
    upload_url = generate_presigned_url(blob_id)

    main_table.put_invocation(
        blob_id=blob_id,
        invocation_status=invocation_status,
        requested_on=str(now),
        **clear_data,
    )

    response_body = {
        "blob_id": blob_id,
        "invocation_status": invocation_status,
        "requested_on": now,
        "upload_url": upload_url,
        "_links": {
            "status": f"https://{event.get('requestContext').get('domainName')}/"
            f"{event.get('requestContext').get('stage')}/blobs/{blob_id}",
        },
    }
    if callback_url := clear_data.get("callback_url"):
        response_body.update(callback_url=callback_url)

    return {
        "statusCode": HTTPStatus.CREATED,
        "body": create_or_get_blob_response_schema.dump(response_body),
    }


@lambda_decorator
def get_blob(event, _):
    """
    Handles requests of GET /blobs/{blob_id} endpoint.

    Args:
        event (dict): Invocation information for the lambda handler.
        _ (dict): Unused context information for the lambda handler.

    Returns:
        dict: blob status.
    """
    blob_id = event.get("pathParameters", {}).get("blob_id")

    if not (invocation := main_table.get_invocation(blob_id)):
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": {
                "message": f"Invocation with the blob_id '{blob_id}' was not found."
            },
        }

    invocation_status = invocation.get("invocation_status")

    response_body = {"blob_id": blob_id, **invocation}

    if invocation_status == InvocationStatus.FAILED.value:
        response_body.update(failure_reason=INVALID_IMAGE_FORMAT)

    return {
        "statusCode": HTTPStatus.OK,
        "body": create_or_get_blob_response_schema.dump(response_body),
    }
