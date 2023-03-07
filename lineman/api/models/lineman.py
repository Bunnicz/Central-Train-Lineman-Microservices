from .base import db


class Lineman(db.Model):
    """Lineman Table."""

    __tablename__ = "lineman"
    
    id = db.Column(db.Integer, unique=True, primary_key=True)
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, is_open: bool):
        self.is_open = is_open

    def __repr__(self):
        return f"<Crossing(is open={self.is_open}, timestamp={self.timestamp})"
