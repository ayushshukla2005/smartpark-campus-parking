# SmartPark Hub — Smart Campus Parking & AI Predictor

A production-ready full-stack campus parking management and forecasting system. Combines real-time client-side zone tracking with a machine-learning Random Forest regressor to predict parking availability across campus gates and academic blocks.

---

## 🌟 Key Features

### 1. Real-Time Campus Parking Dashboard (`/`)
- **Campus Overview Bar:** Aggregates real-time open spots across all campus zones (`Main Gate`, `Admission Block`, `Block 34`) with dynamic utilization percentage and congestion status.
- **Interactive Zone Cards:** Capacity progress bars, dynamic status badges (`Available`, `Filling Fast`, `Nearly Full`, `Full`), and single-click spot reservation.
- **Active Session Tracker:** Automatically tracks your occupied spot with live elapsed duration timer, saved GPS coordinates, and one-click Google Maps walking directions back to your car.
- **Safety & Confirmations:** Inline confirmation panel prevents accidental spot release; non-intrusive toast notifications replace blocking browser dialogs.
- **Resilient State Management:** Browser `localStorage` caching with automatic schema validation and a "Reset Demo Counts" utility for testers.

### 2. AI Occupancy Forecasting (`/predict.html`)
- **Multi-Zone Random Forest Regressor:** Predicts spot availability based on zone ID, hour (7:00 AM – 8:00 PM), and day of the week (Monday – Sunday).
- **"Best Pick" Zone Recommendation:** Automatically highlights the optimal parking lot with lowest projected congestion for the user's arrival window.
- **Quick Time Presets:** One-click shortcuts for morning rush (10 AM), lunch surge (12 PM), evening departure (5 PM), and weekend library hours.
- **Production-Ready Relative API Integration:** Smooth asynchronous fetching with animated loading spinners and error fallbacks.

### 3. Hardened Flask Backend (`app.py`)
- **Single-Server Architecture:** Serves both the interactive frontend (`/`, `/predict.html`) and the REST API (`/predict`, `/health`) on a single port without CORS or cross-origin issues.
- **Fault-Tolerant Model Loading:** Dynamically regenerates `parking_model.pkl` on startup if the model file is missing or encounters a deserialization/version incompatibility.
- **Input Validation:** Strict parsing of query parameters with clean `400 Bad Request` JSON responses for out-of-range hours or invalid days.
- **Cloud-Ready WSGI Support:** Dynamic port binding (`PORT`), environment-driven debug flags (`FLASK_DEBUG`), and compatibility with `gunicorn`.

---

## 🏗️ System Architecture & Data Flow

```
+------------------------------------------------------------------+
|                            Browser UI                            |
|                                                                  |
|   Live Parking Dashboard (/)       AI Predictor (/predict.html)  |
|   - localStorage state             - Day & Hour Selectors        |
|   - Geolocation GPS Locator        - Quick Presets               |
|   - Active Duration Timer          - Dynamic Recommendation      |
+-------------------+------------------------------+---------------+
                    |                              |
           HTML / Static Files               REST API Calls
                    |                     (/predict?hour=X&day=Y)
                    v                              v
+------------------------------------------------------------------+
|                        Flask Backend (app.py)                    |
|                                                                  |
|   Endpoints:                                                     |
|   - GET /               -> Serves index.html                     |
|   - GET /predict.html   -> Serves predict.html                   |
|   - GET /health         -> Health check JSON                     |
|   - GET /predict        -> Validates params & queries ML model   |
+------------------------------------+-----------------------------+
                                     |
                          Model Deserialization
                          (with auto-retrain fallback)
                                     v
+------------------------------------------------------------------+
|                   ML Pipeline (train_model.py)                   |
|                                                                  |
|   - Generates multi-zone historical traffic data (7 AM - 8 PM)   |
|   - Fits RandomForestRegressor(n_estimators=100)                 |
|   - Serializes trained weights to parking_model.pkl              |
+------------------------------------------------------------------+
```

---

## 📁 Project Structure

```
.
├── app.py              # Flask server, static file routing, API & validation
├── train_model.py      # ML data generator & Random Forest training pipeline
├── parking_model.pkl   # Serialized ML model weights
├── index.html          # Live Parking frontend with GPS tracking & timer
├── predict.html        # AI Predictor frontend with time presets & recommendations
├── requirements.txt    # Pinned Python package dependencies
├── Procfile            # Cloud WSGI startup command for Gunicorn
├── .gitignore          # Excludes caches, venvs, and OS files
└── README.md           # Documentation & deployment guide
```

---

## 🚀 Local Quickstart

### Prerequisites
- Python 3.10 – 3.13 recommended
- pip

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd "Design thinking proj"
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the ML Model (Optional — app.py also does this automatically)
```bash
python train_model.py
```

### 5. Launch the Server
```bash
python app.py
```

Open your browser to:
- **Live Parking Dashboard:** `http://localhost:5000/`
- **AI Predictor:** `http://localhost:5000/predict.html`
- **Health Check:** `http://localhost:5000/health`

---

## 📡 REST API Reference

### 1. Availability Prediction
`GET /predict`

#### Query Parameters:
| Parameter | Type | Required | Range | Description |
|-----------|------|----------|-------|-------------|
| `hour`    | int  | No (default: 10) | `0` to `23` | Hour of arrival (24-hour clock) |
| `day`     | int  | No (default: 0)  | `0` to `6`  | Day of week (`0`=Mon, `6`=Sun) |

#### Success Response (`200 OK`):
```json
[
  {
    "id": 0,
    "slug": "main",
    "name": "Main Gate",
    "total": 500,
    "predicted_available": 63,
    "occupancy_pct": 87.4,
    "congestion_level": "High Congestion",
    "status_badge": "Nearly Full"
  },
  {
    "id": 1,
    "slug": "admission",
    "name": "Admission Block",
    "total": 150,
    "predicted_available": 19,
    "occupancy_pct": 87.3,
    "congestion_level": "High Congestion",
    "status_badge": "Nearly Full"
  },
  {
    "id": 2,
    "slug": "block34",
    "name": "Block 34",
    "total": 400,
    "predicted_available": 54,
    "occupancy_pct": 86.5,
    "congestion_level": "High Congestion",
    "status_badge": "Nearly Full"
  }
]
```

#### Error Response (`400 Bad Request`):
```json
{
  "error": "Invalid 'hour': 99. Must be an integer between 0 and 23."
}
```

---

## ☁️ Cloud Deployment Guide

The application is pre-configured with `Procfile`, dynamic `PORT` binding, and pinned `requirements.txt` for one-click deployment.

### Option A: Render (Recommended)
1. Push your repository to GitHub or GitLab.
2. Sign in to [Render](https://render.com) and click **New + > Web Service**.
3. Select your repository.
4. Set the following build settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python train_model.py`
   - **Start Command:** `gunicorn app:app`
5. Click **Deploy Web Service**. Render assigns an HTTPS URL automatically.

### Option B: Railway
1. Sign in to [Railway.app](https://railway.app).
2. Click **New Project > Deploy from GitHub repo**.
3. Railway automatically detects the `Procfile` and `requirements.txt`.
4. Add environment variable (optional): `PORT=8080`.
5. Your service will build, train, and deploy in under two minutes.

### Option C: Heroku
```bash
heroku create campus-parking-hub
git push heroku main
heroku open
```

---

## 🧪 Verification & Testing

Run unit tests directly through Python:
```python
from app import app
client = app.test_client()

# Verify live dashboard
assert client.get('/').status_code == 200

# Verify AI predictor UI
assert client.get('/predict.html').status_code == 200

# Verify health endpoint
assert client.get('/health').status_code == 200

# Verify predictions API
res = client.get('/predict?hour=14&day=2')
assert res.status_code == 200
assert len(res.get_json()) == 3
```
