import os
import aws_lambda_powertools

import requests


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)


def send_callback(callback_url, data):
    headers = {
        "Content-type": "application/json",
    }

    response = requests.post(url=callback_url, headers=headers, json=data)
    logger.debug(
        f"Callback sent to {callback_url} with status: {response.status_code}."
    )
    response.raise_for_status()
