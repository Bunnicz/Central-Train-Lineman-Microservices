from http import HTTPStatus

from flasgger import swag_from
from flask import Blueprint, Response, json, jsonify, make_response, request
from werkzeug.exceptions import HTTPException

from api.models import Lineman, db
from api.schema import StateSchema

home_api = Blueprint("api", __name__)


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
    responses:
        200
    """
    obj = db.session.query(Lineman).order_by(Lineman.id.desc()).first()
    data = {"is_open": obj.is_open, "timestamp": obj.timestamp}

    return StateSchema().dump(data)


@home_api.put(STATE_URI)
@swag_from(
    {
        "responses": {
            HTTPStatus.OK.value: {
                "description": "Update gate state",
                "schema": StateSchema,
            }
        }
    }
)
def put_state():
    """
    [PUT] gate current state
    A more detailed description of the endpoint
    ---
    parameters:
    -   in: body
        name: body
    responses:
        201
    """
    data = request.json.get("toggle", "").lower()
    if data in ("open", "close"):
        is_open = True if data == "open" else False
        lineman = Lineman(is_open=is_open)
        db.session.add(lineman)
        db.session.commit()
        return Response(status=201)

    return make_response(
        jsonify(
            {"error": "Bad request, please refer to documentation for allowed values"},
        ),
        400,
    )


@home_api.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@home_api.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({"error": "Method Not Allowed"}), 405)


@home_api.errorhandler(HTTPException)
def handle_exception(error):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = error.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response
