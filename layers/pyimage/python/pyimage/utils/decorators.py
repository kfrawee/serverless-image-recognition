"""
Lambda handlers decorators.
REFERENCES:
https://github.com/dschep/lambda-decorators/blob/master/lambda_decorators.py
"""

from functools import wraps
from http import HTTPStatus
from json import JSONDecodeError
import traceback

try:
    import simplejson as json
except ImportError:
    import json

from lambda_decorators import cors_headers

from pyimage.utils.helpers import logger


def dump_json_body_and_catch_unexpected_errors(
    handler_or_none=None, **json_dumps_kwargs
):
    if handler_or_none is not None and len(json_dumps_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    response = handler(event, context)
                    logger.debug({"final_response": response})
                    body = response.get("body")
                    if isinstance(body, dict) or isinstance(body, list):
                        response["body"] = json.dumps(
                            body, default=str, **json_dumps_kwargs
                        )
                    return response
                except Exception:
                    logger.error(f"Unexpected error: {traceback.format_exc()}")
                    return {
                        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "body": json.dumps({"message": "Internal server error"}),
                    }

            return wrapper

        return wrapper_wrapper
    else:
        return dump_json_body_and_catch_unexpected_errors()(handler_or_none)


def load_json_body(handler_or_none=None, **json_loads_kwargs):
    if handler_or_none is not None and len(json_loads_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                if isinstance(event.get("body"), str):
                    try:
                        loaded_body = json.loads(event["body"], **json_loads_kwargs)
                    except Exception as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        logger.debug(event)
                        response = {
                            "statusCode": HTTPStatus.BAD_REQUEST,
                            "body": json.dumps(
                                {"message": "Request body is invalid JSON."}
                            ),
                        }
                        return response

                    event["body"] = loaded_body

                logger.debug(event)

                return handler(event, context)

            return wrapper

        return wrapper_wrapper
    else:
        return load_json_body()(handler_or_none)


def lambda_decorator(handler_func):
    def wrapper_wrapper(handler):
        @wraps(handler)
        @logger.inject_lambda_context
        def wrapper(event, context):
            body = event.get("body")

            try:
                body = json.loads(body)
            except (JSONDecodeError, TypeError):
                pass

            response = cors_headers(
                dump_json_body_and_catch_unexpected_errors(load_json_body(handler))
            )(event, context)
            if headers := response.get("headers"):
                headers[
                    "Strict-Transport-Security"
                ] = "max-age=31536000; includeSubDomains; preload"
            else:
                response["headers"] = {
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
                }
            return response

        return wrapper

    return wrapper_wrapper(handler_func)
