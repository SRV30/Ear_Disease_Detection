from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from database.db import users_collection, blacklist_collection, password_reset_collection
from utils.validators import validate_auth_payload, ForgotPasswordSchema, ResetPasswordSchema, PASSWORD_RE
from config import RATE_LIMIT_LOGIN, RATE_LIMIT_SIGNUP
from extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
@limiter.limit(RATE_LIMIT_SIGNUP)
def signup():
    try:
        data = validate_auth_payload(request.get_json(silent=True))
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400

    email = data["email"]
    password = data["password"]

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users_collection.insert_one({"email": email, "password": hashed, "name": "", "avatar": ""})

    return jsonify({"message": "User created"})


@auth_bp.route("/login", methods=["POST"])
@limiter.limit(RATE_LIMIT_LOGIN)
def login():
    try:
        data = validate_auth_payload(request.get_json(silent=True))
    except ValidationError:
        return jsonify({"error": "Invalid credentials"}), 401

    user = users_collection.find_one({"email": data["email"]})
    if not user or not bcrypt.checkpw(data["password"].encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "access_token": create_access_token(identity=data["email"]),
        "refresh_token": create_refresh_token(identity=data["email"])
    })


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    return jsonify({"access_token": create_access_token(identity=get_jwt_identity())})


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per hour")
def forgot_password():
    payload = request.get_json(silent=True) or {}
    try:
        data = ForgotPasswordSchema().load(payload)
    except ValidationError:
        return jsonify({"message": "If the email exists, a reset link has been sent"}), 200

    email = data["email"].strip().lower()
    user = users_collection.find_one({"email": email})
    if user:
        token = secrets.token_urlsafe(32)
        password_reset_collection.insert_one({
            "email": email,
            "token": token,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
            "used": False
        })
        # Integrate your SMTP provider here; do not return token in production.
    return jsonify({"message": "If the email exists, a reset link has been sent"}), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("10 per hour")
def reset_password():
    payload = request.get_json(silent=True) or {}
    try:
        data = ResetPasswordSchema().load(payload)
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400

    token_doc = password_reset_collection.find_one({"token": data["token"], "used": False})
    if not token_doc or token_doc["expires_at"] < datetime.now(timezone.utc):
        return jsonify({"error": "Invalid or expired token"}), 400

    if not PASSWORD_RE.match(data["password"]):
        return jsonify({"error": "Weak password"}), 400

    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    users_collection.update_one({"email": token_doc["email"]}, {"$set": {"password": hashed}})
    password_reset_collection.update_one({"_id": token_doc["_id"]}, {"$set": {"used": True}})
    return jsonify({"message": "Password reset successful"})


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    blacklist_collection.insert_one({"jti": get_jwt()["jti"]})
    return jsonify({"message": "Logged out"})
