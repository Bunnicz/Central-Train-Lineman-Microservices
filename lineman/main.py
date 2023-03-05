from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_prefixed_env()
app.config["SECRET_KEY"]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/state")
def hello_world2():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run()

# from typing import List
# from typing import Optional
# from sqlalchemy import ForeignKey
# from sqlalchemy import String
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship


# class Base(DeclarativeBase):
#     pass


# class Turnpike(Base):
#     __tablename__ = "turnpike"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # place: Mapped[str] = mapped_column(String(30))
#     state: Mapped[bool] = mapped_column()
#     timestamp:

#     def __repr__(self) -> str:
#         return f"Turnpike(id={self.id!r}, place={self.name!r}, state={self.state!r})"
