from flask import Blueprint, jsonify, request
from models import MeetingRoom
from app import db

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/", methods=["GET"])
def get_meeting_rooms():
    rooms = MeetingRoom.query.all()
    return jsonify([
        {
            "room_id": r.room_id,
            "room_name": r.room_name,
            "location": r.location,
            "capacity": r.capacity,
            "equipment": r.equipment,
            "is_active": r.is_active
        }
        for r in rooms
    ])

@rooms_bp.route("/", methods=["POST"])
def create_meeting_room():
    data = request.get_json()
    try:
        new_room = MeetingRoom(
            room_name=data.get("room_name"),
            location=data.get("location"),
            capacity=data.get("capacity"),
            equipment=data.get("equipment"),
            is_active=data.get("is_active", True)
        )
        db.session.add(new_room)
        db.session.commit()

        return jsonify({
            "message": "Meeting room created successfully",
            "room_id": new_room.room_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@rooms_bp.route("/<int:room_id>", methods=["PUT"])
def update_meeting_room(room_id):
    data = request.get_json()
    room = MeetingRoom.query.get(room_id)

    if not room:
        return jsonify({"error": "Room not found"}), 404

    try:
        room.room_name = data.get("room_name", room.room_name)
        room.location = data.get("location", room.location)
        room.capacity = data.get("capacity", room.capacity)
        room.equipment = data.get("equipment", room.equipment)
        room.is_active = data.get("is_active", room.is_active)

        db.session.commit()
        return jsonify({"message": "Meeting room updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
def delete_meeting_room(room_id):
    room = MeetingRoom.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    try:
        db.session.delete(room)
        db.session.commit()
        return jsonify({"message": "Meeting room deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400