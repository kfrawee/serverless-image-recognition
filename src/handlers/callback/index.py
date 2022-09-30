""" 
Handler for sending results to callback - if provided.
"""

from datetime import datetime, timezone


from pyimage.utils.decorators import lambda_decorator
from pyimage.utils.helpers import logger

from pyimage.services.dynamodb import MainTable
from pyimage.utils.helpers import send_callback

main_table = MainTable()


@lambda_decorator
def handler(event, _):

    logger.debug("+" * 20)

    # try:
    # send_callback(callback_url, callback_data)

    return {}
