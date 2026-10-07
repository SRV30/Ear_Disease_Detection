from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "../models/efficientnet_b0_ear_disease.pth")
CLASS_MAPPING_PATH = os.path.join(BASE_DIR, "../models/class_mapping.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}
IMG_SIZE = 224

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
CALIBRATION_PATH = os.path.join(BASE_DIR, "../models/temperature_scaling.json")

# OOD rejection threshold selected from the current known/unknown evaluation set.
OOD_CONFIDENCE_THRESHOLD = 0.9998

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

RATE_LIMIT_STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
