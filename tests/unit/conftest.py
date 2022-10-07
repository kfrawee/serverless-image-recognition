import os
from dataclasses import dataclass
from unittest import mock
import uuid

import pytest


@pytest.fixture(scope="class")
def lambda_context(request):
    """inject dummy context to lambda"""

    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-east-1:1234:function:test"
        aws_request_id: str = str(uuid.uuid4())

    # set a class attribute on the invoking test context
    request.cls.lambda_context = LambdaContext()


@pytest.fixture(scope="session")
def set_environment_variables():
    env_vars = {
        "REGION": "us-east-1",
        "MAIN_TABLE": "MAIN_TABLE",
        "MAIN_BUCKET": "MAIN_BUCKET",
    }
    with mock.patch.dict(os.environ, env_vars):
        yield


@pytest.fixture(scope="session")
def set_aws_credentials():
    aws_credentials = {
        "AWS_ACCESS_KEY_ID": "TEST",
        "AWS_SECRET_ACCESS_KEY": "TEST",
        "AWS_SECURITY_TOKEN": "TEST",
        "AWS_SESSION_TOKEN": "TEST",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    with mock.patch.dict(os.environ, aws_credentials):
        yield
