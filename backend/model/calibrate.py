import argparse
import json
import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


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
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, NUM_CLASSES)
    return model


def collect_logits(model, loader, device):
    logits_all = []
    labels_all = []

    with torch.inference_mode():
        for images, labels in loader:
            logits_all.append(model(images.to(device)).cpu())
            labels_all.append(labels)

    return torch.cat(logits_all), torch.cat(labels_all)


def expected_calibration_error(logits, labels, bins=15):
    probabilities = torch.softmax(logits, dim=1)
    confidence, predictions = probabilities.max(dim=1)
    accuracies = predictions.eq(labels)

    ece = torch.zeros(1, dtype=torch.float64)
    boundaries = torch.linspace(0, 1, bins + 1)

    for lower, upper in zip(boundaries[:-1], boundaries[1:]):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            ece += (
                mask.float().mean().double()
                * (accuracies[mask].float().mean() - confidence[mask].mean()).abs().double()
            )

    return float(ece.item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--checkpoint", default="models/efficientnet_b0_ear_disease.pth")
    parser.add_argument("--output", default="models/temperature_scaling.json")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    val_dataset = datasets.ImageFolder(
        os.path.join(args.data_dir, "val"),
        transform=transform,
    )

    if val_dataset.classes != CLASS_NAMES:
        raise ValueError(
            f"Unexpected class order: {val_dataset.classes}. Expected: {CLASS_NAMES}"
        )

    loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
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

    logits, labels = collect_logits(model, loader, device)

    temperature = nn.Parameter(torch.ones(1))
    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.LBFGS(
        [temperature],
        lr=0.01,
        max_iter=100,
        line_search_fn="strong_wolfe",
    )

    def closure():
        optimizer.zero_grad()
        loss = criterion(logits / temperature.clamp_min(0.05), labels)
        loss.backward()
        return loss

    optimizer.step(closure)

    fitted_temperature = float(temperature.detach().clamp_min(0.05).item())

    uncalibrated_nll = float(criterion(logits, labels).item())
    calibrated_nll = float(
        criterion(logits / fitted_temperature, labels).item()
    )
    uncalibrated_ece = expected_calibration_error(logits, labels)
    calibrated_ece = expected_calibration_error(
        logits / fitted_temperature,
        labels,
    )

    result = {
        "method": "temperature_scaling",
        "temperature": fitted_temperature,
        "calibration_set": "validation",
        "validation_images": len(val_dataset),
        "uncalibrated_nll": uncalibrated_nll,
        "calibrated_nll": calibrated_nll,
        "uncalibrated_ece": uncalibrated_ece,
        "calibrated_ece": calibrated_ece,
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(f"Validation images: {len(val_dataset)}")
    print(f"Temperature: {fitted_temperature:.6f}")
    print(f"Uncalibrated NLL: {uncalibrated_nll:.6f}")
    print(f"Calibrated NLL: {calibrated_nll:.6f}")
    print(f"Uncalibrated ECE: {uncalibrated_ece:.6f}")
    print(f"Calibrated ECE: {calibrated_ece:.6f}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
