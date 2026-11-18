# SmartPark — Campus Real-Time Parking & AI Predictor

[![Live Demo](https://img.shields.io/badge/Render-Live%20Demo-46E3B7?style=flat&logo=render&logoColor=white)](https://smartpark-campus-parking.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

SmartPark is a full-stack campus parking management and predictive intelligence web application. It combines client-side live zone tracking, browser GPS vehicle pinning, and a server-side Random Forest machine learning regressor to forecast spot availability before drivers arrive on campus.

> 🌐 **Live Web Application:** [https://smartpark-campus-parking.onrender.com/](https://smartpark-campus-parking.onrender.com/)  
> *Note: Hosted on Render's free tier. If the instance has been idle, the first request may take ~30 seconds while the container spins up.*

---

## 🌟 Key Features

### 1. Live Multi-Zone Parking Dashboard (`index.html`)
- **Campus Utilization Overview:** Tracks real-time occupancy across **1,050 total campus spots** divided into three dedicated zones:
  - **Main Gate:** 500 bays (Primary student & visitor entry)
  - **Admission Block:** 150 bays (Administrative & guest parking)
  - **Block 34:** 400 bays (Academic & laboratory complex)
- **Dynamic Congestion Tiers:** Automatically evaluates capacity thresholds to assign status tiers: `Available` (<50%), `Filling Fast` (50–79%), `Nearly Full` (80–99%), and `Full` (100%).
- **Resilient Local Persistence:** Stores parking counts and user sessions in browser `localStorage`, with built-in schema validation and a one-click "Reset Demo Counts" action for repeatable testing.

### 2. GPS Vehicle Pinning & Return Navigation
- **High-Accuracy Geolocation:** Uses `navigator.geolocation` (`enableHighAccuracy: true`) to record latitude and longitude the moment a driver marks their spot.
- **Active Session Duration Timer:** Live tick timer calculates elapsed parking hours and minutes directly on the active parking card.
- **Turn-by-Turn Return Walking Directions:** One-click Google Maps integration (`https://www.google.com/maps/dir/?api=1&destination=lat,lng`) opens walking navigation straight back to your vehicle.
- **Safety Confirmations:** Inline release confirmation panel prevents accidental spot checkout.

### 3. AI Occupancy Predictor (`predict.html`)
- **Trained Random Forest Regressor:** Powered by `parking_model.pkl` trained across historical campus schedules (`7:00 AM – 8:00 PM`) and all days of the week (`Monday – Sunday`).
- **Top AI Recommendation Banner:** Evaluates model predictions for all zones simultaneously and automatically highlights the optimal lot with the lowest projected congestion.
- **Quick-Select Presets:** Rapid one-click shortcuts for key campus transit windows:
  - *Tuesday 10:00 AM* — Peak Lecture Rush
  - *Wednesday 12:00 PM* — Midday Lunch Surge
  - *Friday 5:00 PM* — Evening Departure Shift
  - *Saturday 11:00 AM* — Weekend Workshop / Library Access
- **Split 12-Column Desktop Cockpit:** Sticky parameter rail on the left (`lg:col-span-5`) paired with real-time prediction cards on the right (`lg:col-span-7`) for unified zero-scroll interaction.

### 4. Modern Dark Glassmorphic Design System
- **21st.dev HANZO Radar Sweep Backdrop:** Fixed, battery-conscious conic gradient (`#0A0A0A` base, `#DC2828` crimson, `#811D1D` ruby, `#262626` neutral) enhanced with subtle SVG turbulence wave distortion and radial vignette.
- **Liquid Glass Floating Pill Navbar:** Centered pill capsule navigation (`blur(20px) saturate(160%)`) with specular bevel highlights, crisp hairline borders, and glowing active indicators.
- **Fluid Responsive Typography:** Built on Google Fonts (`Inter` for headings/body and `JetBrains Mono` for tabular metrics and technical kickers) utilizing CSS `clamp()` scaling and `tabular-nums` alignment.
- **Full-Viewport Edge-to-Edge Fluid Shell:** Spans 100% of viewport width and height (`w-full min-h-screen overflow-x-hidden`) with bottom-anchored footers.

### 5. Self-Healing ML Backend (`app.py` & `train_model.py`)
- **Single-Server Architecture:** Unified Flask server serves both the static frontend (`/`, `/predict.html`) and JSON REST API (`/predict`, `/health`) on a single port without CORS complexity.
- **Automatic Retraining Fallback:** If `parking_model.pkl` is missing or fails deserialization due to environment differences, `app.py` dynamically invokes `train_model.train_and_save()` on startup to regenerate the model file automatically.
- **Robust Input Validation:** Strictly validates query parameters, returning clean `400 Bad Request` JSON responses for out-of-range hours (`0–23`) or days (`0–6`).

---

## 🏗️ System Architecture & Data Flow

```text
+-----------------------------------------------------------------------------------+
|                                Browser Client UI                                  |
|                                                                                   |
|   Live Parking Dashboard (index.html)        AI Forecast Cockpit (predict.html)   |
|   - localStorage state & reset utility       - Day (0-6) & Hour (7-20) selectors  |
|   - HTML5 Geolocation (GPS pinning)          - Quick-preset schedule chips        |
|   - Real-time active parking session timer   - Top AI Recommendation banner       |
|   - Google Maps walking directions           - Multi-zone predicted bay cards     |
+--------------------------+---------------------------------+----------------------+
                           |                                 |
              HTTP GET / & /predict.html               HTTP GET /predict?hour=H&day=D
                           |                                 |
                           v                                 v
+-----------------------------------------------------------------------------------+
|                           Unified Flask Backend (app.py)                          |
|                                                                                   |
|   - Static file routing: / -> index.html, /predict.html -> predict.html           |
|   - Health probe endpoint: /health -> JSON status & zone metadata                 |
|   - Input sanitization & range verification (hour: 0-23, day: 0-6)                |
|   - Production WSGI compatibility (Gunicorn / PORT binding)                       |
+------------------------------------------+----------------------------------------+
                                           |
                               Reads input feature vector:
                             [zone_id, hour, day_of_week]
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        Machine Learning Pipeline & Artifact                       |
|                                                                                   |
|   parking_model.pkl                          train_model.py                       |
|   - Serialized RandomForestRegressor         - Generates 7,500 synthetic samples  |
|   - 100 decision trees (n_jobs=-1)           - Models peak, midday & weekend flow |
|   - Trained on historical campus data        - Auto-retrain fallback on startup   |
+-----------------------------------------------------------------------------------+
```

---

## 📁 Repository Structure

```text
.
├── .gitignore          # Ignores Python bytecode caches, virtual environments, and OS metadata
├── .python-version     # Pins Python runtime to 3.11.11 for prebuilt cloud wheels
├── Procfile            # Cloud WSGI startup declaration for Gunicorn (web: gunicorn app:app)
├── README.md           # Project documentation, architecture overview, and API reference
├── app.py              # Flask server, static page routes, health monitor, and /predict API
├── index.html          # Live Parking Dashboard with GPS vehicle locator and session timer
├── parking_model.pkl   # Serialized Random Forest regressor weights
├── predict.html        # AI Occupancy Predictor UI with split 12-column layout and presets
├── render.yaml         # Render Infrastructure-as-Code blueprint for automated deployment
├── requirements.txt    # Pinned production Python dependencies
└── train_model.py      # Synthetic historical data generator and Random Forest training pipeline
```

---

## 📡 REST API Reference

### 1. Live Parking Dashboard
`GET /` or `GET /index.html`
* Serves the primary interactive parking management dashboard.

### 2. AI Parking Predictor UI
`GET /predict.html` or `GET /predict-ui`
* Serves the AI forecasting interface.

### 3. Service Health Probe
`GET /health`
* Used by cloud orchestrators, load balancers, and uptime monitors.

**Response (`200 OK`):**
```json
{
  "model_loaded": true,
  "service": "campus-parking-hub",
  "status": "healthy",
  "zones_count": 3
}
```

### 4. Parking Availability Forecast
`GET /predict`

#### Query Parameters:
| Parameter | Type | Required | Default | Allowed Range | Description |
|:---|:---:|:---:|:---:|:---:|:---|
| `hour` | `int` | No | `10` | `0` to `23` | Hour of arrival in 24-hour clock format |
| `day` | `int` | No | `0` | `0` to `6` | Day of week (`0` = Monday, ..., `6` = Sunday) |

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

#### Validation Error Responses (`400 Bad Request`):
When passing an out-of-range or non-integer parameter:
```json
{
  "error": "Invalid 'hour': 99. Must be an integer between 0 and 23."
}
```
```json
{
  "error": "Invalid 'day': 8. Must be an integer between 0 and 6 (0=Monday, 6=Sunday)."
}
```

---

## 💻 Local Development & Setup

### Prerequisites
- Python 3.10 – 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/ayushshukla2005/smartpark-campus-parking.git
cd smartpark-campus-parking
```

### 2. Create and Activate a Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt / PowerShell)
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Retrain the Machine Learning Model
The repository includes pre-trained weights in `parking_model.pkl`. To regenerate them from scratch:
```bash
python train_model.py
```

### 5. Start the Application
```bash
python app.py
```
Open your browser to:
- **Live Parking Dashboard:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **AI Occupancy Predictor:** [http://127.0.0.1:5000/predict.html](http://127.0.0.1:5000/predict.html)
- **Health Check Endpoint:** [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)

---

## ☁️ Cloud Deployment (Render)

This repository is pre-configured for deployment on [Render](https://render.com) using its Web Service infrastructure:
- **Runtime:** Configured via [.python-version](file:///.python-version) (`3.11.11`) to ensure instant package installation from binary wheels.
- **Process Entry:** Defined in [Procfile](file:///Procfile) as `web: gunicorn app:app`.
- **Dynamic Port:** `app.py` reads `os.environ.get("PORT", 5000)` and binds to `0.0.0.0`.
- **Infrastructure Blueprint:** Included in [render.yaml](file:///render.yaml) for 1-click declarative setup.

To redeploy or fork to your own Render account:
1. Push your repository to GitHub.
2. Visit Render Dashboard > **New +** > **Blueprint** (or connect your repo as a **Web Service**).
3. Set **Build Command**: `pip install -r requirements.txt && python train_model.py`.
4. Set **Start Command**: `gunicorn app:app`.
5. Deploy. Render provisions free managed SSL/HTTPS certificates automatically.

---

## 📄 License
This project was developed for academic, campus mobility, and portfolio research. Open for educational and non-commercial use.
