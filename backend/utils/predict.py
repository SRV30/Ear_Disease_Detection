import json
import os
import sys

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import CLASS_MAPPING_PATH, IMG_SIZE, MODEL_PATH


NUM_CLASSES = 5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(model_path):
    model = efficientnet_b0(weights=None)

    num_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(num_features, NUM_CLASSES)

    checkpoint = torch.load(
        model_path,
        map_location=DEVICE,
        weights_only=True
    )

    model.load_state_dict(checkpoint)
    model.to(DEVICE)
    model.eval()

    return model


with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
    class_mapping = json.load(f)

class_names = [class_mapping[str(i)] for i in range(NUM_CLASSES)]

model = load_model(MODEL_PATH)

inference_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def predict_image(img_path):
    img = Image.open(img_path).convert("RGB")
    tensor = inference_transform(img).unsqueeze(0).to(DEVICE)

    with torch.inference_mode():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    predicted_index = int(torch.argmax(probs).item())
    predicted_class = class_names[predicted_index]
    confidence = float(probs[predicted_index].item()) * 100

    return predicted_class, confidence, probs.cpu().tolist()
