from os import environ

from flasgger import Swagger
from flask import Flask

from api.models import Lineman, db
from api.views.home import home_api

FLASK_DEBUG = environ.get("FLASK_DEBUG", "false").lower() == "true"
SECRET_KEY = environ.get("SECRET_KEY", "supersecret")
POSTGRES_NAME = environ.get("POSTGRES_NAME", "postgres")
POSTGRES_USERNAME = environ.get("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVICE_HOST = environ.get("POSTGRES_SERVICE_HOST", "postgres")
POSTGRES_SERVICE_PORT = environ.get("POSTGRES_SERVICE_PORT", "5432")
DATABASE_NAME = environ.get("DATABASE_NAME", "postgres")


def create_app() -> Flask:
    """Returns flask app
    Config app and init extesnions with postgres DB.

    Returns:
        Flask: Flask class object.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = FLASK_DEBUG
    app.config["SWAGGER"] = {"title": "Lineman api", "version": "1.0.0"}
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql://{POSTGRES_NAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVICE_HOST}:{POSTGRES_SERVICE_PORT}/{DATABASE_NAME}"

    Swagger(app)
    db.init_app(app)
    app.register_blueprint(home_api, url_prefix="/api/v1")

    with app.app_context():
        db.create_all()
        if db.session.query(Lineman.id).first() is None:
            first_state = Lineman(is_open=False)
            db.session.add(first_state)
            db.session.commit()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
