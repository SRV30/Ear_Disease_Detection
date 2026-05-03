from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "../models/best_model.keras")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}

load_dotenv()

IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per day;50 per hour")
RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "10 per minute")
RATE_LIMIT_SIGNUP = os.getenv("RATE_LIMIT_SIGNUP", "5 per minute")
RATE_LIMIT_PREDICT = os.getenv("RATE_LIMIT_PREDICT", "20 per minute")
UPLOAD_RETENTION_HOURS = int(os.getenv("UPLOAD_RETENTION_HOURS", "24"))
