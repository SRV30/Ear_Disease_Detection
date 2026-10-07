from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    decode_token,
)
from extensions import limiter
import bcrypt
from database.db import users_collection, blacklist_collection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("5 per minute")
def signup():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    users_collection.insert_one({
        "email": email,
        "password": hashed
    })

    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = users_collection.find_one({"email": email})

    if not user or not bcrypt.checkpw(
        password.encode(),
        user["password"].encode()
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    })

@auth_bp.route("/refresh", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    token = create_access_token(identity=user)
    return jsonify({"access_token": token})

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    access_jti = get_jwt()["jti"]
    blacklist_collection.update_one(
        {"jti": access_jti},
        {"$set": {"jti": access_jti}},
        upsert=True,
    )

    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")

    if refresh_token:
        try:
            refresh_payload = decode_token(refresh_token)
            if refresh_payload.get("type") == "refresh":
                refresh_jti = refresh_payload["jti"]
                blacklist_collection.update_one(
                    {"jti": refresh_jti},
                    {"$set": {"jti": refresh_jti}},
                    upsert=True,
                )
        except Exception:
            # Logout should still revoke the current access token.
            pass

    return jsonify({"message": "Logged out"})
