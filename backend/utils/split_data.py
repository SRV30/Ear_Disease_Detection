import os
import shutil
import random
from collections import defaultdict

SOURCE_DIR = "data/raw"
OUTPUT_DIR = "data"
TRAIN_DIR = os.path.join(OUTPUT_DIR, "train")
VAL_DIR = os.path.join(OUTPUT_DIR, "val")
TEST_DIR = os.path.join(OUTPUT_DIR, "test")

TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15
SEED = 42


def clear_and_create_dirs(base_dirs, classes):
    for base in base_dirs:
        if os.path.exists(base):
            shutil.rmtree(base)
        for cls in classes:
            os.makedirs(os.path.join(base, cls), exist_ok=True)


def extract_group_id(filename):
    stem = os.path.splitext(filename)[0]
    return stem.split("_")[0]


random.seed(SEED)
classes = sorted([c for c in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, c))])
clear_and_create_dirs([TRAIN_DIR, VAL_DIR, TEST_DIR], classes)

for cls in classes:
    class_path = os.path.join(SOURCE_DIR, cls)
    images = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]

    grouped = defaultdict(list)
    for img in images:
        grouped[extract_group_id(img)].append(img)

    groups = list(grouped.keys())
    random.shuffle(groups)

    n = len(groups)
    n_train = int(n * TRAIN_RATIO)
    n_val = int(n * VAL_RATIO)

    train_groups = set(groups[:n_train])
    val_groups = set(groups[n_train:n_train + n_val])
    test_groups = set(groups[n_train + n_val:])

    counts = {"train": 0, "val": 0, "test": 0}

    for gid, imgs in grouped.items():
        if gid in train_groups:
            split = "train"
            dst_base = TRAIN_DIR
        elif gid in val_groups:
            split = "val"
            dst_base = VAL_DIR
        else:
            split = "test"
            dst_base = TEST_DIR

        for img in imgs:
            shutil.copy(os.path.join(class_path, img), os.path.join(dst_base, cls, img))
            counts[split] += 1

    print(f"{cls}: {counts['train']} train, {counts['val']} val, {counts['test']} test")

print("Data split completed (group-aware, deterministic)")
