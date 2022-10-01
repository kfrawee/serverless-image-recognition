from marshmallow import Schema, fields, post_dump
from marshmallow_union import Union


class CreateBlobRequestSchema(Schema):
    callback_url = fields.URL()


class CreateOrGetBlobResponseSchema(Schema):
    """For response dump/order only"""

    blob_id = fields.String()

    invocation_status = fields.String()
    failure_reason = fields.String()

    requested_on = fields.String()
    started_on = fields.String()
    completed_on = fields.String()

    labels = fields.List(fields.String())

    upload_url = fields.URL()
    callback_url = fields.URL()

    message = fields.String()

    _links = fields.Dict()

    class Meta:
        ordered = True

    @post_dump
    def return_dict(self, data, **kwargs):
        """Post dump hook: Convert OrderedDict to Dict"""
        return dict(data)
