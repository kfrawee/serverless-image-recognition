""" 
Handler for sending results to callback - if provided.
"""
from http import HTTPStatus
from requests.exceptions import HTTPError, ConnectionError, ConnectTimeout

from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.helpers import logger

from pyimage.services.dynamodb import MainTable
from pyimage.utils.helpers import send_callback
from pyimage.utils.invocation_statuses import InvocationStatus
from pyimage.utils.error_messages import INVALID_IMAGE_FORMAT
from pyimage.utils.schemas import CreateOrGetBlobResponseSchema


main_table = MainTable()
create_or_get_blob_response_schema = CreateOrGetBlobResponseSchema()


@lambda_decorator
def handler(event, _):
    """Handles sending updates to callback.

    Args:
        event (dict): Invocation information for the lambda handler.
        _ (dict): Unused context information for the lambda handler.

    Returns:
        dict: empty dict
    """

    blob_id = (
        event.get("Records", [])[0]
        .get("dynamodb", {})
        .get("NewImage", {})
        .get("pk", {})
        .get("S", "")
    )
    invocation = main_table.get_invocation(blob_id)

    if not (callback_url := invocation.get("callback_url")):
        return {
            "statusCode": HTTPStatus.OK,
        }

    try:
        callback_payload = {
            "blob_id": blob_id,
            **invocation,
        }

        invocation_status = invocation.get("invocation_status")
        if invocation_status == InvocationStatus.FAILED.value:
            callback_payload.update(failure_reason=INVALID_IMAGE_FORMAT)

        send_callback(
            callback_url, create_or_get_blob_response_schema.dump(callback_payload)
        )
    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        logger.error(f"Sending request to '{callback_url}' failed: '{e}'.")
    
    return event
