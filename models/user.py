from app import db
from datetime import datetime

class MeetingUser(db.Model):
    __tablename__ = "meeting_mgnt_user"

    nik = db.Column(db.String(6), db.ForeignKey("employees.employee_code"), primary_key=True) 
    userid = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    section_cd = db.Column(db.String(50))
    section_nm = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default="1")
    is_email_confirmed = db.Column(db.Boolean, default=False)
    ent_by = db.Column(db.String(100), default="SYSTEM")
    ent_dt = db.Column(db.DateTime, default=datetime.utcnow)
    upd_by = db.Column(db.String(100))
    upd_dt = db.Column(db.DateTime, onupdate=datetime.utcnow)
    password = db.Column(db.String(255), nullable=False)

    employee_obj = db.relationship(
    "Employee",
    primaryjoin="Employee.employee_code == foreign(MeetingUser.nik)",
    backref=db.backref("meeting_users", lazy=True),
)

    def __repr__(self):
        return f"<MeetingUser {self.userid}>"

