from flask import Blueprint, request, jsonify
from extensions import db

from models.event_division import EventDivision
from models.event import Event

event_divisions_bp = Blueprint(
    "event_divisions",
    __name__
)

@event_divisions_bp.route("/", methods=["GET"])
def get_event_divisions():

    divisions = EventDivision.query.all()

    return jsonify([
        {
            "id": division.id,
            "event_id": division.event_id,
            "name": division.name,
            "created_at": division.created_at
        }
        for division in divisions
    ]), 200

@event_divisions_bp.route("/<int:id>", methods=["GET"])
def get_event_division(id):

    division = EventDivision.query.get(id)

    if not division:
        return jsonify({
            "message": "Division not found"
        }), 404

    return jsonify({
        "id": division.id,
        "event_id": division.event_id,
        "name": division.name,
        "created_at": division.created_at
    }), 200

@event_divisions_bp.route("/event/<int:event_id>", methods=["GET"])
def get_divisions_by_event(event_id):

    divisions = EventDivision.query.filter_by(
        event_id=event_id
    ).all()

    return jsonify([
        {
            "id": division.id,
            "event_id": division.event_id,
            "name": division.name
        }
        for division in divisions
    ]), 200

@event_divisions_bp.route("/", methods=["POST"])
def create_event_division():

    data = request.get_json()

    event_id = data.get("event_id")
    name = data.get("name")

    if not event_id:
        return jsonify({
            "message": "event_id is required"
        }), 400

    if not name:
        return jsonify({
            "message": "name is required"
        }), 400

    event = Event.query.get(event_id)

    if not event:
        return jsonify({
            "message": "Event not found"
        }), 404

    division = EventDivision(
        event_id=event_id,
        name=name
    )

    db.session.add(division)
    db.session.commit()

    return jsonify({
        "message": "Division created successfully",
        "id": division.id
    }), 201

@event_divisions_bp.route("/<int:id>", methods=["PUT"])
def update_event_division(id):

    division = EventDivision.query.get(id)

    if not division:
        return jsonify({
            "message": "Division not found"
        }), 404

    data = request.get_json()

    division.name = data.get(
        "name",
        division.name
    )

    db.session.commit()

    return jsonify({
        "message": "Division updated successfully"
    }), 200

@event_divisions_bp.route("/<int:id>", methods=["DELETE"])
def delete_event_division(id):

    division = EventDivision.query.get(id)

    if not division:
        return jsonify({
            "message": "Division not found"
        }), 404

    db.session.delete(division)
    db.session.commit()

    return jsonify({
        "message": "Division deleted successfully"
    }), 200