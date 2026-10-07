import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument(
        "--checkpoint",
        default="models/efficientnet_b0_ear_disease.pth",
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/efficientnet_b0",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    test_dataset = datasets.ImageFolder(
        os.path.join(args.data_dir, "test"),
        transform=transform,
    )

    if test_dataset.classes != CLASS_NAMES:
        raise ValueError(
            f"Unexpected class order: {test_dataset.classes}. "
            f"Expected: {CLASS_NAMES}"
        )

    test_loader = DataLoader(
        test_dataset,
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
    y_pred = []
    y_prob = []

    with torch.inference_mode():
        for images, labels in test_loader:
            images = images.to(device)
            logits = model(images)
            probabilities = torch.softmax(logits, dim=1)
            predictions = probabilities.argmax(dim=1)

            y_true.extend(labels.numpy().tolist())
            y_pred.extend(predictions.cpu().numpy().tolist())
            y_prob.extend(probabilities.cpu().numpy().tolist())

    accuracy = accuracy_score(y_true, y_pred)
    balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
    macro_precision = precision_score(
        y_true, y_pred, average="macro", zero_division=0
    )
    macro_recall = recall_score(
        y_true, y_pred, average="macro", zero_division=0
    )
    macro_f1 = f1_score(
        y_true, y_pred, average="macro", zero_division=0
    )
    weighted_f1 = f1_score(
        y_true, y_pred, average="weighted", zero_division=0
    )

    report = classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred)

    results = {
        "model": "EfficientNet-B0",
        "checkpoint": args.checkpoint,
        "test_images": len(test_dataset),
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
    }

    with open(
        os.path.join(args.output_dir, "evaluation_results.json"),
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(results, file, indent=2)

    fig, ax = plt.subplots(figsize=(8, 7))
    image = ax.imshow(cm)
    fig.colorbar(image, ax=ax)

    ax.set(
        xticks=np.arange(NUM_CLASSES),
        yticks=np.arange(NUM_CLASSES),
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        xlabel="Predicted label",
        ylabel="True label",
        title="EfficientNet-B0 Confusion Matrix",
    )

    threshold = cm.max() / 2 if cm.size else 0

    for row in range(cm.shape[0]):
        for col in range(cm.shape[1]):
            ax.text(
                col,
                row,
                str(cm[row, col]),
                ha="center",
                va="center",
                color="white" if cm[row, col] > threshold else "black",
            )

    fig.tight_layout()
    fig.savefig(
        os.path.join(args.output_dir, "confusion_matrix.png"),
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)

    print(f"Test images: {len(test_dataset)}")
    print(f"Accuracy: {accuracy:.6f}")
    print(f"Balanced accuracy: {balanced_accuracy:.6f}")
    print(f"Macro precision: {macro_precision:.6f}")
    print(f"Macro recall: {macro_recall:.6f}")
    print(f"Macro F1: {macro_f1:.6f}")
    print(f"Weighted F1: {weighted_f1:.6f}")
    print(f"Results saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
