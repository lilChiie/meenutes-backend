from flask import Blueprint, request, jsonify
from app import db

status_bp = Blueprint("status", __name__)

@status_bp.route("/", methods=["GET"])
def get_statuses():
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.status_id,
                s.status_name,
                s.status_description
            FROM dbo.meeting_mgn_meeting_status s
            ORDER BY s.status_id ASC
        """)
        rows = cursor.fetchall()

        # ambil nama kolom
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
