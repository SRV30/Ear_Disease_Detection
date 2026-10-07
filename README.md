# Ear Disease Detection

### AI-Powered Ear Disease Detection with Explainable AI

A full-stack web application for analyzing otoscopic ear images using a PyTorch EfficientNet-B0 model. The system provides disease prediction, calibrated confidence, Grad-CAM visual explanations, AI-generated guidance, protected diagnosis history, and downloadable PDF reports.

> **Medical disclaimer:** This project is an AI-assisted research/academic system. It is not a clinical diagnostic device and should not replace evaluation by a qualified healthcare professional.

---

## Overview

The system supports five classes:

1. Acute Otitis Media
2. Cerumen Impaction
3. Chronic Otitis Media
4. Myringosclerosis
5. Normal

A typical prediction flow is:

```
Ear Image
   ↓
Flask API + Image Validation
   ↓
Image Quality Checks
   ↓
EfficientNet-B0
   ↓
Temperature-Scaled Probabilities
   ↓
Prediction + Confidence
   ├── Grad-CAM Heatmap
   ├── AI-generated Explanation
   └── Diagnosis History
            ↓
       PDF Report
```

---

## Key Features

- **EfficientNet-B0** image classification using PyTorch/Torchvision
- **Transfer learning** with staged fine-tuning
- **Temperature scaling** for confidence calibration
- **Grad-CAM** visual explanations
- Image validation for JPEG/PNG files
- Image resolution, blur, brightness, and contrast checks
- Maximum upload size of **50 MB**
- Protected media access with ownership checks
- JWT authentication with access and refresh tokens
- Rate limiting on sensitive API endpoints
- Diagnosis history with individual/all-record deletion
- Downloadable professional PDF reports
- Model metadata endpoint
- Health monitoring endpoint
- React + Tailwind responsive frontend
- MongoDB persistence
- Automated backend tests with pytest
- GitHub Actions CI for backend tests and frontend builds

---

## Model

### EfficientNet-B0

| Property | Value |
|---|---|
| Architecture | EfficientNet-B0 |
| Framework | PyTorch / Torchvision |
| Input size | 224 × 224 |
| Classes | 5 |
| Parameters | 4,013,953 |
| Checkpoint | `models/efficientnet_b0_ear_disease.pth` |
| Model version | 1.0.0 |

### Inference preprocessing

Images are resized to **224 × 224**, converted to tensors, and normalized using ImageNet statistics:

```text
Mean = [0.485, 0.456, 0.406]
Std  = [0.229, 0.224, 0.225]
```

Training used image augmentation including horizontal flipping, rotation, and color jitter.

---

## Dataset

The project started with **3,000 original images**.

After removing **78 exact duplicate copies**, the leakage-safe dataset contained:

**2,922 unique images**

A group-aware split was used to prevent related/duplicate images from crossing dataset boundaries:

| Split | Images |
|---|---:|
| Training | 2,059 |
| Validation | 418 |
| Test | 445 |
| **Total** | **2,922** |

Classes:

| Class | Original Images |
|---|---:|
| Acute Otitis Media | 600 |
| Cerumen Impaction | 600 |
| Chronic Otitis Media | 600 |
| Myringosclerosis | 600 |
| Normal | 600 |

---

## Model Training

The training pipeline uses staged transfer learning:

1. Load pretrained ImageNet EfficientNet-B0 weights.
2. Replace the final classifier with a 5-class classifier.
3. Initially freeze the backbone and train the classification head.
4. Unfreeze the upper layers and fine-tune.
5. Use AdamW optimization.
6. Use CrossEntropyLoss.
7. Use ReduceLROnPlateau scheduling.
8. Save the checkpoint with the lowest validation loss.
9. Apply early stopping.

Important training settings include:

```text
Batch size:       32
Learning rate:    1e-4
Weight decay:     1e-4
Image size:       224 × 224
Random seed:      42
```

---

## Evaluation

On the leakage-safe internal test set of **445 images**, the final EfficientNet-B0 model achieved:

| Metric | Score |
|---|---:|
| Accuracy | 100.00% |
| Balanced Accuracy | 100.00% |
| Macro Precision | 100.00% |
| Macro Recall | 100.00% |
| Macro F1 | 100.00% |
| Weighted F1 | 100.00% |

Test-set class support:

| Class | Test Images |
|---|---:|
| Acute Otitis Media | 61 |
| Cerumen Impaction | 105 |
| Chronic Otitis Media | 68 |
| Myringosclerosis | 101 |
| Normal | 110 |

### Important evaluation caveat

These results are from the project's **internal leakage-safe test set**. They should not be interpreted as clinical or real-world accuracy.

External images showed domain shift, particularly for **Myringosclerosis**. The system also does not include a dedicated unknown/out-of-distribution class, so arbitrary non-ear images may still receive a prediction.

---

## Confidence Calibration

Temperature scaling was fitted using the validation set and then evaluated on the untouched test set.

```text
Temperature = 0.631204
```

Test-set calibration results:

| Metric | Before Calibration | After Calibration |
|---|---:|---:|
| NLL | 0.00005482 | 0.00000024 |
| ECE | 0.00005478 | 0.00000012 |

Temperature scaling changes the probability distribution while preserving the model's predicted class.

---

## Explainable AI — Grad-CAM

Grad-CAM is generated from the final EfficientNet feature layer to visualize image regions contributing to the prediction.

A quantitative deletion-faithfulness evaluation was also performed on all 445 test images:

| Top attribution pixels masked | Predicted-class probability drop | Random-mask drop |
|---|---:|---:|
| 10% | 2.87 pp | 0.03 pp |
| 20% | 17.48 pp | 0.12 pp |
| 30% | 31.26 pp | 0.78 pp |
| 50% | 50.12 pp | 8.80 pp |

The substantially larger probability drop for high-attribution regions compared with random masking provides evidence that the Grad-CAM explanation is faithful to the model's prediction.

> Grad-CAM is an interpretability tool, not a clinically validated lesion-localization method.

---

## Image Quality Checks

Before inference, uploaded images are checked for:

- JPEG/PNG format
- Valid image contents
- Valid dimensions
- Maximum pixel count
- Minimum resolution of 224 × 224
- Excessive blur
- Excessive darkness
- Excessive brightness
- Insufficient contrast

Current upload limit:

```text
50 MB per request
```

---

## Security

The backend includes several production-oriented protections:

- JWT authentication
- Access and refresh token support
- Token blacklist on logout
- Per-user history ownership checks
- Protected original images and Grad-CAM media
- MIME type and actual image-format validation
- Secure filenames
- Maximum request size
- Image pixel limit
- API rate limiting
- Configurable CORS origins
- Environment-based secrets and database configuration
- User-specific history deletion
- Authenticated PDF report access

For production, Redis is recommended as the rate-limit storage backend instead of the default in-memory store.

---

## API

### Health

```http
GET /health
```

Returns API, model, database, and version status.

### Model information

```http
GET /model-info
```

Returns model architecture, version, input size, classes, and calibration status.

### Authentication

```http
POST /signup
POST /login
POST /refresh
POST /logout
```

### Prediction

```http
POST /predict
```

Requires JWT authentication and accepts an image upload.

### History

```http
GET    /history
DELETE /history/<history_id>
DELETE /history
```

### Protected media

```http
GET /media/<filename>
```

### PDF report

```http
GET /report/<history_id>
```

---

## Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS
- Axios
- React Router
- React Dropzone
- Chart.js

### Backend

- Python
- Flask
- Flask-JWT-Extended
- Flask-CORS
- Flask-Limiter
- Gunicorn

### Machine Learning

- PyTorch
- Torchvision
- EfficientNet-B0
- OpenCV
- Pillow
- Grad-CAM

### Database

- MongoDB
- PyMongo

### Reporting

- ReportLab

### Testing / CI

- pytest
- GitHub Actions

---

## Project Structure

```text
Ear_Disease_Detection/
│
├── backend/
│   ├── model/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── calibrate.py
│   │   ├── evaluate_calibration.py
│   │   ├── evaluate_gradcam.py
│   │   └── analyze_image_quality.py
│   │
│   ├── routes/
│   │   ├── auth_route.py
│   │   ├── predict_route.py
│   │   ├── history_route.py
│   │   ├── report_route.py
│   │   └── info_route.py
│   │
│   ├── utils/
│   │   ├── predict.py
│   │   ├── gradcam.py
│   │   ├── image_quality.py
│   │   └── llm_agent.py
│   │
│   ├── database/
│   ├── tests/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── models/
│   ├── efficientnet_b0_ear_disease.pth
│   ├── class_mapping.json
│   └── temperature_scaling.json
│
├── scripts/
│   └── prepare_dataset.py
│
├── evaluation/
│   └── efficientnet_b0/
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Local Setup

### 1. Clone

```bash
git clone https://github.com/SRV30/Ear_Disease_Detection.git
cd Ear_Disease_Detection
```

### 2. Backend

Create and activate a virtual environment:

**Windows PowerShell**

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r backend/requirements.txt
python -m pip install -r backend/requirements-dev.txt
```

Create `backend/.env`:

```env
MONGO_URI=mongodb://localhost:27017
JWT_SECRET_KEY=replace-with-a-long-random-secret
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
RATE_LIMIT_STORAGE_URI=memory://
```

Start the backend:

```powershell
python backend/app.py
```

The API runs on:

```text
http://127.0.0.1:5000
```

### 3. Frontend

```powershell
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Start the development server:

```powershell
npm run dev
```

The frontend is normally available at:

```text
http://localhost:5173
```

---

## Testing

Run the backend automated tests:

```powershell
pytest backend/tests -v
```

The test suite covers:

- API health
- Model metadata
- Authentication protection
- Protected history/media/report routes
- Image validation
- Invalid image rejection
- MIME/extension validation
- Oversized image rejection

The project also has a GitHub Actions workflow that runs backend tests and the frontend production build on pushes to `main` and pull requests targeting `main`.

---

## Environment Variables

### Backend

```env
MONGO_URI=
JWT_SECRET_KEY=
CORS_ORIGINS=
RATE_LIMIT_STORAGE_URI=
```

### Frontend

```env
VITE_API_BASE_URL=
```

Do not commit real secrets or production credentials.

---

## Screenshots

Project screenshots/demo material:

https://drive.google.com/file/d/1Sfiavxmrg6wtNisTqRmeEYrrCt03_czZ/view?usp=sharing

---

## Limitations

- Internal test performance does not establish clinical performance.
- Real-world domain shift can reduce reliability.
- The model can still produce predictions for images outside the five target classes.
- Image quality and acquisition conditions affect predictions.
- Grad-CAM explanations are not clinical lesion localization.
- Further external validation on diverse clinical datasets is required.
- The system should be used as decision support, not as a replacement for a healthcare professional.

---

## Future Work

- Larger and more diverse clinical datasets
- External validation across different acquisition devices and clinical sites
- Improved handling of unknown/out-of-distribution images
- Mobile deployment
- Hospital/EHR integration
- Additional model architectures and ensemble methods
- More comprehensive clinical validation

---

## Author

**SRV**

---

## License

This project is intended for academic and research purposes.

---

## Acknowledgements

- Medical imaging and otoscopy research community
- PyTorch and Torchvision
- Flask ecosystem
- React ecosystem
- Open-source explainable AI research
