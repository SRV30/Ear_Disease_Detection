from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import history_collection

history_bp = Blueprint("history", __name__)

@history_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user = get_jwt_identity()
    data = list(history_collection.find({"user": user}, {"_id": 0}))
    return jsonify(data[::-1])