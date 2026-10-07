import argparse
import json
import os

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0


NUM_CLASSES = 5
CLASS_NAMES = [
    "Acute Otitis Media",
    "Cerumen Impaction",
    "Chronic Otitis Media",
    "Myringosclerosis",
    "Normal",
]
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def build_model():
    model = efficientnet_b0(weights=None)
    model.classifier[-1] = nn.Linear(
        model.classifier[-1].in_features,
        NUM_CLASSES,
    )
    return model


def predict_scores(model, image_path, transform, temperature, device):
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.inference_mode():
        logits = model(tensor)
        probabilities = torch.softmax(logits / temperature, dim=1)[0]

    confidence = float(probabilities.max().item())

    return {
        "max_softmax": confidence,
        "ood_score": 1.0 - confidence,
        "prediction": CLASS_NAMES[int(probabilities.argmax().item())],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Inspect OOD scores for a folder of images."
    )
    parser.add_argument("--data-dir", required=True)
    parser.add_argument(
        "--checkpoint",
        default="models/efficientnet_b0_ear_disease.pth",
    )
    parser.add_argument(
        "--calibration",
        default="models/temperature_scaling.json",
    )
    parser.add_argument(
        "--output",
        default="evaluation/ood_scores.json",
    )
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(args.calibration, "r", encoding="utf-8") as file:
        calibration = json.load(file)

    temperature = max(float(calibration.get("temperature", 1.0)), 0.05)

    model = build_model()
    checkpoint = torch.load(
        args.checkpoint,
        map_location=device,
        weights_only=True,
    )
    model.load_state_dict(checkpoint)
    model.to(device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    image_extensions = {".jpg", ".jpeg", ".png"}
    results = []

    for root, _, files in os.walk(args.data_dir):
        for filename in sorted(files):
            if os.path.splitext(filename)[1].lower() not in image_extensions:
                continue

            path = os.path.join(root, filename)
            result = predict_scores(
                model,
                path,
                transform,
                temperature,
                device,
            )
            result["image"] = os.path.relpath(path, args.data_dir)

            if args.threshold is not None:
                result["is_unknown"] = result["max_softmax"] < args.threshold

            results.append(result)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(
            {
                "method": "maximum_softmax_probability",
                "temperature": temperature,
                "threshold": args.threshold,
                "images": len(results),
                "results": results,
            },
            file,
            indent=2,
        )

    print(f"Images evaluated: {len(results)}")
    print(f"Temperature: {temperature:.6f}")

    if args.threshold is None:
        print("Threshold: not set; scores are reported only.")
    else:
        unknown = sum(item["is_unknown"] for item in results)
        print(f"Threshold: {args.threshold:.6f}")
        print(f"Rejected as unknown: {unknown}/{len(results)}")

    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
