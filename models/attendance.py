from app import db

class MeetingAttendance(db.Model):
    __tablename__ = "meeting_mgn_meeting_attendance"

    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meeting_id = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, nullable=True)   # null kalau guest
    attendee_name = db.Column(db.String(255), nullable=False)
    attendee_email = db.Column(db.String(255), nullable=True)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    registration_method = db.Column(db.String(50), nullable=True)
    registered_by = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_guest = db.Column(db.Boolean, default=False)
    attendance_status = db.Column(db.SmallInteger, default=0)  