from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from database.db import users_collection, history_collection, connections_collection
from utils.validators import ProfileSchema, parse_positive_int

user_bp = Blueprint("user", __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    email = get_jwt_identity()
    user = users_collection.find_one({"email": email}, {"password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["id"] = str(user.pop("_id"))
    return jsonify(user)


@user_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    payload = request.get_json(silent=True) or {}
    try:
        data = ProfileSchema().load(payload)
    except ValidationError as err:
        return jsonify({"error": str(err)}), 400

    if not data:
        return jsonify({"error": "No valid fields provided"}), 400

    users_collection.update_one({"email": get_jwt_identity()}, {"$set": data})
    return jsonify({"message": "Profile updated"})


@user_bp.route('/profile/history', methods=['GET'])
@jwt_required()
def profile_history():
    email = get_jwt_identity()
    page = parse_positive_int(request.args.get("page"), 1, 1, 100000)
    limit = parse_positive_int(request.args.get("limit"), 10, 1, 100)
    skip = (page - 1) * limit
    items = list(history_collection.find({"user": email}, {"_id": 0}).sort("_id", -1).skip(skip).limit(limit))
    total = history_collection.count_documents({"user": email})
    return jsonify({"items": items, "page": page, "limit": limit, "total": total})


@user_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    q = (request.args.get("q") or "").strip().lower()
    if len(q) < 3:
        return jsonify({"error": "Query too short"}), 400

    cursor = users_collection.find({"email": {"$regex": q}}, {"email": 1, "name": 1}).limit(20)
    out = [{"id": str(u["_id"]), "email": u.get("email", ""), "name": u.get("name", "")} for u in cursor]
    return jsonify(out)


@user_bp.route('/connections/request', methods=['POST'])
@jwt_required()
def send_connection_request():
    payload = request.get_json(silent=True) or {}
    target_id = payload.get("target_user_id", "")
    if not ObjectId.is_valid(target_id):
        return jsonify({"error": "Invalid target user id"}), 400

    me = users_collection.find_one({"email": get_jwt_identity()})
    if str(me["_id"]) == target_id:
        return jsonify({"error": "Cannot connect to yourself"}), 400

    target = users_collection.find_one({"_id": ObjectId(target_id)})
    if not target:
        return jsonify({"error": "Target user not found"}), 404

    doc = {"from_user": str(me["_id"]), "to_user": target_id, "status": "pending"}
    connections_collection.update_one({"from_user": doc["from_user"], "to_user": target_id}, {"$setOnInsert": doc}, upsert=True)
    return jsonify({"message": "Request sent"})


@user_bp.route('/connections/accept', methods=['POST'])
@jwt_required()
def accept_connection_request():
    payload = request.get_json(silent=True) or {}
    requester_id = payload.get("requester_user_id", "")
    if not ObjectId.is_valid(requester_id):
        return jsonify({"error": "Invalid requester user id"}), 400

    me = users_collection.find_one({"email": get_jwt_identity()})
    res = connections_collection.update_one(
        {"from_user": requester_id, "to_user": str(me["_id"]), "status": "pending"},
        {"$set": {"status": "accepted"}}
    )
    if res.matched_count == 0:
        return jsonify({"error": "No pending request found"}), 404
    return jsonify({"message": "Request accepted"})
