from flask import Blueprint, request, jsonify
from app import db

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/", methods=["GET"])
def get_employees():
    search = request.args.get("q", None)

    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("EXEC dbo.search_employees @search = ?", (search,))
        
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
