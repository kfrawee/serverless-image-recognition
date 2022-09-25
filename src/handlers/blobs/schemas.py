from marshmallow import Schema, fields


class CreateBlobSchema(Schema):
    callback_url = fields.URL()
