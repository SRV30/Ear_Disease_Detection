from flask import Blueprint, jsonify
import json

from config import (
    MODEL_NAME,
    MODEL_VERSION,
    MODEL_FRAMEWORK,
    MODEL_ARCHITECTURE,
    MODEL_INPUT_SIZE,
    CALIBRATION_PATH,
)
from database.db import client
from utils.predict import TEMPERATURE, class_names, model

info_bp = Blueprint("info", __name__)


@info_bp.route("/health", methods=["GET"])
def health():
    database_status = "healthy"

    try:
        client.admin.command("ping")
    except Exception:
        database_status = "unavailable"

    model_status = "healthy" if model is not None else "unavailable"
    overall_status = (
        "healthy"
        if database_status == "healthy" and model_status == "healthy"
        else "degraded"
    )

    return jsonify({
        "status": overall_status,
        "service": "Ear Disease Detection API",
        "model": model_status,
        "database": database_status,
        "version": MODEL_VERSION,
    }), 200 if overall_status == "healthy" else 503


@info_bp.route("/model-info", methods=["GET"])
def model_info():
    calibration_available = False
    try:
        with open(CALIBRATION_PATH, "r", encoding="utf-8") as f:
            calibration_available = bool(json.load(f).get("temperature"))
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
        pass

    return jsonify({
        "name": MODEL_NAME,
        "version": MODEL_VERSION,
        "framework": MODEL_FRAMEWORK,
        "architecture": MODEL_ARCHITECTURE,
        "input_size": [MODEL_INPUT_SIZE, MODEL_INPUT_SIZE],
        "classes": class_names,
        "temperature_scaling": {
            "enabled": calibration_available,
            "temperature": TEMPERATURE if calibration_available else None,
        },
        "checkpoint": "models/efficientnet_b0_ear_disease.pth",
    })
