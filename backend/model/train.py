import argparse
import copy
import json
import os
import random

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import EfficientNet_B0_Weights


SEED = 42
NUM_CLASSES = 5
CLASS_MAPPING = {
    0: "Acute Otitis Media",
    1: "Cerumen Impaction",
    2: "Chronic Otitis Media",
    3: "Myringosclerosis",
    4: "Normal",
}

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    return train_transform, eval_transform


def build_model():
    weights = EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, NUM_CLASSES)

    return model


def validate_class_order(dataset):
    expected = list(CLASS_MAPPING.values())

    if dataset.classes != expected:
        raise ValueError(
            "Unexpected class-folder order. "
            f"Expected {expected}, found {dataset.classes}."
        )


def run_epoch(model, loader, criterion, optimizer, device, training):
    model.train(training)

    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        if training:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)

            if training:
                loss.backward()
                optimizer.step()

        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


def train_stage(
    model,
    train_loader,
    val_loader,
    device,
    epochs,
    learning_rate,
    weight_decay,
    patience,
    best_state,
    best_val_loss,
):
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    scheduler = ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=2,
    )

    epochs_without_improvement = 0

    for epoch in range(1, epochs + 1):
        train_loss, train_acc = run_epoch(
            model, train_loader, criterion, optimizer, device, True
        )

        with torch.inference_mode():
            val_loss, val_acc = run_epoch(
                model, val_loader, criterion, optimizer, device, False
            )

        scheduler.step(val_loss)

        print(
            f"Epoch {epoch:02d}/{epochs} | "
            f"train_loss={train_loss:.6f} train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.6f} val_acc={val_acc:.4f} | "
            f"lr={optimizer.param_groups[0]['lr']:.2e}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            print("Early stopping.")
            break

    return best_state, best_val_loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output", default="models/efficientnet_b0_ear_disease.pth")
    parser.add_argument("--class-mapping", default="models/class_mapping.json")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--head-epochs", type=int, default=5)
    parser.add_argument("--finetune-epochs", type=int, default=15)
    parser.add_argument("--unfreeze-blocks", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--finetune-lr", type=float, default=1e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=3)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    set_seed(args.seed)

    train_transform, eval_transform = get_transforms()

    train_dir = os.path.join(args.data_dir, "train")
    val_dir = os.path.join(args.data_dir, "val")

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=eval_transform)

    validate_class_order(train_dataset)
    validate_class_order(val_dataset)

    if train_dataset.classes != val_dataset.classes:
        raise ValueError("Train and validation class mappings do not match.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Train images: {len(train_dataset)}")
    print(f"Validation images: {len(val_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )

    model = build_model().to(device)

    # Stage 1: freeze the ImageNet backbone and train the 5-class head.
    for parameter in model.features.parameters():
        parameter.requires_grad = False

    best_state = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")

    print("\nStage 1: classification head")
    best_state, best_val_loss = train_stage(
        model,
        train_loader,
        val_loader,
        device,
        args.head_epochs,
        args.lr,
        args.weight_decay,
        args.patience,
        best_state,
        best_val_loss,
    )

    # Stage 2: unfreeze the top EfficientNet feature blocks and fine-tune.
    for parameter in model.features.parameters():
        parameter.requires_grad = False

    blocks = list(model.features.children())
    for block in blocks[-args.unfreeze_blocks:]:
        for parameter in block.parameters():
            parameter.requires_grad = True

    for parameter in model.classifier.parameters():
        parameter.requires_grad = True

    model.load_state_dict(best_state)

    print("\nStage 2: fine-tuning top feature blocks")
    best_state, best_val_loss = train_stage(
        model,
        train_loader,
        val_loader,
        device,
        args.finetune_epochs,
        args.finetune_lr,
        args.weight_decay,
        args.patience,
        best_state,
        best_val_loss,
    )

    model.load_state_dict(best_state)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    torch.save(model.state_dict(), args.output)

    os.makedirs(os.path.dirname(args.class_mapping), exist_ok=True)
    with open(args.class_mapping, "w", encoding="utf-8") as file:
        json.dump(
            {str(k): v for k, v in CLASS_MAPPING.items()},
            file,
            indent=2,
        )

    print(f"Best validation loss: {best_val_loss:.8f}")
    print(f"Model saved: {args.output}")
    print(f"Class mapping saved: {args.class_mapping}")


if __name__ == "__main__":
    main()
