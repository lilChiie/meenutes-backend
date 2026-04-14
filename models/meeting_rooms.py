from app import db

class MeetingRoom(db.Model):
    __tablename__ = "meeting_mgn_meeting_rooms"

    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer, default=0)
    equipment = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)

    meetings = db.relationship("Meeting", backref="room", lazy=True)
