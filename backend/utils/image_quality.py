import cv2
import numpy as np
from PIL import Image


MIN_IMAGE_WIDTH = 224
MIN_IMAGE_HEIGHT = 224

MIN_BLUR_SCORE = 3.0
MIN_BRIGHTNESS = 40.0
MAX_BRIGHTNESS = 180.0
MIN_CONTRAST = 25.0


def check_image_quality(image_path):
    with Image.open(image_path) as image:
        width, height = image.size
        rgb = np.asarray(image.convert("RGB"))

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        return False, (
            f"Image resolution is too low ({width}x{height}). "
            f"Minimum required resolution is {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}."
        )

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    contrast = float(gray.std())

    if blur_score < MIN_BLUR_SCORE:
        return False, "Image is too blurry for reliable analysis."

    if brightness < MIN_BRIGHTNESS:
        return False, "Image is too dark for reliable analysis."

    if brightness > MAX_BRIGHTNESS:
        return False, "Image is too bright for reliable analysis."

    if contrast < MIN_CONTRAST:
        return False, "Image has insufficient contrast for reliable analysis."

    return True, None
