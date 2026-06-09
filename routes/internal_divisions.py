from flask import Blueprint, request, jsonify
from extensions import db

from models.internal_divisions import InternalDivision
from models.user import User

internal_divisions_bp = Blueprint(
    "internal_divisions",
    __name__
)

@internal_divisions_bp.route("/", methods=["GET"])
def get_internal_divisions():

    divisions = InternalDivision.query.all()

    return jsonify([
        {
            "id": division.id,
            "user_id": division.user_id,
            "name": division.name,
            "created_at": division.created_at
        }
        for division in divisions
    ]), 200

@internal_divisions_bp.route("/<int:id>", methods=["GET"])
def get_internal_division(id):

    division = InternalDivision.query.get(id)

    if not division:
        return jsonify({
            "message": "Division not found"
        }), 404

    return jsonify({
        "id": division.id,
        "user_id": division.user_id,
        "name": division.name,
        "created_at": division.created_at
    }), 200

@internal_divisions_bp.route("/user/<int:user_id>", methods=["GET"])
def get_internal_divisions_by_user(user_id):

    divisions = InternalDivision.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify([
        {
            "id": division.id,
            "name": division.name
        }
        for division in divisions
    ]), 200

@internal_divisions_bp.route("/", methods=["POST"])
def create_internal_division():

    data = request.get_json()

    user_id = data.get("user_id")
    name = data.get("name")

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

    division = InternalDivision(
        user_id=user_id,
        name=name
    )

    db.session.add(division)
    db.session.commit()

    return jsonify({
        "message": "Internal division created successfully",
        "id": division.id
    }), 201

@internal_divisions_bp.route("/<int:id>", methods=["PUT"])
def update_internal_division(id):

    division = InternalDivision.query.get(id)

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

@internal_divisions_bp.route("/<int:id>", methods=["DELETE"])
def delete_internal_division(id):

    division = InternalDivision.query.get(id)

    if not division:
        return jsonify({
            "message": "Division not found"
        }), 404

    db.session.delete(division)
    db.session.commit()

    return jsonify({
        "message": "Division deleted successfully"
    }), 200