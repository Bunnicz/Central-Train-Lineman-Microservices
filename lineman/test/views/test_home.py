# import pytest
# from app import create_app
# from api.models import db
# from datetime import datetime


# @pytest.fixture()
# def app():
#     app = create_app()
#     app.config.update(
#         {
#             "TESTING": True,
#         }
#     )

#     yield app


# def test_get_api_endpoint():
#     with app.test_client() as c:
#         response = c.get("api/v1/state")
#         assert response.status_code == 200
#         json_response = response.get_json()
#         now = str(datetime.now())
#         assert json_response == {"is_open": False, "timestamp": now}


# def test_post_api_endpoint():
#     with app.test_client() as c:
#         response = c.post("api/v1/state", json={"toggle": "open"})
#         assert response.status_code == 201
