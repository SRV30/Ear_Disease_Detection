import argparse
import os

from utils.image_quality import check_image_quality


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/test")
    args = parser.parse_args()

    total = 0
    passed = 0
    failed = []

    for root, _, files in os.walk(args.data_dir):
        for filename in files:
            if os.path.splitext(filename)[1].lower() not in IMAGE_EXTENSIONS:
                continue

            path = os.path.join(root, filename)
            total += 1

            try:
                quality_ok, message = check_image_quality(path)
            except Exception as exc:
                quality_ok = False
                message = f"Exception: {exc}"

            if quality_ok:
                passed += 1
            else:
                failed.append((os.path.relpath(path, args.data_dir), message))

    print(f"Test images: {total}")
    print(f"Passed quality checks: {passed}")
    print(f"Rejected: {len(failed)}")

    if failed:
        print("\nRejected images:")
        for path, message in failed:
            print(f"- {path}: {message}")

        raise SystemExit(1)

    print("All test images passed the configured quality thresholds.")


if __name__ == "__main__":
    main()
