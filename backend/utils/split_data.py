import os
import shutil
import random

SOURCE_DIR = "data/raw"
TRAIN_DIR = "data/train"
VAL_DIR = "data/val"

SPLIT_RATIO = 0.8

for cls in os.listdir(SOURCE_DIR):
    class_path = os.path.join(SOURCE_DIR, cls)
    
    if not os.path.isdir(class_path):
        continue

    images = os.listdir(class_path)
    random.shuffle(images)

    split_index = int(len(images) * SPLIT_RATIO)

    train_images = images[:split_index]
    val_images = images[split_index:]

    os.makedirs(os.path.join(TRAIN_DIR, cls), exist_ok=True)
    os.makedirs(os.path.join(VAL_DIR, cls), exist_ok=True)

    for img in train_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(TRAIN_DIR, cls, img)
        shutil.copy(src, dst)

    for img in val_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(VAL_DIR, cls, img)
        shutil.copy(src, dst)

    print(f"{cls}: {len(train_images)} train, {len(val_images)} val")

print("Data split completed")