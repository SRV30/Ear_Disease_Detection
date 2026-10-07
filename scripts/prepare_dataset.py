import argparse
import hashlib
import json
import os
import random
import shutil
from collections import defaultdict

import imagehash
from PIL import Image


CLASSES = [
    "Acute Otitis Media",
    "Cerumen Impaction",
    "Chronic Otitis Media",
    "Myringosclerosis",
    "Normal",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_images(raw_dir):
    images = []

    for class_name in CLASSES:
        class_dir = os.path.join(raw_dir, class_name)
        if not os.path.isdir(class_dir):
            raise FileNotFoundError(f"Missing class directory: {class_dir}")

        for name in sorted(os.listdir(class_dir)):
            path = os.path.join(class_dir, name)
            if (
                os.path.isfile(path)
                and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
            ):
                images.append(
                    {
                        "path": path,
                        "class_name": class_name,
                        "class_id": CLASSES.index(class_name),
                        "filename": name,
                    }
                )

    return images


def remove_exact_duplicates(images):
    seen = {}
    unique = []
    duplicate_count = 0

    for item in images:
        digest = sha256_file(item["path"])

        if digest in seen:
            duplicate_count += 1
            continue

        seen[digest] = item["path"]
        item["sha256"] = digest
        unique.append(item)

    return unique, duplicate_count


def build_phash_groups(images, threshold):
    hashes = []

    for item in images:
        with Image.open(item["path"]) as image:
            image = image.convert("RGB")
            hashes.append(imagehash.phash(image))

    uf = UnionFind(len(images))

    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            if hashes[i] - hashes[j] <= threshold:
                uf.union(i, j)

    groups = defaultdict(list)
    for index in range(len(images)):
        groups[uf.find(index)].append(index)

    return list(groups.values())


def group_stats(groups, images):
    stats = []

    for group_id, indexes in enumerate(groups):
        counts = [0] * len(CLASSES)
        for index in indexes:
            counts[images[index]["class_id"]] += 1

        stats.append(
            {
                "group_id": group_id,
                "indexes": indexes,
                "size": len(indexes),
                "class_counts": counts,
            }
        )

    return stats


def assign_groups(stats, targets, seed):
    rng = random.Random(seed)
    stats = stats[:]

    # Larger groups are placed first. A small random component makes the
    # deterministic tie-breaking less dependent on filesystem ordering.
    rng.shuffle(stats)
    stats.sort(key=lambda group: group["size"], reverse=True)

    split_names = ["train", "val", "test"]
    class_totals = [
        sum(group["class_counts"][class_id] for group in stats)
        for class_id in range(len(CLASSES))
    ]

    current = {
        split: [0] * len(CLASSES)
        for split in split_names
    }

    assignments = {split: [] for split in split_names}

    def score(split, group):
        candidate = {
            name: current[name][:]
            for name in split_names
        }
        candidate[split] = [
            candidate[split][i] + group["class_counts"][i]
            for i in range(len(CLASSES))
        ]

        value = 0.0

        for name in split_names:
            target_total = targets[name]
            current_total = sum(candidate[name])

            # Strongly prioritize the requested total size.
            value += ((current_total - target_total) / max(target_total, 1)) ** 2 * 100

            # Keep each class close to the same class proportion.
            for class_id, total in enumerate(class_totals):
                target_class = total * target_total / sum(class_totals)
                value += (
                    (candidate[name][class_id] - target_class)
                    / max(target_class, 1)
                ) ** 2

        return value

    for group in stats:
        valid_splits = []
        for split in split_names:
            current_total = sum(current[split])
            if current_total + group["size"] <= targets[split]:
                valid_splits.append(split)

        if not valid_splits:
            valid_splits = split_names

        best_split = min(
            valid_splits,
            key=lambda split: (score(split, group), split),
        )

        assignments[best_split].append(group)
        for class_id, count in enumerate(group["class_counts"]):
            current[best_split][class_id] += count

    return assignments, current


def copy_splits(assignments, stats, images, output_dir):
    for split in ["train", "val", "test"]:
        split_dir = os.path.join(output_dir, split)

        if os.path.exists(split_dir):
            shutil.rmtree(split_dir)

        for class_name in CLASSES:
            os.makedirs(os.path.join(split_dir, class_name), exist_ok=True)

        for group in assignments[split]:
            for index in group["indexes"]:
                item = images[index]
                destination = os.path.join(
                    split_dir,
                    item["class_name"],
                    item["filename"],
                )

                # Preserve a duplicate-safe name if the same filename occurs
                # multiple times in a class directory.
                if os.path.exists(destination):
                    base, extension = os.path.splitext(item["filename"])
                    destination = os.path.join(
                        split_dir,
                        item["class_name"],
                        f"{base}_{item['sha256'][:8]}{extension}",
                    )

                shutil.copy2(item["path"], destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--phash-threshold", type=int, default=4)
    parser.add_argument("--train-size", type=int, default=2059)
    parser.add_argument("--val-size", type=int, default=418)
    parser.add_argument("--test-size", type=int, default=445)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--strict-targets", action="store_true")
    args = parser.parse_args()

    total_target = args.train_size + args.val_size + args.test_size

    images = collect_images(args.raw_dir)
    print(f"Original images found: {len(images)}")

    images, duplicate_count = remove_exact_duplicates(images)
    print(f"Exact duplicate copies removed: {duplicate_count}")
    print(f"Unique images: {len(images)}")

    if len(images) != total_target:
        raise ValueError(
            f"Expected {total_target} unique images for the recorded split, "
            f"but found {len(images)}."
        )

    groups = build_phash_groups(images, args.phash_threshold)
    stats = group_stats(groups, images)

    cross_class_groups = [
        group
        for group in stats
        if sum(1 for count in group["class_counts"] if count > 0) > 1
    ]

    print(f"pHash groups: {len(groups)}")
    print(f"Near-duplicate groups: {sum(1 for g in stats if g['size'] > 1)}")
    print(f"Cross-class groups: {len(cross_class_groups)}")

    targets = {
        "train": args.train_size,
        "val": args.val_size,
        "test": args.test_size,
    }

    assignments, current = assign_groups(stats, targets, args.seed)

    actual_sizes = {
        split: sum(current[split])
        for split in ["train", "val", "test"]
    }

    print(f"Train: {actual_sizes['train']}")
    print(f"Validation: {actual_sizes['val']}")
    print(f"Test: {actual_sizes['test']}")

    if args.strict_targets and actual_sizes != targets:
        raise ValueError(
            f"Could not reproduce exact target sizes. "
            f"Expected {targets}, got {actual_sizes}. "
            "Inspect the grouping threshold/data and rerun."
        )

    copy_splits(assignments, stats, images, args.output_dir)

    manifest = {
        "seed": args.seed,
        "phash_threshold": args.phash_threshold,
        "original_images": len(images) + duplicate_count,
        "exact_duplicate_copies_removed": duplicate_count,
        "unique_images": len(images),
        "phash_groups": len(groups),
        "near_duplicate_groups": sum(1 for g in stats if g["size"] > 1),
        "cross_class_groups": len(cross_class_groups),
        "split_sizes": actual_sizes,
        "classes": CLASSES,
    }

    os.makedirs("evaluation", exist_ok=True)
    with open(
        os.path.join("evaluation", "dataset_manifest.json"),
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(manifest, file, indent=2)

    print("Dataset preparation completed.")


if __name__ == "__main__":
    main()
