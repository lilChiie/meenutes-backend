from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.meeting_minutes import MeetingMinutes

transcription_bp = Blueprint('transcription', __name__)


@transcription_bp.route('/', methods=['POST'])
@jwt_required()
def create_minutes():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data.get('title'):
        return jsonify({"success": False, "error": "Title is required"}), 400
    if not data.get('meeting_date'):
        return jsonify({"success": False, "error": "Meeting date is required"}), 400

    minute = MeetingMinutes(
        title=data['title'],
        meeting_date=data['meeting_date'],
        event_id=data.get('event_id'),
        event_division_id=data.get('event_division_id'),
        internal_division_id=data.get('internal_division_id'),
        transcript=None,
        summary=None,
        created_by=current_user_id
    )
    db.session.add(minute)
    db.session.commit()

    return jsonify({"success": True, "message": "Meeting minutes created", "id": minute.id}), 201


@transcription_bp.route('/<int:minutes_id>/transcript', methods=['PATCH'])
@jwt_required()
def append_transcript(minutes_id):
    try:
        data = request.get_json()
        text = (data.get('text') or '').strip()

        if not text:
            return jsonify({"success": False, "error": "Field 'text' is required"}), 400

        minute = MeetingMinutes.query.get(minutes_id)
        if not minute:
            return jsonify({"success": False, "error": "Minutes not found"}), 404

        existing = minute.transcript or ""
        minute.transcript = (existing + " " + text).strip()
        db.session.commit()

        return jsonify({"success": True, "transcript": minute.transcript}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@transcription_bp.route('/<int:minutes_id>/summary', methods=['PATCH'])
@jwt_required()
def save_summary(minutes_id):
    try:
        data = request.get_json()
        summary = (data.get('summary') or '').strip()

        if not summary:
            return jsonify({"success": False, "error": "Field 'summary' is required"}), 400

        minute = MeetingMinutes.query.get(minutes_id)
        if not minute:
            return jsonify({"success": False, "error": "Minutes not found"}), 404

        minute.summary = summary
        db.session.commit()

        return jsonify({"success": True, "message": "Summary saved"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500