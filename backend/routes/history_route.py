from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from bson.errors import InvalidId
import os

from database.db import history_collection
from config import UPLOAD_FOLDER
from extensions import limiter

history_bp = Blueprint("history", __name__)


def remove_history_files(record):
    for field in ("image_url", "heatmap_url"):
        url = record.get(field, "")
        filename = os.path.basename(url)

        if not filename:
            continue

        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass


@history_bp.route("/history", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def get_history():
    user = get_jwt_identity()
    records = list(
        history_collection.find(
            {"user": user},
            {"user": 0},
        ).sort("_id", -1)
    )

    for record in records:
        record["id"] = str(record.pop("_id"))
        record["created_at"] = ObjectId(record["id"]).generation_time.isoformat()

    return jsonify(records)


@history_bp.route("/history/<history_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("30 per minute")
def delete_history_item(history_id):
    user = get_jwt_identity()

    try:
        object_id = ObjectId(history_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid history id"}), 400

    record = history_collection.find_one({
        "_id": object_id,
        "user": user,
    })

    if not record:
        return jsonify({"error": "History item not found"}), 404

    history_collection.delete_one({"_id": object_id})
    remove_history_files(record)

    return jsonify({"message": "History item deleted"})


@history_bp.route("/history", methods=["DELETE"])
@jwt_required()
@limiter.limit("5 per minute")
def delete_all_history():
    user = get_jwt_identity()
    records = list(history_collection.find({"user": user}))

    result = history_collection.delete_many({"user": user})

    for record in records:
        remove_history_files(record)

    return jsonify({
        "message": "All history deleted",
        "deleted_count": result.deleted_count,
    })
