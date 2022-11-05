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
class TestLabelImage(TestCase):
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
                    "s3": {"object": {"key": "123"}},
                }
            ],
        }

        from src.handlers.label_images.index import handler

        self.handler = handler

    def tearDown(self):
        self.MainTable.delete()
        self.MainBucket.delete()

    @mock.patch(
        "src.handlers.label_images.index.main_table.update_invocation",
        return_value={},
    )
    @mock.patch(
        "src.handlers.label_images.index.label_image",
        return_value=["label_1"],
    )
    @mock.patch(
        "src.handlers.label_images.index.delete_object",
        return_value={},
    )
    def test_label_image_completed(self, *args):
        response = self.handler(self.event, self.lambda_context)

        assert response == self.event

    @mock.patch(
        "src.handlers.label_images.index.main_table.update_invocation",
        return_value={},
    )
    @mock.patch(
        "src.handlers.label_images.index.label_image",
        return_value=[],
    )
    @mock.patch(
        "src.handlers.label_images.index.delete_object",
        return_value={},
    )
    def test_label_image_failed(self, *args):
        response = self.handler(self.event, self.lambda_context)

        assert response == self.event
