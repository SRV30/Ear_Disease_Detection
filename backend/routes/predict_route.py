from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError

from utils.predict import predict_image, model
from utils.llm_agent import llm_analysis
from utils.gradcam import get_gradcam
from database.db import history_collection
from config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_IMAGE_PIXELS,
    OOD_CONFIDENCE_THRESHOLD,
)
from extensions import limiter

predict_bp = Blueprint("predict", __name__)

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_image(file):
    if not allowed_file(file.filename):
        raise ValueError("Invalid image file type.")

    if file.mimetype not in ALLOWED_MIME_TYPES:
        raise ValueError("Only JPEG and PNG images are supported.")

    try:
        file.stream.seek(0)
        with Image.open(file.stream) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ValueError("Uploaded file is not a valid JPEG or PNG image.")

            width, height = image.size
            if width <= 0 or height <= 0:
                raise ValueError("Invalid image dimensions.")

            if width * height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions are too large.")

            image.verify()

        file.stream.seek(0)
        with Image.open(file.stream) as image:
            image.load()

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("Uploaded file is not a valid image.") from exc
    finally:
        file.stream.seek(0)


def get_owned_media(user, filename):
    if not secure_filename(filename) or secure_filename(filename) != filename:
        return None

    return history_collection.find_one(
        {
            "user": user,
            "$or": [
                {"image_url": f"/media/{filename}"},
                {"heatmap_url": f"/media/{filename}"},
                {"image_url": f"/uploads/{filename}"},
                {"heatmap_url": f"/uploads/{filename}"},
            ],
        }
    )


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def predict():
    filepath = None
    heatmap_path = None

    try:
        user = get_jwt_identity()

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        try:
            validate_image(file)
        except ValueError as exc:
            return jsonify({"error": "Invalid image", "message": str(exc)}), 400

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        symptoms = request.form.get("symptoms", "")

        prediction, confidence, probs = predict_image(filepath)

        logging.info("%s -> %s (%.4f)", user, prediction, confidence)

        # Reject images whose calibrated maximum class probability is below
        # the empirically selected OOD threshold. Do this before LLM analysis
        # or Grad-CAM so unsupported images are not presented as diagnoses.
        if confidence / 100.0 < OOD_CONFIDENCE_THRESHOLD:
            # OOD results are intentionally not persisted in patient history.
            # The uploaded file is also removed because it is not associated
            # with a history record and therefore should not remain in storage.
            response = {
                "prediction": "Unknown / Unsupported Image",
                "confidence": round(confidence, 4),
                "explanation": "The uploaded image is not sufficiently similar to the supported otoscopic ear-image classes.",
                "risk": "Unsupported image",
                "advice": "Please upload a clear otoscopic image of the ear belonging to one of the supported classes.",
                "extra": "This image was rejected by the model's unknown-image screening step and should not be interpreted as a diagnosis.",
                "probabilities": probs,
                "image_url": None,
                "heatmap_url": None,
                "ood_rejected": True,
            }

            if filepath and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    logging.warning("Could not remove rejected OOD image: %s", filepath)

            filepath = None
            return jsonify(response), 200

        analysis = llm_analysis(prediction, confidence, symptoms)

        heatmap_path = get_gradcam(model, filepath)
        heatmap_filename = os.path.basename(heatmap_path)

        data = {
            "user": user,
            "prediction": prediction,
            "confidence": confidence,
            "explanation": analysis["explanation"],
            "risk": analysis["risk"],
            "advice": analysis["advice"],
            "extra": analysis["extra"],
            "probabilities": probs,
            "image_url": f"/media/{filename}",
            "heatmap_url": f"/media/{heatmap_filename}",
        }

        history_collection.insert_one(data)

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "explanation": analysis["explanation"],
            "risk": analysis["risk"],
            "advice": analysis["advice"],
            "extra": analysis["extra"],
            "probabilities": probs,
            "image_url": f"/media/{filename}",
            "heatmap_url": f"/media/{heatmap_filename}",
        })

    except Exception as exc:
        logging.exception("Prediction failed")

        for path in (heatmap_path, filepath):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    logging.warning("Could not remove temporary file: %s", path)

        return jsonify({
            "error": "Internal server error",
            "message": "Prediction could not be completed."
        }), 500


@predict_bp.route("/media/<filename>", methods=["GET"])
@jwt_required()
@limiter.limit("60 per minute")
def protected_media(filename):
    user = get_jwt_identity()

    if not get_owned_media(user, filename):
        return jsonify({"error": "Media not found"}), 404

    return send_from_directory(UPLOAD_FOLDER, filename)
