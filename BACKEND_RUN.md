# Backend Run Guide (EarCare AI Clinic)

## 1) Prerequisites
- Python 3.10+ (recommended 3.10/3.11)
- MongoDB running locally or a cloud MongoDB URI
- Trained model file at `models/best_model.keras`

## 2) Create environment file
Create `backend/.env`:

```env
MONGO_URI=mongodb://127.0.0.1:27017/earcare
JWT_SECRET_KEY=replace_with_a_long_random_secret
```

## 3) Create and activate a virtual environment
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

## 4) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Start backend API
```bash
python app.py
```

The API starts on `http://127.0.0.1:5000`.

## 6) Quick health check
```bash
curl http://127.0.0.1:5000/
```

Expected response contains:
- `message: Ear Disease Detection API Running`
- `status: healthy`

## 7) Optional: JWT flow smoke-test
1. `POST /signup` with JSON `{ "email": "test@example.com", "password": "test1234" }`
2. `POST /login` to receive access/refresh token
3. Use `Authorization: Bearer <access_token>` to call `POST /predict` and `GET /history`

## 8) Common issues
- Model load error: ensure `models/best_model.keras` exists.
- JWT error: ensure `JWT_SECRET_KEY` is set.
- Database error: ensure `MONGO_URI` is reachable.
- CORS/UI mismatch: frontend currently points to `http://127.0.0.1:5000`.
