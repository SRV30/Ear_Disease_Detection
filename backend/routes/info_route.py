from flask import Blueprint, jsonify
import json

from config import (
    MODEL_NAME,
    MODEL_VERSION,
    MODEL_FRAMEWORK,
    MODEL_ARCHITECTURE,
    MODEL_INPUT_SIZE,
    CLASS_MAPPING_PATH,
    CALIBRATION_PATH,
)
from utils.predict import TEMPERATURE, class_names

info_bp = Blueprint("info", __name__)


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
