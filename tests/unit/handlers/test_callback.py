import json
from http import HTTPStatus
from unittest import TestCase, mock

import pytest
from moto import mock_dynamodb, mock_s3


@pytest.mark.usefixtures("lambda_context")
@pytest.mark.usefixtures("set_aws_credentials")
@pytest.mark.usefixtures("set_environment_variables")
@mock_dynamodb
@mock_s3
class TestCallBack(TestCase):
    def setUp(self):
        from utils import create_table, create_bucket

        self.MainTable = create_table()
        self.MainBucket = create_bucket()

        self.event = {
            "requestContext": {
                "requestId": "TEST",
                "path": "TEST",
                "domainName": "TEST",
            },
            "resource": "/TEST",
            "Records": [
                {
                    "dynamodb": {"NewImage": {"pk": {"S": "123"}}},
                }
            ],
        }

        from src.handlers.callback.index import handler

        self.handler = handler

    def tearDown(self):
        self.MainTable.delete()
        self.MainBucket.delete()

    @mock.patch(
        "src.handlers.callback.index.main_table.get_invocation",
        return_value={},
    )
    def test_no_callback(self, *args):
        response = self.handler(self.event, self.lambda_context)

        assert response

    @mock.patch(
        "src.handlers.callback.index.main_table.get_invocation",
        return_value={
            "callback_url": "https://www.example.com/callback",
            "invocation_status": "FAILED",
        },
    )
    @mock.patch(
        "src.handlers.callback.index.send_callback",
        return_value={},
    )
    def test_callback_failed_invocation(self, *args):
        response = self.handler(self.event, self.lambda_context)

        assert response

    @mock.patch(
        "src.handlers.callback.index.main_table.get_invocation",
        return_value={
            "callback_url": "https://www.example.com/callback",
            "invocation_status": "COMPLETED",
        },
    )
    @mock.patch(
        "src.handlers.callback.index.send_callback",
        return_value={},
    )
    def test_callback_completed_invocation(self, *args):
        response = self.handler(self.event, self.lambda_context)

        assert response
