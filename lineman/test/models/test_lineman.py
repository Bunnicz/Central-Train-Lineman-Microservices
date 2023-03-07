# import pytest
# from test.conftest import app
# from api.models import db
# from datetime import datetime

# import api.models.lineman as lineman


# def test_db_create(app):
#     app = app()
#     now = str(datetime.now())
#     test_model_to_insert = lineman.Lineman(is_open=False, timestamp=now)
#     test_model_to_insert.save()
#     db.session.commit()

#     assert db.session.query(lineman.Lineman).one()
