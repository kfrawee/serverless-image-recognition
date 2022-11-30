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
        from utils import create_bucket, create_table

        self.MainTable = create_table()
        self.MainBucket = create_bucket()

        self.event = {
            "requestContext": {
                "requestId": "TEST",
                "path": "TEST",
                "domainName": "TEST",
            },
            "resource": "/TEST",
            "pathParameters": {
                "blob_id": "123",
            },
        }

        from src.handlers.blobs.index import get_blob

        self.handler = get_blob

    def tearDown(self):
        self.MainTable.delete()
        self.MainBucket.delete()

    @mock.patch(
        "src.handlers.blobs.index.main_table.get_invocation",
        return_value={"blob_id": "123", "invocation_status": "COMPLETED"},
    )
    def test_get_blob_completed(self, *args):
        response = self.handler(self.event, self.lambda_context)
        assert response["statusCode"] == HTTPStatus.OK
        resp_body = json.loads(response.get("body"))
        assert resp_body.get("invocation_status") == "COMPLETED"

    @mock.patch(
        "src.handlers.blobs.index.main_table.get_invocation",
        return_value={"blob_id": "123", "invocation_status": "FAILED"},
    )
    def test_get_blob_failed(self, *args):
        response = self.handler(self.event, self.lambda_context)
        assert response["statusCode"] == HTTPStatus.OK
        resp_body = json.loads(response.get("body"))
        assert resp_body.get("invocation_status") == "FAILED"

    @mock.patch(
        "src.handlers.blobs.index.main_table.get_invocation",
        return_value={},
    )
    def test_get_blob_not_found(self, *args):
        response = self.handler(self.event, self.lambda_context)
        assert response["statusCode"] == HTTPStatus.NOT_FOUND
