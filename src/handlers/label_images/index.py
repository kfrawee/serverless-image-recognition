"""
Handler for label image once it is uploaded to s3
"""

from datetime import datetime


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
    labels = label_image(image_key)

    if labels:
        # TODO: update the table with COMPLETED and labels
        # main_table.update_invocation()
        pass

    else:
        pass
        # TODO: update the table with FAILED

    # delete the uploaded object, no need to keep it in s3
    # delete_object(image_key)
    return {}
