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
class TestGetBlob(TestCase):
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
            "body": json.dumps({"callback_url": "https://www.example.com/abc-123-xyz"}),
        }

        self.event_invalid_body = {
            "requestContext": {
                "requestId": "TEST",
                "path": "TEST",
                "domainName": "TEST",
            },
            "resource": "/TEST",
            "body": json.dumps({"invalid_schema_key": "value"}),
        }

        from src.handlers.blobs.index import create_blob

        self.handler = create_blob

    def tearDown(self):
        self.MainTable.delete()
        self.MainBucket.delete()

    def test_create_blob_invalid_request(self, *args):
        response = self.handler(self.event_invalid_body, self.lambda_context)
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST

    @mock.patch(
        "src.handlers.blobs.index.generate_presigned_url",
        return_value="https://www.example.com/test",
    )
    @mock.patch(
        "src.handlers.blobs.index.main_table.put_invocation",
        return_value={},
    )
    def test_create_blob_success(self, *args):
        response = self.handler(self.event, self.lambda_context)
        assert response["statusCode"] == HTTPStatus.CREATED
        resp_body = json.loads(response.get("body"))
        assert resp_body.get("invocation_status") == "ACTION_REQUIRED"
