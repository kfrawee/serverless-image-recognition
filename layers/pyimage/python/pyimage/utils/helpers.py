import os
import aws_lambda_powertools


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)
