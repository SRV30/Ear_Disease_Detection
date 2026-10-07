import argparse
import json
import os

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import log_loss
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import efficientnet_b0


NUM_CLASSES = 5
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def build_model():
    model = efficientnet_b0(weights=None)
    model.classifier[-1] = nn.Linear(
        model.classifier[-1].in_features,
        NUM_CLASSES,
    )
    return model


def expected_calibration_error(y_true, probabilities, bins=15):
    confidences = probabilities.max(axis=1)
    predictions = probabilities.argmax(axis=1)
    accuracies = predictions == y_true

    ece = 0.0
    for lower, upper in zip(
        np.linspace(0.0, 1.0, bins + 1)[:-1],
        np.linspace(0.0, 1.0, bins + 1)[1:],
    ):
        mask = (confidences > lower) & (confidences <= upper)
        if not np.any(mask):
            continue

        ece += (
            mask.mean()
            * abs(
                accuracies[mask].mean()
                - confidences[mask].mean()
            )
        )

    return float(ece)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
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
        default="evaluation/efficientnet_b0/calibration_test_results.json",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(args.calibration, "r", encoding="utf-8") as file:
        calibration = json.load(file)

    temperature = max(
        float(calibration.get("temperature", 1.0)),
        0.05,
    )

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    dataset = datasets.ImageFolder(
        os.path.join(args.data_dir, "test"),
        transform=transform,
    )

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    model = build_model()
    checkpoint = torch.load(
        args.checkpoint,
        map_location=device,
        weights_only=True,
    )
    model.load_state_dict(checkpoint)
    model.to(device)
    model.eval()

    y_true = []
    logits_all = []

    with torch.inference_mode():
        for images, labels in loader:
            logits = model(images.to(device))
            logits_all.append(logits.cpu())
            y_true.extend(labels.tolist())

    logits = torch.cat(logits_all).numpy()
    y_true = np.asarray(y_true)

    uncalibrated = torch.softmax(
        torch.from_numpy(logits),
        dim=1,
    ).numpy()

    calibrated = torch.softmax(
        torch.from_numpy(logits) / temperature,
        dim=1,
    ).numpy()

    uncalibrated_nll = log_loss(
        y_true,
        uncalibrated,
        labels=list(range(NUM_CLASSES)),
    )
    calibrated_nll = log_loss(
        y_true,
        calibrated,
        labels=list(range(NUM_CLASSES)),
    )

    uncalibrated_ece = expected_calibration_error(
        y_true,
        uncalibrated,
    )
    calibrated_ece = expected_calibration_error(
        y_true,
        calibrated,
    )

    results = {
        "model": "EfficientNet-B0",
        "test_images": len(dataset),
        "temperature": temperature,
        "calibration_fit_set": calibration.get(
            "calibration_set",
            "validation",
        ),
        "uncalibrated": {
            "nll": uncalibrated_nll,
            "ece_15_bins": uncalibrated_ece,
        },
        "calibrated": {
            "nll": calibrated_nll,
            "ece_15_bins": calibrated_ece,
        },
        "interpretation": (
            "Temperature was fitted on validation data and evaluated "
            "without refitting on the untouched test set."
        ),
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"Test images: {len(dataset)}")
    print(f"Temperature: {temperature:.6f}")
    print(f"Uncalibrated NLL: {uncalibrated_nll:.8f}")
    print(f"Calibrated NLL: {calibrated_nll:.8f}")
    print(f"Uncalibrated ECE: {uncalibrated_ece:.8f}")
    print(f"Calibrated ECE: {calibrated_ece:.8f}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
