import argparse
import json
import os

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
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


def get_gradcam(model, tensor, class_index):
    activations = []
    gradients = []
    target_layer = model.features[-1]

    def forward_hook(_, __, output):
        activations.append(output)

    def backward_hook(_, __, grad_output):
        gradients.append(grad_output[0])

    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_full_backward_hook(backward_hook)

    try:
        model.zero_grad(set_to_none=True)
        logits = model(tensor)
        score = logits[0, class_index]
        score.backward()

        activation = activations[0]
        gradient = gradients[0]
        weights = gradient.mean(dim=(2, 3), keepdim=True)

        cam = (weights * activation).sum(dim=1).squeeze(0)
        cam = torch.relu(cam)

        maximum = cam.max()
        if maximum.item() > 0:
            cam = cam / maximum

        return cam.detach().cpu().numpy()
    finally:
        forward_handle.remove()
        backward_handle.remove()


def normalized_tensor(image_array, transform, device):
    image = Image.fromarray(image_array)
    return transform(image).unsqueeze(0).to(device)


def mask_top_fraction(image, cam, fraction):
    height, width = image.shape[:2]
    resized = cv2.resize(cam, (width, height), interpolation=cv2.INTER_LINEAR)

    count = max(1, int(resized.size * fraction))
    threshold = np.partition(resized.reshape(-1), -count)[-count]
    mask = resized >= threshold

    # Replace highlighted pixels with ImageNet mean RGB rather than black.
    output = image.copy()
    mean_rgb = np.array([123.675, 116.28, 103.53], dtype=np.uint8)
    output[mask] = mean_rgb

    return output


def evaluate(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    dataset = datasets.ImageFolder(
        os.path.join(args.data_dir, "test"),
        transform=None,
    )

    if dataset.classes != CLASS_NAMES:
        raise ValueError(
            f"Unexpected class order: {dataset.classes}. Expected: {CLASS_NAMES}"
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

    fractions = [0.10, 0.20, 0.30, 0.50]
    totals = {
        str(fraction): {
            "baseline_probability": 0.0,
            "masked_probability": 0.0,
            "probability_drop": 0.0,
            "relative_drop": 0.0,
            "random_probability_drop": 0.0,
        }
        for fraction in fractions
    }

    processed = 0
    prediction_changes = {str(fraction): 0 for fraction in fractions}

    for path, true_class in dataset.samples:
        with Image.open(path) as image:
            image = np.asarray(image.convert("RGB"))

        tensor = normalized_tensor(image, transform, device)

        with torch.inference_mode():
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = int(probabilities.argmax(dim=1).item())
            baseline_probability = float(probabilities[0, predicted_class].item())

        cam_tensor = normalized_tensor(image, transform, device)
        cam = get_gradcam(model, cam_tensor, predicted_class)

        rng = np.random.default_rng(42 + processed)

        for fraction in fractions:
            masked = mask_top_fraction(image, cam, fraction)
            masked_tensor = normalized_tensor(masked, transform, device)

            with torch.inference_mode():
                masked_probabilities = torch.softmax(
                    model(masked_tensor), dim=1
                )
                masked_probability = float(
                    masked_probabilities[0, predicted_class].item()
                )
                masked_prediction = int(masked_probabilities.argmax(dim=1).item())

            drop = baseline_probability - masked_probability
            relative_drop = drop / max(baseline_probability, 1e-12)

            # Random baseline with the same mask size.
            random_cam = rng.random(cam.shape, dtype=np.float32)
            random_masked = mask_top_fraction(image, random_cam, fraction)
            random_tensor = normalized_tensor(
                random_masked, transform, device
            )

            with torch.inference_mode():
                random_probabilities = torch.softmax(
                    model(random_tensor), dim=1
                )
                random_drop = baseline_probability - float(
                    random_probabilities[0, predicted_class].item()
                )

            key = str(fraction)
            totals[key]["baseline_probability"] += baseline_probability
            totals[key]["masked_probability"] += masked_probability
            totals[key]["probability_drop"] += drop
            totals[key]["relative_drop"] += relative_drop
            totals[key]["random_probability_drop"] += random_drop

            if masked_prediction != predicted_class:
                prediction_changes[key] += 1

        processed += 1

        if processed % 50 == 0:
            print(f"Processed: {processed}/{len(dataset)}")

    results = {
        "model": "EfficientNet-B0",
        "test_images": processed,
        "method": (
            "Grad-CAM faithfulness by deletion: replace the highest-"
            "attribution pixels with ImageNet mean RGB and measure the "
            "predicted-class probability drop. A random same-size mask "
            "is used as a baseline."
        ),
        "fractions": {},
    }

    for fraction in fractions:
        key = str(fraction)
        averages = {
            metric: value / processed
            for metric, value in totals[key].items()
        }

        results["fractions"][key] = {
            **averages,
            "prediction_change_rate": prediction_changes[key] / processed,
            "faithfulness_gain_over_random": (
                averages["probability_drop"]
                - averages["random_probability_drop"]
            ),
        }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"Test images: {processed}")
    for fraction in fractions:
        key = str(fraction)
        result = results["fractions"][key]
        print(
            f"Top {int(fraction * 100):2d}% | "
            f"drop={result['probability_drop']:.6f} | "
            f"random_drop={result['random_probability_drop']:.6f} | "
            f"gain={result['faithfulness_gain_over_random']:.6f} | "
            f"prediction_change={result['prediction_change_rate']:.4f}"
        )

    print(f"Saved: {args.output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument(
        "--checkpoint",
        default="models/efficientnet_b0_ear_disease.pth",
    )
    parser.add_argument(
        "--output",
        default="evaluation/efficientnet_b0/gradcam_quantitative_results.json",
    )
    args = parser.parse_args()
    evaluate(args)


if __name__ == "__main__":
    main()
