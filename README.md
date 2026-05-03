# 🩺 EarCare AI Clinic  
### AI-Powered Ear Disease Detection System  

🚀 An intelligent healthcare web application that detects ear diseases from otoscopic images using **Deep Learning, Explainable AI, and LLM-based insights**.

---

## 📌 Overview

**EarCare AI Clinic** is a full-stack AI-powered system designed to assist doctors and patients in diagnosing ear diseases quickly and accurately.

The system analyzes ear (otoscopic) images using a deep learning model and provides:
- Disease prediction  
- Confidence score  
- Visual explanation (Grad-CAM)  
- Human-readable medical insights  

---

## 🎯 One-Line Pitch

> AI-powered ear disease detection system that combines deep learning, explainable AI, and real-time web deployment to assist doctors and improve patient diagnosis.

---

## 🧠 Key Features

- 🔍 **AI-based Disease Detection**  
- 🧠 **Explainable AI (Grad-CAM heatmaps)**  
- 📊 **Confidence Score + Risk Analysis**  
- 💬 **LLM-based Medical Explanation**  
- 📁 **Patient History Tracking**  
- 🔐 **JWT Authentication (Login/Signup/Logout)**  
- 📱 **Modern Responsive UI (React + Tailwind)**  
- ⚡ **Fast Prediction (<5 seconds)**  

---

## ⚙️ How It Works

1. User uploads ear image or captures via camera  
2. Image is sent to backend (Flask API)  
3. Deep Learning model (**EfficientNet**) processes image  
4. Model outputs:
   - Predicted disease  
   - Confidence score  
5. Grad-CAM generates heatmap (focus region)  
6. LLM generates easy-to-understand explanation  
7. Results displayed on frontend dashboard  

---

## 📊 Dataset

- Dataset: **Otoscopic Ear Images**
- Total Images: **3000**
- Classes: **5 (Balanced dataset)**
- Format: JPEG (.jpg)

| Class                     | Images |
|--------------------------|--------|
| Acute Otitis Media       | 600    |
| Cerumen Impaction        | 600    |
| Chronic Otitis Media     | 600    |
| Myringosclerosis         | 600    |
| Normal                   | 600    |

---

## 🧪 Deep Learning Approach

- Model: **EfficientNet (Transfer Learning)**  
- Framework: TensorFlow / Keras  
- Image Size: 224 × 224  

### Techniques Used:
- Transfer Learning  
- Data Augmentation  
- Batch Training  
- Hyperparameter Tuning  

---

## 📈 Model Performance

- Initial Accuracy: ~10–15%  
- Final Accuracy: **~98%**  
- Validation Accuracy: ~95–97%  

> High accuracy achieved due to balanced dataset, transfer learning, and optimized training pipeline.

---

## 🔍 Explainable AI

We use **Grad-CAM** to visualize model attention:

- Highlights important regions in the image  
- Improves trust and interpretability  
- Useful for medical validation  

---

## 💬 LLM Integration

- Converts predictions into **human-readable medical insights**
- Provides:
  - Disease explanation  
  - Risk level  
  - Suggested next steps  

---

## 🏗️ System Architecture

User → Upload Image → Flask API → EfficientNet Model
→ Prediction → Grad-CAM → LLM → Frontend Dashboard

---

## 🛠 Tech Stack

### Frontend:
- React.js  
- Tailwind CSS  

### Backend:
- Flask  

### Machine Learning:
- TensorFlow / Keras  
- EfficientNet  

### Database:
- MongoDB  

### Authentication:
- JWT (Access + Refresh Tokens)  

### Extras:
- Grad-CAM  
- LLM Integration  

---

## 📸 Screenshots

> Add your project screenshots here:

- UI Dashboard  
- Image Upload Interface  
- Prediction Output  
- Grad-CAM Heatmap  

---

## 🚀 Impact

- ⚡ Diagnosis in under 5 seconds  
- 👨‍⚕️ Assists doctors (not replacement)  
- 🧑‍🤝‍🧑 Easy for patients to understand  
- 🌍 Useful in rural / low-resource areas  

---

## ⚠️ Limitations

- Performance depends on image quality  
- Not a replacement for professional diagnosis  
- Requires further validation on real-world data  

---

## 🔮 Future Work

- Mobile application deployment  
- Integration with hospital systems  
- Use of advanced models (ResNet, Vision Transformers)  
- Larger and more diverse dataset  

---

## 👨‍💻 Author

- **SRV**

---

## 📜 License

This project is for academic and research purposes only.

---

## 🙌 Acknowledgements

- Medical imaging datasets  
- Deep learning research community  
- Open-source tools and libraries  

---

## ⭐ Show Your Support

If you found this project useful, consider giving it a ⭐ on GitHub!


## ⚡ Backend Startup Optimization (Lazy Model Loading)

The backend now uses lazy loading for the TensorFlow model:
- Flask server starts immediately
- Model loads only on first `POST /predict` request
- Loaded model is cached and reused for all subsequent predictions
- Thread-safe loading prevents duplicate model initialization under concurrent requests

Implementation files:
- `backend/utils/model_loader.py`
- `backend/utils/predict.py`
- `backend/routes/predict_route.py`

## 🔐 Security & Reliability Upgrades

### Added protections
- JWT-protected `/uploads/<filename>` route for private image access.
- Upload hard limit via `MAX_CONTENT_LENGTH`.
- File validation checks extension + MIME type + actual image integrity (`Pillow.verify()`).
- Central auth validation for signup/login:
  - Email format validation
  - Password strength (8-64 chars, letter + number)
- Internal server errors no longer leak exception messages.

### Stability improvements
- Rate limiting:
  - `/signup`
  - `/login`
  - `/predict`
- Paginated history API: `GET /history?page=1&limit=10`
- Old upload cleanup (time-based retention) executed periodically.
- Configurable limits and controls via `.env`.

### New env variables
Add these in `backend/.env`:

```env
MAX_CONTENT_LENGTH=5242880
RATE_LIMIT_DEFAULT=200 per day;50 per hour
RATE_LIMIT_SIGNUP=5 per minute
RATE_LIMIT_LOGIN=10 per minute
RATE_LIMIT_PREDICT=20 per minute
UPLOAD_RETENTION_HOURS=24
IMG_SIZE=224
```
