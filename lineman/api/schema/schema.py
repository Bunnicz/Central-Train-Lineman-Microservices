from flask_marshmallow import Schema
from marshmallow.fields import Bool, Str


class StateSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["is_open", "timestamp"]

    is_open = Bool()
    timestamp = Str()
