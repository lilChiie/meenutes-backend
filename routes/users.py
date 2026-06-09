from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from extensions import db
from models.user import User

users_bp = Blueprint("users", __name__)

@users_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "message": "Username not found"
        }), 404

    if not check_password_hash(
        user.password,
        password
    ):
        return jsonify({
            "message": "Incorrect password"
        }), 401

    token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role
        }
    }), 200

@users_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "admin")

    if not username:
        return jsonify({
            "message": "Username is required"
        }), 400

    if not name:
        return jsonify({
            "message": "Name is required"
        }), 400

    if not email:
        return jsonify({
            "message": "Email is required"
        }), 400

    if not password:
        return jsonify({
            "message": "Password is required"
        }), 400

    existing_user = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "message": "Username or email is already taken"
        }), 409

    try:
        user = User(
            username=username,
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "user_id": user.id
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": str(e)
        }), 500
    
@users_bp.route("/", methods=["GET"])
def get_users():

    users = User.query.all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }
        for user in users
    ]), 200

@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200