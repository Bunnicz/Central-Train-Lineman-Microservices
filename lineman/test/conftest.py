# import pytest

# from app import create_app
# from api.models import db


# @pytest.yield_fixture
# def app():
#     def _app():
#         app = create_app()
#         app.test_request_context().push()

#         # always starting with an empty DB
#         db.drop_all()
#         from api.models import Lineman

#         db.create_all()

#         return app

#     yield _app
#     db.session.remove()
#     db.drop_all()
