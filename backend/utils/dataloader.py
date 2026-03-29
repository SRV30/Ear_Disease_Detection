import os
import cv2
import numpy as np

IMG_SIZE = 224

def load_data(data_dir):
    X, y = [], []
    classes = sorted(os.listdir(data_dir))

    for label, cls in enumerate(classes):
        path = os.path.join(data_dir, cls)

        for img_name in os.listdir(path):
            try:
                img_path = os.path.join(path, img_name)
                img = cv2.imread(img_path)
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                img = img / 255.0

                X.append(img)
                y.append(label)
            except:
                continue

    return np.array(X), np.array(y), classes