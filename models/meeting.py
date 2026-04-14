from app import db
from datetime import datetime

class Meeting(db.Model):
    __tablename__ = "meeting_mgn_meetings"

    meeting_id = db.Column(db.Integer, primary_key=True)
    meeting_title = db.Column(db.String(255), nullable=False)
    meeting_purpose = db.Column(db.String(500))

    start_date_time = db.Column(db.DateTime, nullable=False)
    end_date_time = db.Column(db.DateTime, nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey("meeting_mgn_meeting_rooms.room_id"), nullable=False)
    author_employee_id = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=False)
    status_id = db.Column(db.Integer, nullable=False, default=1)
