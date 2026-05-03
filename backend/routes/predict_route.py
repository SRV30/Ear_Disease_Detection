from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
import logging
from PIL import Image
from werkzeug.utils import secure_filename

from utils.predict import predict_image
from utils.model_loader import get_model
from utils.llm_agent import llm_analysis
from utils.gradcam import get_gradcam
from database.db import history_collection
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, RATE_LIMIT_PREDICT, UPLOAD_RETENTION_HOURS
from extensions import limiter
from utils.cleanup import cleanup_old_uploads

predict_bp = Blueprint("predict", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
@limiter.limit(RATE_LIMIT_PREDICT)
def predict():
    try:
        user = get_jwt_identity()

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename) or file.mimetype not in ALLOWED_MIME_TYPES:
            return jsonify({"error": "Invalid file type"}), 400

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            with Image.open(filepath) as img:
                img.verify()
        except Exception:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": "Invalid image content"}), 400

        cleanup_old_uploads(UPLOAD_FOLDER, retention_hours=UPLOAD_RETENTION_HOURS)

        symptoms = str(request.form.get("symptoms", "")).strip()[:500]

        prediction, confidence, probs = predict_image(filepath)

        logging.info(f"{user} → {prediction} ({confidence})")

        analysis = llm_analysis(prediction, confidence, symptoms)

        heatmap_path = get_gradcam(get_model(), filepath)

        data = {
            "user": user,
            "prediction": prediction,
            "confidence": confidence,
            "explanation": analysis["explanation"],
            "risk": analysis["risk"],
            "advice": analysis["advice"],
            "extra": analysis["extra"],
            "probabilities": probs,
            "image_url": f"/uploads/{filename}",
            "heatmap_url": f"/uploads/{os.path.basename(heatmap_path)}"
        }

        history_collection.insert_one(data)

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "explanation": analysis["explanation"],
            "risk": analysis["risk"],
            "advice": analysis["advice"],
            "extra": analysis["extra"],
            "probabilities": probs,
            "image_url": f"/uploads/{filename}",
            "heatmap_url": f"/uploads/{os.path.basename(heatmap_path)}"
        })

    except Exception:
        logging.exception("Prediction failed")
        return jsonify({
            "error": "Internal server error"
        }), 500