from flask import Blueprint, jsonify
from extensions import db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/summary", methods=["GET"])
def dashboard_summary():
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        cursor.execute("EXEC sp_dashboard_summary")

        row = cursor.fetchone()

        data = {
            "total_events": row[0],
            "total_minutes": row[1],
            "total_event_divisions": row[2],
            "total_internal_divisions": row[3],
            "daily_minutes": row[4],
            "weekly_minutes": row[5],
            "monthly_minutes": row[6]
        }

        cursor.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500
    
@dashboard_bp.route("/monthly-activity", methods=["GET"])
def dashboard_monthly_activity():
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        cursor.execute("EXEC sp_dashboard_monthly_activity")

        rows = cursor.fetchall()

        result = []

        for row in rows:
            result.append({
                "month_name": row[0],
                "total_minutes": row[1]
            })

        cursor.close()
        conn.close()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500