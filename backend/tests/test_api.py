import io
import os
import sys
from unittest.mock import Mock

import pytest
from PIL import Image

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from routes.predict_route import validate_image


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def make_image_bytes(image_format="JPEG", size=(500, 500)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (120, 120, 120)).save(buffer, format=image_format)
    buffer.seek(0)
    return buffer


def test_root_is_healthy(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_health_endpoint(client, monkeypatch):
    from routes import info_route

    ping = Mock()
    monkeypatch.setattr(info_route.client.admin, "command", ping)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model"] == "healthy"
    assert data["database"] == "healthy"
    ping.assert_called_once_with("ping")


def test_model_info(client):
    response = client.get("/model-info")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "EfficientNet-B0"
    assert data["framework"] == "PyTorch"
    assert data["architecture"] == "torchvision.models.efficientnet_b0"
    assert data["input_size"] == [224, 224]
    assert len(data["classes"]) == 5
    assert data["temperature_scaling"]["enabled"] is True


def test_history_requires_authentication(client):
    response = client.get("/history")

    assert response.status_code == 401


def test_predict_requires_authentication(client):
    response = client.post("/predict")

    assert response.status_code == 401


def test_report_requires_authentication(client):
    response = client.get("/report/000000000000000000000000")

    assert response.status_code == 401


def test_media_requires_authentication(client):
    response = client.get("/media/example.jpg")

    assert response.status_code == 401


def test_validate_valid_jpeg():
    image = Mock()
    image.filename = "ear.jpg"
    image.mimetype = "image/jpeg"
    image.stream = make_image_bytes("JPEG")

    validate_image(image)


def test_validate_rejects_wrong_extension():
    image = Mock()
    image.filename = "ear.txt"
    image.mimetype = "image/jpeg"
    image.stream = make_image_bytes("JPEG")

    with pytest.raises(ValueError, match="Invalid image file type"):
        validate_image(image)


def test_validate_rejects_wrong_mime_type():
    image = Mock()
    image.filename = "ear.jpg"
    image.mimetype = "text/plain"
    image.stream = make_image_bytes("JPEG")

    with pytest.raises(ValueError, match="Only JPEG and PNG"):
        validate_image(image)


def test_validate_rejects_fake_image():
    image = Mock()
    image.filename = "ear.jpg"
    image.mimetype = "image/jpeg"
    image.stream = io.BytesIO(b"not an image")

    with pytest.raises(ValueError, match="valid image"):
        validate_image(image)


def test_validate_rejects_oversized_dimensions():
    image = Mock()
    image.filename = "ear.jpg"
    image.mimetype = "image/jpeg"
    image.stream = make_image_bytes("JPEG", size=(6000, 5000))

    with pytest.raises(ValueError, match="too large"):
        validate_image(image)
