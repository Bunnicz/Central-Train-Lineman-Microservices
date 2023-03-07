from http import HTTPStatus
from flask import Blueprint, jsonify, make_response, request, abort, Request
from flasgger import swag_from
from api.models import db, Lineman
from api.schema import WelcomeSchema, StateSchema, ToggleSchema
from flask_sqlalchemy import SQLAlchemy

home_api = Blueprint("api", __name__)


# @home_api.route("/")
# @swag_from(
#     {
#         "responses": {
#             HTTPStatus.OK.value: {
#                 "description": "Welcome to the Lineman Api",
#                 "schema": WelcomeSchema,
#             }
#         }
#     }
# )
# def welcome():
#     """
#     Home route - disable later
#     A more detailed description of the endpoint
#     ---
#     """
#     result = Lineman()
#     return WelcomeSchema().dump(result), 200

STATE_URI = "/state"


@home_api.get(STATE_URI)
@swag_from(
    {
        "responses": {
            HTTPStatus.OK.value: {
                "description": "Get crossing current state",
                "schema": StateSchema,
            }
        }
    }
)
def get_state():
    """
    [GET] gate current state
    A more detailed description of the endpoint
    ---
    """

    obj = db.session.query(Lineman).order_by(Lineman.id.desc()).first()
    data = {"is_open": obj.is_open, "timestamp": obj.timestamp}

    if not request.json or not "title" in request.json:
        abort(400)
    # if data["toggle"] == "Open":
    #     pass
    # elif data["toggle"] == "Close":
    #     pass
    lineman = Lineman(is_open=False)
    db.session.add(lineman)
    db.session.commit()
    return StateSchema().dump(data)


@home_api.put(STATE_URI)
@swag_from(
    {
        "responses": {
            HTTPStatus.OK.value: {
                "description": "Get crossing current state",
                "schema": StateSchema,
            }
        }
    }
)
def put_state(request: Request):
    """
    [PUT] gate current state
    A more detailed description of the endpoint
    ---
    """

    obj = db.session.query(Lineman).order_by(Lineman.id.desc()).first()
    data = {"is_open": obj.is_open, "timestamp": obj.timestamp}

    if not request.json or not "title" in request.json:
        abort(400)
    # if data["toggle"] == "Open":
    #     pass
    # elif data["toggle"] == "Close":
    #     pass
    lineman = Lineman(is_open=False)
    db.session.add(lineman)
    db.session.commit()

    return StateSchema().dump(data)


@home_api.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)
