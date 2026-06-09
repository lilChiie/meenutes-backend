from flask import Blueprint, request, jsonify
from extensions import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.meeting_minutes import MeetingMinutes

meeting_minutes_bp = Blueprint(
    "meeting_minutes",
    __name__
)

@meeting_minutes_bp.route("/", methods=["GET"])
def get_minutes():

    minutes = MeetingMinutes.query.all()

    return jsonify([
        {
            "id": item.id,
            "title": item.title,
            "event_id": item.event_id,
            "event_division_id": item.event_division_id,
            "internal_division_id": item.internal_division_id,
            "meeting_date": item.meeting_date,
            "summary": item.summary,
            "created_by": item.created_by
        }
        for item in minutes
    ]), 200

@meeting_minutes_bp.route("/<int:id>", methods=["GET"])
def get_minute(id):

    minute = MeetingMinutes.query.get(id)

    if not minute:
        return jsonify({
            "message": "Meeting minutes not found"
        }), 404

    return jsonify({
        "id": minute.id,
        "title": minute.title,
        "event_id": minute.event_id,
        "event_division_id": minute.event_division_id,
        "internal_division_id": minute.internal_division_id,
        "meeting_date": minute.meeting_date,
        "transcript": minute.transcript,
        "summary": minute.summary,
        "created_by": minute.created_by,
        "created_at": minute.created_at
    }), 200

@meeting_minutes_bp.route("/", methods=["POST"])
@jwt_required()
def create_minutes():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    minute = MeetingMinutes(
        title=data.get("title"),
        event_id=data.get("event_id"),
        event_division_id=data.get("event_division_id"),
        internal_division_id=data.get("internal_division_id"),
        meeting_date=data.get("meeting_date"),
        transcript=data.get("transcript"),
        summary=data.get("summary"),
        created_by=current_user_id  
    )

    db.session.add(minute)
    db.session.commit()

    return jsonify({
        "message": "Meeting minutes created successfully",
        "id": minute.id
    }), 201

@meeting_minutes_bp.route("/<int:id>", methods=["PUT"])
def update_minutes(id):

    minute = MeetingMinutes.query.get(id)

    if not minute:
        return jsonify({
            "message": "Meeting minutes not found"
        }), 404

    data = request.get_json()

    minute.title = data.get(
        "title",
        minute.title
    )

    minute.meeting_date = data.get(
        "meeting_date",
        minute.meeting_date
    )

    minute.transcript = data.get(
        "transcript",
        minute.transcript
    )

    minute.summary = data.get(
        "summary",
        minute.summary
    )

    db.session.commit()

    return jsonify({
        "message": "Meeting minutes updated successfully"
    }), 200

@meeting_minutes_bp.route("/<int:id>", methods=["DELETE"])
def delete_minutes(id):

    minute = MeetingMinutes.query.get(id)

    if not minute:
        return jsonify({
            "message": "Meeting minutes not found"
        }), 404

    db.session.delete(minute)
    db.session.commit()

    return jsonify({
        "message": "Meeting minutes deleted successfully"
    }), 200

@meeting_minutes_bp.route("/event/<int:event_id>", methods=["GET"])
def get_minutes_by_event(event_id):

    minutes = MeetingMinutes.query.filter_by(
        event_id=event_id
    ).all()

    return jsonify([
        {
            "id": item.id,
            "title": item.title,
            "meeting_date": item.meeting_date
        }
        for item in minutes
    ])

@meeting_minutes_bp.route(
    "/event-division/<int:event_division_id>",
    methods=["GET"]
)
def get_minutes_by_event_division(
    event_division_id
):

    minutes = MeetingMinutes.query.filter_by(
        event_division_id=event_division_id
    ).all()

    return jsonify([
        {
            "id": item.id,
            "title": item.title,
            "meeting_date": item.meeting_date
        }
        for item in minutes
    ])

@meeting_minutes_bp.route(
    "/internal-division/<int:internal_division_id>",
    methods=["GET"]
)
def get_minutes_by_internal_division(
    internal_division_id
):

    minutes = MeetingMinutes.query.filter_by(
        internal_division_id=internal_division_id
    ).all()

    return jsonify([
        {
            "id": item.id,
            "title": item.title,
            "meeting_date": item.meeting_date
        }
        for item in minutes
    ])

@meeting_minutes_bp.route(
    "/internal",
    methods=["GET"]
)
def get_internal_minutes():

    minutes = MeetingMinutes.query.filter(
        MeetingMinutes.event_id.is_(None),
        MeetingMinutes.event_division_id.is_(None),
        MeetingMinutes.internal_division_id.is_(None)
    ).all()

    return jsonify([
        {
            "id": item.id,
            "title": item.title,
            "meeting_date": item.meeting_date,
            "summary": item.summary,
            "created_by": item.created_by
        }
        for item in minutes
    ]), 200

    #calendar

def serialize_row(row_dict):
    """Konversi datetime ke string agar JSON-serializable."""
    for field in ("meeting_date", "created_at"):
        if row_dict.get(field) and hasattr(row_dict[field], "isoformat"):
            row_dict[field] = row_dict[field].isoformat()
    return row_dict


# =============================================
# DAILY
# GET /meeting-minutes/daily?date=2026-06-06
# =============================================
@meeting_minutes_bp.route("/daily", methods=["GET"])
def get_daily_minutes():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        date_str = request.args.get("date")  # format YYYY-MM-DD, optional

        if date_str:
            cursor.execute("EXEC sp_MeetingMinutes_Daily @date = ?", (date_str,))
        else:
            cursor.execute("EXEC sp_MeetingMinutes_Daily")

        rows    = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data    = [serialize_row(dict(zip(columns, row))) for row in rows]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()


# =============================================
# WEEKLY
# GET /meeting-minutes/weekly?year=2026&week=23
# =============================================
@meeting_minutes_bp.route("/weekly", methods=["GET"])
def get_weekly_minutes():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        year = request.args.get("year", type=int)
        week = request.args.get("week", type=int)

        if year and week:
            cursor.execute("EXEC sp_MeetingMinutes_Weekly @year = ?, @week = ?", (year, week))
        else:
            cursor.execute("EXEC sp_MeetingMinutes_Weekly")

        rows    = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data    = [serialize_row(dict(zip(columns, row))) for row in rows]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()


# =============================================
# MONTHLY
# GET /meeting-minutes/monthly?year=2026&month=6
# =============================================
@meeting_minutes_bp.route("/monthly", methods=["GET"])
def get_monthly_minutes():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()

        month = request.args.get("month", type=int)
        year  = request.args.get("year",  type=int)

        if month and year:
            cursor.execute("EXEC sp_MeetingMinutes_Monthly @month = ?, @year = ?", (month, year))
        else:
            cursor.execute("EXEC sp_MeetingMinutes_Monthly")

        rows    = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data    = [serialize_row(dict(zip(columns, row))) for row in rows]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()