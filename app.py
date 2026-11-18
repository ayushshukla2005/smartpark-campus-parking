import os
import sys
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'parking_model.pkl')

app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)

# Campus parking zones metadata
ZONES = [
    {'id': 0, 'slug': 'main', 'name': 'Main Gate', 'total': 500},
    {'id': 1, 'slug': 'admission', 'name': 'Admission Block', 'total': 150},
    {'id': 2, 'slug': 'block34', 'name': 'Block 34', 'total': 400}
]

def load_or_train_model():
    """
    Safely load the trained model. If missing, corrupted, or incompatible,
    automatically invokes the training pipeline to regenerate parking_model.pkl.
    """
    if os.path.exists(MODEL_PATH):
        try:
            loaded_model = joblib.load(MODEL_PATH)
            print(f"✅ Loaded parking model from: {MODEL_PATH}")
            return loaded_model
        except Exception as exc:
            print(f"⚠️ Model load failed ({exc}). Retraining clean model...")
    else:
        print("⚠️ parking_model.pkl not found. Training model now...")

    try:
        from train_model import train_and_save
        return train_and_save(MODEL_PATH)
    except Exception as exc:
        print(f"❌ Critical failure during model generation: {exc}", file=sys.stderr)
        raise exc

# Global model instance
model = load_or_train_model()

# ============================================================================
# FRONTEND STATIC ROUTES
# ============================================================================

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_index():
    """Serve the primary Live Parking dashboard."""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/predict.html', methods=['GET'])
@app.route('/predict-ui', methods=['GET'])
def serve_predict():
    """Serve the AI Predictor UI."""
    return send_from_directory(BASE_DIR, 'predict.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for cloud uptime monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'campus-parking-hub',
        'model_loaded': model is not None,
        'zones_count': len(ZONES)
    }), 200

# ============================================================================
# PREDICTIVE API
# ============================================================================

@app.route('/predict', methods=['GET'])
def predict():
    """
    Predict parking availability across all campus zones.
    Query parameters:
      - hour: Integer [0-23] (default: 10)
      - day:  Integer [0-6] where 0=Monday, 6=Sunday (default: 0)
    """
    # 1. Parse and validate 'hour' parameter
    raw_hour = request.args.get('hour', '10')
    try:
        hour = int(raw_hour)
        if not (0 <= hour <= 23):
            return jsonify({
                'error': f"Invalid 'hour': {hour}. Must be an integer between 0 and 23."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'error': f"Invalid 'hour': '{raw_hour}'. Must be a valid integer between 0 and 23."
        }), 400

    # 2. Parse and validate 'day' parameter
    raw_day = request.args.get('day', '0')
    try:
        day_of_week = int(raw_day)
        if not (0 <= day_of_week <= 6):
            return jsonify({
                'error': f"Invalid 'day': {day_of_week}. Must be an integer between 0 and 6 (0=Monday, 6=Sunday)."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'error': f"Invalid 'day': '{raw_day}'. Must be a valid integer between 0 and 6 (0=Monday, 6=Sunday)."
        }), 400

    # 3. Predict for each zone
    predictions = []
    for zone in ZONES:
        zone_id = zone['id']
        total = zone['total']

        input_data = pd.DataFrame(
            [[zone_id, hour, day_of_week]],
            columns=['zone_id', 'hour', 'day_of_week']
        )
        raw_pred = model.predict(input_data)[0]

        # Clamp between 0 and total capacity
        available = max(0, min(total, int(round(raw_pred))))
        occupancy_pct = round(((total - available) / total) * 100, 1)

        # Categorize congestion level
        if occupancy_pct >= 80:
            congestion_level = "High Congestion"
            status_badge = "Nearly Full"
        elif occupancy_pct >= 50:
            congestion_level = "Moderate Flow"
            status_badge = "Filling Fast"
        else:
            congestion_level = "Low Congestion"
            status_badge = "Available"

        predictions.append({
            'id': zone_id,
            'slug': zone['slug'],
            'name': zone['name'],
            'total': total,
            'predicted_available': available,
            'occupancy_pct': occupancy_pct,
            'congestion_level': congestion_level,
            'status_badge': status_badge
        })

    return jsonify(predictions), 200

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1')

    print(f"🚀 Campus Parking Hub running at http://0.0.0.0:{port} (Debug: {debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
