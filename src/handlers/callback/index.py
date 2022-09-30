""" 
Handler for sending results to callback - if provided.
"""

from requests.exceptions import HTTPError, ConnectionError, ConnectTimeout

from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.helpers import logger

from pyimage.services.dynamodb import MainTable
from pyimage.utils.helpers import send_callback
from pyimage.utils.schemas import CreateOrGetBlobResponseSchema

main_table = MainTable()
create_or_get_blob_response_schema = CreateOrGetBlobResponseSchema()


@lambda_decorator
def handler(event, _):

    blob_id = (
        event.get("Records", [])[0]
        .get("dynamodb", {})
        .get("NewImage", {})
        .get("pk", {})
        .get("S", "")
    )
    invocation = main_table.get_invocation(blob_id)

    if not (callback_url := invocation.get("callback_url")):
        return {}

    try:
        invocation_status = invocation.get("invocation_status")
        callback_data = create_or_get_blob_response_schema.dump(invocation)

        response = send_callback(callback_url, callback_data)
    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        logger.error(f"Sending request to '{callback_url}' failed: '{e}'.")
    return {}
