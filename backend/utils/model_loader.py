import logging
import threading
import tensorflow as tf
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MODEL_PATH

_model = None
_model_lock = threading.Lock()


def get_model():
    """Load TensorFlow model lazily and cache it process-wide."""
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                logging.info("Loading TensorFlow model from %s", MODEL_PATH)
                _model = tf.keras.models.load_model(MODEL_PATH)
                logging.info("TensorFlow model loaded successfully")

    return _model
