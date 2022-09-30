"""
Handler for labeling image once it is uploaded to s3
"""

from datetime import datetime, timezone


from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.invocation_statuses import InvocationStatus
from pyimage.utils.helpers import logger

from pyimage.services.s3 import delete_object
from pyimage.services.dynamodb import MainTable
from pyimage.services.rekognition import label_image


main_table = MainTable()


@lambda_decorator
def handler(event, _):
    """Handles image labeling once uploaded to s3.

    Args:
        event (dict): Invocation information for the lambda handler.
        _ (dict): Unused context information for the lambda handler.

    Returns:
        dict: empty dict
    """

    image_key = event.get("Records", [])[0].get("s3", {}).get("object", {}).get("key")
    blob_id = image_key.split("/")[-1]

    main_table.update_invocation(
        blob_id=blob_id,
        invocation_status=InvocationStatus.IN_PROGRESS.value,
    )

    labels = label_image(image_key)
    now = datetime.now(timezone.utc)

    if labels:
        main_table.update_invocation(
            blob_id=blob_id,
            invocation_status=InvocationStatus.COMPLETED.value,
            completed_on=str(now),
            labels=labels,
        )

    else:
        main_table.update_invocation(
            blob_id=blob_id,
            invocation_status=InvocationStatus.FAILED.value,
            completed_on=str(now),
        )

    # delete the uploaded object, no need to keep it in s3
    delete_object(image_key)
    return {}
