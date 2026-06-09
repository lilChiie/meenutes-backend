from extensions import db
from datetime import datetime

class MeetingMinutes(db.Model):
    __tablename__ = "meeting_minutes"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id")
    )

    event_division_id = db.Column(
        db.Integer,
        db.ForeignKey("event_divisions.id")
    )

    internal_division_id = db.Column(
        db.Integer,
        db.ForeignKey("internal_divisions.id")
    )

    meeting_date = db.Column(db.DateTime)

    transcript = db.Column(db.Text)

    summary = db.Column(db.Text)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )