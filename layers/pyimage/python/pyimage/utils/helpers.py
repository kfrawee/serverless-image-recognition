import os
import aws_lambda_powertools

# import requests


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)

def send_callback():
    pass