"""
Handler for blobs CRUDS (post and get) operations.
    - create_blob
    - get_blob
"""

import json
from http import HTTPStatus
import ulid

from pyimage.utils.decorators import lambda_decorator


@lambda_decorator
def handler(event, _):
    return {
        "statusCode": HTTPStatus.OK,
        "body": {"message": str(ulid.new())},
    }
