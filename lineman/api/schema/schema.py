from flask_marshmallow import Schema
from marshmallow.fields import Str, Bool


class WelcomeSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["message"]

    message = Str()


class StateSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["is_open"]

    message = Bool()


class ToggleSchema(Schema):
    class Meta:
        # Fields to expose
        fields = ["toggle"]

    message = Str()
