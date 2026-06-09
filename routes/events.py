from flask import Blueprint, request, jsonify
from extensions import db

from models.event import Event
from models.user import User

events_bp = Blueprint(
    "events",
    __name__
)

@events_bp.route("/", methods=["GET"])
def get_events():

    events = Event.query.all()

    return jsonify([
        {
            "id": event.id,
            "user_id": event.user_id,
            "name": event.name,
            "description": event.description,
            "event_date": event.event_date,
            "created_at": event.created_at
        }
        for event in events
    ]), 200

@events_bp.route("/<int:id>", methods=["GET"])
def get_event(id):

    event = Event.query.get(id)

    if not event:
        return jsonify({
            "message": "Event not found"
        }), 404

    return jsonify({
        "id": event.id,
        "user_id": event.user_id,
        "name": event.name,
        "description": event.description,
        "event_date": event.event_date,
        "created_at": event.created_at
    }), 200

@events_bp.route("/user/<int:user_id>", methods=["GET"])
def get_events_by_user(user_id):

    events = Event.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify([
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "event_date": event.event_date,
            "created_at": event.created_at
        }
        for event in events
    ]), 200

@events_bp.route("/", methods=["POST"])
def create_event():

    data = request.get_json()

    user_id = data.get("user_id")
    name = data.get("name")
    description = data.get("description")
    event_date = data.get("event_date")


    if not user_id:
        return jsonify({
            "message": "user_id is required"
        }), 400

    if not name:
        return jsonify({
            "message": "name is required"
        }), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    event = Event(
        user_id=user_id,
        name=name,
        description=description,
        event_date=event_date
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "Event created successfully",
        "id": event.id
    }), 201

@events_bp.route("/<int:id>", methods=["PUT"])
def update_event(id):

    event = Event.query.get(id)

    if not event:
        return jsonify({
            "message": "Event not found"
        }), 404

    data = request.get_json()

    event.name = data.get(
        "name",
        event.name
    )

    event.description = data.get(
        "description",
        event.description
    )

    event.event_date = data.get(
        "event_date",
        event.event_date
    )

    db.session.commit()

    return jsonify({
        "message": "Event updated successfully"
    }), 200

@events_bp.route("/<int:id>", methods=["DELETE"])
def delete_event(id):

    event = Event.query.get(id)

    if not event:
        return jsonify({
            "message": "Event not found"
        }), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({
        "message": "Event deleted successfully"
    }), 200