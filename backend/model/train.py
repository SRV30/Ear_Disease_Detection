import sys
import os
import json
import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score, confusion_matrix, classification_report

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.preprocess import get_data_generators, get_eval_generator

TRAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/train'))
VAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/val'))
TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/test'))

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

train_data, val_data = get_data_generators(TRAIN_DIR, VAL_DIR)
test_data = get_eval_generator(TEST_DIR)

base = tf.keras.applications.EfficientNetB3(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base.trainable = False

x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
x = tf.keras.layers.BatchNormalization()(x)
x = tf.keras.layers.Dense(256, activation="relu")(x)
x = tf.keras.layers.Dropout(0.4)(x)
output = tf.keras.layers.Dense(train_data.num_classes, activation="softmax")(x)

model = tf.keras.Model(inputs=base.input, outputs=output)
model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss="sparse_categorical_crossentropy", metrics=["accuracy"])

class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(train_data.classes), y=train_data.classes)
class_weights = dict(enumerate(class_weights))

MODEL_SAVE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../models/best_model.keras'))
METRICS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../models/eval_metrics.json'))
CM_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../models/confusion_matrix.npy'))

callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
    tf.keras.callbacks.ModelCheckpoint(MODEL_SAVE_PATH, monitor="val_loss", save_best_only=True, verbose=1),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=2, factor=0.3, verbose=1)
]

model.fit(train_data, validation_data=val_data, epochs=15, callbacks=callbacks, class_weight=class_weights)

base.trainable = True
for layer in base.layers[:-50]:
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train_data, validation_data=val_data, epochs=10, callbacks=callbacks, class_weight=class_weights)

best_model = tf.keras.models.load_model(MODEL_SAVE_PATH)
test_loss, test_acc = best_model.evaluate(test_data, verbose=0)

y_prob = best_model.predict(test_data, verbose=0)
y_pred = np.argmax(y_prob, axis=1)
y_true = test_data.classes

macro_f1 = float(f1_score(y_true, y_pred, average="macro"))
cm = confusion_matrix(y_true, y_pred)
report = classification_report(y_true, y_pred, target_names=list(test_data.class_indices.keys()), output_dict=True)

np.save(CM_PATH, cm)
with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump({"test_accuracy": float(test_acc), "test_loss": float(test_loss), "macro_f1": macro_f1, "classification_report": report}, f, indent=2)

print(f"Test Accuracy: {test_acc:.4f}")
print(f"Macro F1: {macro_f1:.4f}")
print(f"Saved model: {MODEL_SAVE_PATH}")
print(f"Saved metrics: {METRICS_PATH}")
print(f"Saved confusion matrix: {CM_PATH}")
