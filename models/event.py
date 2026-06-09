from extensions import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date  = db.Column(db.Date, nullable=True)  
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )