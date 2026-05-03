from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import bcrypt
from database.db import users_collection, blacklist_collection
from marshmallow import ValidationError
from utils.validators import validate_auth_payload
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

    users_collection.insert_one({
        "email": email,
        "password": hashed
    })

    return jsonify({"message": "User created"})

@auth_bp.route("/login", methods=["POST"])
@limiter.limit(RATE_LIMIT_LOGIN)
def login():
    try:
        data = validate_auth_payload(request.get_json(silent=True))
    except ValidationError:
        return jsonify({"error": "Invalid credentials"}), 401

    email = data["email"]
    password = data["password"]

    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    })

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    token = create_access_token(identity=user)
    return jsonify({"access_token": token})

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist_collection.insert_one({"jti": jti})
    return jsonify({"message": "Logged out"})