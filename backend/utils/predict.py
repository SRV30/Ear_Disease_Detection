import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import IMG_SIZE, CONFIDENCE_THRESHOLD
from utils.model_loader import get_model

class_names = [
    "Acute_Otitis_Media",
    "Cerumen_Impaction",
    "Chronic_Otitis_Media",
    "Myringosclerosis",
    "Normal"
]


def predict_image(img_path):
    model = get_model()

    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array)[0]

    predicted_class = class_names[np.argmax(preds)]
    confidence = float(np.max(preds)) * 100

    if confidence < CONFIDENCE_THRESHOLD:
        predicted_class = "Uncertain"

    return predicted_class, confidence, preds.tolist()
