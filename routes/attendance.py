from flask import Blueprint, jsonify, request
from app import db
from models import MeetingAttendance

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/", methods=["GET"])
def get_attendance():
    records = MeetingAttendance.query.all()
    
    return jsonify([
        {
            "attendance_id": r.attendance_id,
            "meeting_id": r.meeting_id,
            "employee_id": r.employee_id,
            "attendee_name": r.attendee_name,
            "attendee_email": r.attendee_email,
            "check_in_time": r.check_in_time,
            "check_out_time": r.check_out_time,
            "registration_method": r.registration_method,
            "registered_by": r.registered_by,
            "notes": r.notes,
            "is_guest": r.is_guest,
            "attendance_status": r.attendance_status
        }
        for r in records
    ])

@attendance_bp.route("/", methods=["POST"])
def create_attendance():
    data = request.get_json()

    try:
        # Wajib
        if not data.get("meeting_id"):
            return jsonify({"error": "meeting_id is required"}), 400
        if not data.get("attendee_name"):
            return jsonify({"error": "attendee_name is required"}), 400

        new_att = MeetingAttendance(
            meeting_id=data.get("meeting_id"),
            employee_id=data.get("employee_id"),
            attendee_name=data.get("attendee_name"),
            attendee_email=data.get("attendee_email"),

            check_in_time=data.get("check_in_time"),   # biarkan None → pakai default DB
            check_out_time=data.get("check_out_time"),

            registration_method=data.get("registration_method"),  # None = default "Tablet"
            registered_by=data.get("registered_by"),
            notes=data.get("notes"),
            is_guest=data.get("is_guest", False),

            attendance_status=data.get("attendance_status", 0)  # default pending
        )

        db.session.add(new_att)
        db.session.commit()

        return jsonify({
            "message": "Attendance record created successfully",
            "attendance_id": new_att.attendance_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@attendance_bp.route("/<int:attendance_id>", methods=["PUT"])
def update_attendance(attendance_id):
    data = request.get_json()
    record = MeetingAttendance.query.get(attendance_id)

    if not record:
        return jsonify({"error": "Attendance record not found"}), 404

    try:
        record.meeting_id = data.get("meeting_id", record.meeting_id)
        record.employee_id = data.get("employee_id", record.employee_id)
        record.attendee_name = data.get("attendee_name", record.attendee_name)
        record.attendee_email = data.get("attendee_email", record.attendee_email)
        record.check_in_time = data.get("check_in_time", record.check_in_time)
        record.check_out_time = data.get("check_out_time", record.check_out_time)
        record.registration_method = data.get("registration_method", record.registration_method)
        record.registered_by = data.get("registered_by", record.registered_by)
        record.notes = data.get("notes", record.notes)
        record.is_guest = data.get("is_guest", record.is_guest)

        db.session.commit()

        return jsonify({"message": "Attendance updated successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@attendance_bp.route("/<int:attendance_id>", methods=["DELETE"])
def delete_attendance(attendance_id):
    record = MeetingAttendance.query.get(attendance_id)

    if not record:
        return jsonify({"error": "Attendance record not found"}), 404

    try:
        db.session.delete(record)
        db.session.commit()

        return jsonify({"message": "Attendance record deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
