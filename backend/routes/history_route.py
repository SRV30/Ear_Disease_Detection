from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import history_collection
from utils.validators import parse_positive_int

history_bp = Blueprint("history", __name__)

@history_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user = get_jwt_identity()

    page = parse_positive_int(request.args.get("page"), default=1, minimum=1, maximum=100000)
    limit = parse_positive_int(request.args.get("limit"), default=10, minimum=1, maximum=100)
    skip = (page - 1) * limit

    cursor = history_collection.find({"user": user}, {"_id": 0}).sort("_id", -1).skip(skip).limit(limit)
    items = list(cursor)
    total = history_collection.count_documents({"user": user})

    return jsonify({"items": items, "page": page, "limit": limit, "total": total})
