"""
Handler for blobs CRUDS (post and get) operations.
    - create_blob
    - get_blob
"""

import json
from http import HTTPStatus


from lambda_layer.test import test_layer_functions


def handler(event, _):
    return {"statusCode": HTTPStatus.OK, "Body": {"message": test_layer_functions()}}
