# Backend Run Guide (Windows PowerShell)

## 1) Open project and go to backend
```powershell
cd /d <PROJECT_ROOT>\backend
```

## 2) Create virtual environment (first time only)
```powershell
py -3 -m venv .venv
```

## 3) Activate virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```

## 4) Confirm Python/Pip are from venv
```powershell
python -c "import sys; print(sys.executable)"
python -m pip --version
```

## 5) Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 6) Fix missing flask-cors explicitly (if needed)
```powershell
python -m pip install flask-cors
python -c "import flask_cors; print(flask_cors.__version__)"
```

## 7) Set environment variables (if .env not used)
```powershell
$env:MONGO_URI="mongodb://127.0.0.1:27017/earcare"
$env:JWT_SECRET_KEY="replace_with_long_random_secret"
```

## 8) Start backend
```powershell
python app.py
```

## 9) Health check
```powershell
curl http://127.0.0.1:5000/
```
