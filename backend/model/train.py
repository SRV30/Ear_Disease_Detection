import sys
import os
import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.preprocess import get_data_generators

TRAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/train'))
VAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/val'))

train_data, val_data = get_data_generators(TRAIN_DIR, VAL_DIR)

base = tf.keras.applications.EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base.trainable = False

x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.Dense(128, activation="relu")(x)
x = tf.keras.layers.Dropout(0.4)(x)
output = tf.keras.layers.Dense(train_data.num_classes, activation="softmax")(x)

model = tf.keras.Model(inputs=base.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)

class_weights = dict(enumerate(class_weights))

MODEL_SAVE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../models/best_model.keras')
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1
    ),
    tf.keras.callbacks.ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor="val_loss",
        save_best_only=True,
        verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        patience=2,
        factor=0.3,
        verbose=1
    )
]

model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks,
    class_weight=class_weights
)

base.trainable = True

for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks,
    class_weight=class_weights
)

val_loss, val_acc = model.evaluate(val_data)
print(f"Validation Accuracy: {val_acc:.4f}")
print(f"Model saved at: {MODEL_SAVE_PATH}")