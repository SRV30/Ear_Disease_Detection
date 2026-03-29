from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
import logging
from werkzeug.utils import secure_filename

from utils.predict import predict_image, model
from utils.llm_agent import llm_analysis
from utils.gradcam import get_gradcam
from database.db import history_collection
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

predict_bp = Blueprint("predict", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        user = get_jwt_identity()

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        symptoms = request.form.get("symptoms", "")

        prediction, confidence, probs = predict_image(filepath)

        logging.info(f"{user} → {prediction} ({confidence})")

        analysis = llm_analysis(prediction, confidence, symptoms)

        heatmap_path = get_gradcam(model, filepath)

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

    except Exception as e:
        logging.exception("Prediction failed")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500