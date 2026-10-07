import argparse
import json
import os
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def analyze_image(path):
    with Image.open(path) as image:
        width, height = image.size
        rgb = np.asarray(image.convert("RGB"))

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    return {
        "width": width,
        "height": height,
        "pixels": width * height,
        "blur_score": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        "brightness": float(gray.mean()),
        "contrast": float(gray.std()),
    }


def collect_images(root):
    rows = []

    for dirpath, _, filenames in os.walk(root):
        for filename in sorted(filenames):
            if os.path.splitext(filename)[1].lower() not in IMAGE_EXTENSIONS:
                continue

            path = os.path.join(dirpath, filename)
            try:
                metrics = analyze_image(path)
                metrics["path"] = os.path.relpath(path, root)
                rows.append(metrics)
            except Exception as exc:
                rows.append({
                    "path": os.path.relpath(path, root),
                    "error": str(exc),
                })

    return rows


def summarize(rows):
    valid = [row for row in rows if "error" not in row]

    fields = ["width", "height", "pixels", "blur_score", "brightness", "contrast"]

    print(f"Images analyzed: {len(rows)}")
    print(f"Valid images: {len(valid)}")
    print(f"Invalid/unreadable: {len(rows) - len(valid)}")

    if not valid:
        return

    print("\nMetric distribution:")
    for field in fields:
        values = np.array([row[field] for row in valid], dtype=float)
        percentiles = np.percentile(values, [1, 5, 10, 25, 50, 75, 90, 95, 99])

        print(
            f"{field}: "
            f"min={values.min():.4f}, "
            f"p1={percentiles[0]:.4f}, "
            f"p5={percentiles[1]:.4f}, "
            f"p10={percentiles[2]:.4f}, "
            f"p25={percentiles[3]:.4f}, "
            f"median={percentiles[4]:.4f}, "
            f"p75={percentiles[5]:.4f}, "
            f"p90={percentiles[6]:.4f}, "
            f"p95={percentiles[7]:.4f}, "
            f"p99={percentiles[8]:.4f}, "
            f"max={values.max():.4f}"
        )


def summarize_by_class(rows):
    groups = defaultdict(list)

    for row in rows:
        if "error" not in row:
            parts = row["path"].replace("\\", "/").split("/")
            if len(parts) >= 2:
                groups[parts[0]].append(row)

    if not groups:
        return

    print("\nPer-class distribution:")
    for class_name in sorted(groups):
        group = groups[class_name]

        print(f"\n{class_name} ({len(group)} images)")
        for field in ["blur_score", "brightness", "contrast"]:
            values = np.array([row[field] for row in group], dtype=float)
            print(
                f"  {field}: "
                f"min={values.min():.4f}, "
                f"p5={np.percentile(values, 5):.4f}, "
                f"median={np.median(values):.4f}, "
                f"p95={np.percentile(values, 95):.4f}, "
                f"max={values.max():.4f}"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default="data/test",
        help="Directory containing images to analyze.",
    )
    parser.add_argument(
        "--output",
        default="evaluation/efficientnet_b0/image_quality_analysis.json",
    )
    args = parser.parse_args()

    rows = collect_images(args.data_dir)

    summarize(rows)
    summarize_by_class(rows)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(rows, file, indent=2)

    print(f"\nSaved: {args.output}")


if __name__ == "__main__":
    main()
