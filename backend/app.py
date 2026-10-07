from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging
from flask_jwt_extended import JWTManager
from database.db import blacklist_collection
from extensions import limiter
from config import (
    UPLOAD_FOLDER,
    JWT_SECRET_KEY,
    MAX_UPLOAD_SIZE,
    CORS_ORIGINS,
    RATE_LIMIT_STORAGE_URI,
)
from routes.predict_route import predict_bp
from routes.history_route import history_bp
from routes.auth_route import auth_bp

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

limiter._storage_uri = RATE_LIMIT_STORAGE_URI
limiter.init_app(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 900
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400

jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return blacklist_collection.find_one({"jti": jti}) is not None

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return {
        "message": "Ear Disease Detection API Running",
        "status": "healthy"
    }

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    # Uploads are intentionally not served through this legacy route.
    return jsonify({"error": "Use an authenticated media endpoint"}), 403

@app.errorhandler(413)
def request_too_large(e):
    return jsonify({
        "error": "File too large",
        "message": "Maximum upload size is 50 MB."
    }), 413

@app.errorhandler(404)
def not_found(e):
    return {"error": "Route not found"}, 404

@app.errorhandler(429)
def rate_limited(e):
    return jsonify({
        "error": "Too many requests",
        "message": "Please try again later."
    }), 429

@app.errorhandler(500)
def server_error(e):
    logging.error(str(e))
    return {"error": "Internal server error"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
