from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "../models/efficientnet_b0_ear_disease.pth")
CLASS_MAPPING_PATH = os.path.join(BASE_DIR, "../models/class_mapping.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
IMG_SIZE = 224

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
