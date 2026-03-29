import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MODEL_PATH, IMG_SIZE

model = tf.keras.models.load_model(MODEL_PATH)

class_names = [
    "Acute_Otitis_Media",
    "Cerumen_Impaction",
    "Chronic_Otitis_Media",
    "Myringosclerosis",
    "Normal"
]

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array)[0]

    predicted_class = class_names[np.argmax(preds)]
    confidence = float(np.max(preds)) * 100

    return predicted_class, confidence, preds.tolist()