from flask import Blueprint, request, jsonify
from app import db
from models.attendance import MeetingAttendance
from datetime import datetime

meetings_bp = Blueprint("meetings", __name__)

@meetings_bp.route("/", methods=["POST"])
def create_meeting():
    data = request.json
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            DECLARE @out_id INT;
            EXEC meeting_mgn_create_meeting
                @meeting_title = ?,
                @meeting_purpose = ?,
                @start_date_time = ?,
                @end_date_time = ?,
                @room_id = ?,
                @author_employee_id = ?,
                @max_attendees = ?,
                @meeting_notes = ?,
                @status_id = ?,
                @created_by = ?,
                @meeting_id = @out_id OUTPUT;
            SELECT @out_id;
        """, (
            data["meeting_title"],
            data.get("meeting_purpose"),
            data["start_date_time"],
            data["end_date_time"],
            data["room_id"],
            data["author_employee_id"],
            data.get("max_attendees"),
            data.get("meeting_notes"),
            data["status_id"],
            data["created_by"]
        ))

        row = cursor.fetchone()
        if not row:
            raise Exception("Meeting ID not returned")
        meeting_id = row[0]
        conn.commit()
        cursor.close()
        conn.close()

        # --- Insert attendees pakai ORM ---
        attendees = data.get("attendees", [])
        for attendee in attendees:
            attendance = MeetingAttendance(
                meeting_id=meeting_id,
                employee_id=attendee.get("employee_id"),
                attendee_name=attendee.get("attendee_name"),
                attendee_email=attendee.get("attendee_email"),
                is_guest=attendee.get("is_guest", 0),
                registered_by=data["created_by"]
            )
            db.session.add(attendance)

        db.session.commit()

        return jsonify({"message": "Meeting created with attendees", "id": meeting_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@meetings_bp.route("/today", methods=["GET"])
def get_meetings_today():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        # Query meetings hari ini
        cursor.execute("""
            SELECT m.meeting_id,
                   m.meeting_title,
                   m.meeting_purpose,
                  CONVERT(VARCHAR(19), m.start_date_time, 120)   AS start_date_time,
                   CONVERT(VARCHAR(19), m.end_date_time, 120)   AS end_date_time,
                   m.room_id,
                   r.room_name,
                   r.location,
                   m.status_id,
                   s.status_name,
                   m.author_employee_id,
                   u.username AS author_name,
                   m.max_attendees,
                   m.meeting_notes,
                   m.created_by
            FROM dbo.meeting_mgn_meetings m
            JOIN dbo.meeting_mgn_meeting_rooms r
                 ON m.room_id = r.room_id
            JOIN dbo.meeting_mgn_meeting_status s
                 ON m.status_id = s.status_id
            LEFT JOIN dbo.meeting_mgnt_user u
                 ON m.author_employee_id = u.userid
            WHERE CAST(m.start_date_time AS DATE) = CAST(GETDATE() AS DATE)
            ORDER BY m.start_date_time ASC
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        meetings = []
        for row in rows:
            meeting = dict(zip(columns, row))
            meeting_id = meeting["meeting_id"]

            # Query attendance per meeting
            cursor.execute("""
    SELECT a.attendance_id,
           a.meeting_id,
           a.employee_id,
           e.employee_code,       -- ambil employee_code dari tabel employee
           a.attendee_name,
           a.attendee_email,
           a.check_in_time,
           a.check_out_time,
           a.registration_method,
           a.registered_by,
           a.notes,
           a.is_guest
    FROM dbo.meeting_mgn_meeting_attendance a
    LEFT JOIN dbo.employees e 
           ON a.employee_id = e.employee_id
                 WHERE a.meeting_id = ?
            """, (meeting_id,))
            attendance_columns = [col[0] for col in cursor.description]
            attendance_rows = cursor.fetchall()
            attendances = [dict(zip(attendance_columns, r)) for r in attendance_rows]

            meeting["attendances"] = attendances

            meetings.append(meeting)

        return jsonify(meetings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@meetings_bp.route("/daily-range", methods=["GET"])
def get_meetings_daily_range():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        # Query semua meeting dari 14 hari sebelum - 14 hari sesudah hari ini
        cursor.execute("""
            SELECT m.meeting_id,
                   m.meeting_title,
                   m.meeting_purpose,
                  CONVERT(VARCHAR(19), m.start_date_time, 120)   AS start_date_time,
                   CONVERT(VARCHAR(19), m.end_date_time, 120)   AS end_date_time,
                   m.room_id,
                   r.room_name,
                   m.status_id,
                   s.status_name,
                   m.author_employee_id,
                   u.username AS author_name,
                   m.max_attendees,
                   m.meeting_notes,
                   m.created_by
            FROM dbo.meeting_mgn_meetings m
            JOIN dbo.meeting_mgn_meeting_rooms r
                 ON m.room_id = r.room_id
            JOIN dbo.meeting_mgn_meeting_status s
                 ON m.status_id = s.status_id
            LEFT JOIN dbo.meeting_mgnt_user u
                 ON m.author_employee_id = u.userid
            WHERE 
                CAST(m.start_date_time AS DATE)
                BETWEEN DATEADD(DAY, -14, CAST(GETDATE() AS DATE))
                    AND DATEADD(DAY, 14, CAST(GETDATE() AS DATE))
            ORDER BY m.start_date_time ASC
        """)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        meetings = []
        for row in rows:
            meeting = dict(zip(columns, row))
            meeting_id = meeting["meeting_id"]

            # Query attendance per meeting
            cursor.execute("""
                SELECT a.attendance_id,
                       a.meeting_id,
                       a.employee_id,
                       e.employee_code,
                       a.attendee_name,
                       a.attendee_email,
                       a.check_in_time,
                       a.check_out_time,
                       a.registration_method,
                       a.registered_by,
                       a.notes,
                       a.is_guest
                FROM dbo.meeting_mgn_meeting_attendance a
                LEFT JOIN dbo.employees e 
                       ON a.employee_id = e.employee_id
                WHERE a.meeting_id = ?
            """, (meeting_id,))
            attendance_columns = [col[0] for col in cursor.description]
            attendance_rows = cursor.fetchall()
            attendances = [dict(zip(attendance_columns, r)) for r in attendance_rows]

            meeting["attendances"] = attendances
            meetings.append(meeting)

        return jsonify(meetings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()


@meetings_bp.route("/weekly", methods=["GET"])
def get_meetings_weekly():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        week_start_str = request.args.get("week_start")  # format YYYY-MM-DD

        # Memanggil SP di pyodbc
        cursor.execute("{CALL sp_get_meetings_weekly(?)}", [week_start_str or None])

        # Result set 1: meetings
        meetings_rows = cursor.fetchall()
        meetings_columns = [col[0] for col in cursor.description]
        meetings = [dict(zip(meetings_columns, r)) for r in meetings_rows]

        # Next result set: attendance
        if cursor.nextset():
            attendance_rows = cursor.fetchall()
            attendance_columns = [col[0] for col in cursor.description]
            attendances = [dict(zip(attendance_columns, r)) for r in attendance_rows]
        else:
            attendances = []

        # Gabungkan attendance ke masing-masing meeting
        for m in meetings:
            m["attendances"] = [a for a in attendances if a["meeting_id"] == m["meeting_id"]]

        return jsonify(meetings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@meetings_bp.route("/monthly", methods=["GET"])
def get_meetings_monthly():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        # Ambil parameter dari frontend (optional)
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)

        # --- Panggil stored procedure ---
        if month and year:
            cursor.execute("EXEC sp_get_meetings_monthly @month = ?, @year = ?", (month, year))
        else:
            cursor.execute("EXEC sp_get_meetings_monthly")

        # === Result set pertama: daftar meeting ===
        meetings_rows = cursor.fetchall()
        meetings_columns = [col[0] for col in cursor.description]
        meetings = [dict(zip(meetings_columns, row)) for row in meetings_rows]

        # === Result set kedua: daftar attendance ===
        # Pindah ke result set berikutnya
        if cursor.nextset():
            attendance_rows = cursor.fetchall()
            attendance_columns = [col[0] for col in cursor.description]
            attendances = [dict(zip(attendance_columns, row)) for row in attendance_rows]
        else:
            attendances = []

        # Gabungkan attendance ke masing-masing meeting
        for meeting in meetings:
            meeting_id = meeting["meeting_id"]
            meeting["attendances"] = [
                a for a in attendances if a["meeting_id"] == meeting_id
            ]

        return jsonify(meetings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()



@meetings_bp.route("/<int:meeting_id>", methods=["GET"])
def get_meeting_detail(meeting_id):
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        # Query meeting detail
        cursor.execute("""
            SELECT m.meeting_id,
                   m.meeting_title,
                   m.meeting_purpose,
                   CONVERT(VARCHAR(19), m.start_date_time, 120)   AS start_date_time,
                   CONVERT(VARCHAR(19), m.end_date_time, 120)   AS end_date_time,
                   m.room_id,
                   r.room_name,
                   r.location, 
                   m.author_employee_id,
                   u.username AS author_name,       -- ambil dari user
                   u.email AS author_email,
                   m.max_attendees,
                   m.meeting_notes,
                   m.created_by,
                   m.status_id,
                   s.status_name
            FROM dbo.meeting_mgn_meetings m
            JOIN dbo.meeting_mgn_meeting_rooms r
                 ON m.room_id = r.room_id
            JOIN dbo.meeting_mgnt_user u
                 ON m.author_employee_id = u.userid
            JOIN dbo.meeting_mgn_meeting_status s
                 ON m.status_id = s.status_id
            WHERE m.meeting_id = ?
        """, (meeting_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Meeting not found"}), 404

        columns = [col[0] for col in cursor.description]
        result = dict(zip(columns, row))

        # Query attendance untuk meeting ini
        cursor.execute("""
            SELECT attendance_id,
                   meeting_id,
                   employee_id,
                   attendee_name,
                   attendee_email,
                   check_in_time,
                   check_out_time,
                   registration_method,
                   registered_by,
                   notes,
                   is_guest
            FROM dbo.meeting_mgn_meeting_attendance
            WHERE meeting_id = ?
        """, (meeting_id,))
        
        attendance_columns = [col[0] for col in cursor.description]
        attendance_rows = cursor.fetchall()
        attendances = [dict(zip(attendance_columns, r)) for r in attendance_rows]

        # Tambahkan attendance ke result
        result["attendances"] = attendances

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@meetings_bp.route("/<int:meeting_id>", methods=["PUT"])
def update_meeting(meeting_id):
    data = request.json
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        # --- Update meeting via stored procedure ---
        cursor.execute("""
    EXEC dbo.meeting_mgn_update_meeting
        @meeting_id = ?,
        @meeting_title = ?,
        @meeting_purpose = ?,
        @start_date_time = ?,
        @end_date_time = ?,
        @room_id = ?,
        @author_employee_id = ?,
        @max_attendees = ?,
        @meeting_notes = ?,
        @status_id = ?,
        @updated_by = ?;
""", (
    meeting_id,
    data["meeting_title"],
    data.get("meeting_purpose"),
    data["start_date_time"],  
    data["end_date_time"],
    data["room_id"],
    data["author_employee_id"], 
    data.get("max_attendees"),
    data.get("meeting_notes"),
    data["status_id"],           
    data["updated_by"]           
))

        conn.commit()
        cursor.close()
        conn.close()

        # --- Handle attendees (replace all) ---
        # Hapus dulu semua attendees lama
        MeetingAttendance.query.filter_by(meeting_id=meeting_id).delete()

        # Tambahkan attendees baru
        attendees = data.get("attendees", [])
        for attendee in attendees:
            attendance = MeetingAttendance(
                meeting_id=meeting_id,
                employee_id=attendee.get("employee_id"),
                attendee_name=attendee.get("attendee_name"),
                attendee_email=attendee.get("attendee_email"),
                is_guest=attendee.get("is_guest", 0),
                registered_by=data["updated_by"]
            )
            db.session.add(attendance)

        db.session.commit()

        return jsonify({"message": "Meeting updated", "id": meeting_id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@meetings_bp.route("/<int:meeting_id>", methods=["DELETE"])
def delete_meeting(meeting_id):
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        # Hapus meeting langsung
        cursor.execute("""
            DELETE FROM dbo.meeting_mgn_meetings
            WHERE meeting_id = ?
        """, (meeting_id,))

        conn.commit()

        return jsonify({"message": f"Meeting {meeting_id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()

