import os

import cv2
import numpy as np
import torch

from utils.predict import DEVICE, IMG_SIZE, inference_transform


def get_gradcam(model, img_path):
    """
    Generate a Grad-CAM heatmap for the PyTorch EfficientNet-B0 model.
    The last convolutional feature block is used as the target layer.
    """

    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Unable to read image: {img_path}")

    # OpenCV loads BGR; convert to RGB for the same preprocessing
    # used by the PyTorch inference pipeline.
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Build the exact inference tensor used by predict.py.
    from PIL import Image

    pil_img = Image.fromarray(rgb_img)
    tensor = inference_transform(pil_img).unsqueeze(0).to(DEVICE)

    activations = []
    gradients = []

    # EfficientNet-B0's final convolutional feature output is
    # model.features[-1], with shape [batch, channels, height, width].
    target_layer = model.features[-1]

    def forward_hook(module, module_input, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_full_backward_hook(backward_hook)

    try:
        model.zero_grad(set_to_none=True)

        logits = model(tensor)
        predicted_index = int(torch.argmax(logits, dim=1).item())
        score = logits[0, predicted_index]
        score.backward()

        activation = activations[0]
        gradient = gradients[0]

        # Global-average-pool gradients to obtain one weight per channel.
        weights = gradient.mean(dim=(2, 3), keepdim=True)

        # Weighted sum of feature maps followed by ReLU.
        heatmap = (weights * activation).sum(dim=1).squeeze(0)
        heatmap = torch.relu(heatmap)

        max_value = heatmap.max()
        if max_value.item() > 0:
            heatmap = heatmap / max_value

        heatmap = heatmap.detach().cpu().numpy()

    finally:
        forward_handle.remove()
        backward_handle.remove()

    # Resize heatmap to the original image dimensions.
    heatmap = cv2.resize(
        heatmap,
        (img.shape[1], img.shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )

    heatmap = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Blend the heatmap with the original image.
    superimposed = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

    base, ext = os.path.splitext(img_path)
    output_path = f"{base}_gradcam{ext}"

    cv2.imwrite(output_path, superimposed)

    return output_path
