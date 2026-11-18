import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parking_model.pkl')

ZONES = [
    {'id': 0, 'slug': 'main', 'name': 'Main Gate', 'total': 500},
    {'id': 1, 'slug': 'admission', 'name': 'Admission Block', 'total': 150},
    {'id': 2, 'slug': 'block34', 'name': 'Block 34', 'total': 400}
]

def generate_synthetic_data(samples_per_zone=2500, random_state=42):
    """
    Generate realistic historical parking occupancy data.
    - Covers hours 7:00 AM to 8:00 PM (7 through 20).
    - Covers all 7 days of the week (0=Mon to 6=Sun).
    - Accounts for weekday peak class hours, midday turnover, evening departure,
      and weekend activity patterns.
    """
    rng = np.random.default_rng(random_state)
    all_records = []

    for zone in ZONES:
        total = zone['total']
        # Sample hours across operating schedule (7 to 20 inclusive)
        hours = rng.integers(7, 21, size=samples_per_zone)
        # Sample days across entire week (0 to 6 inclusive)
        days = rng.integers(0, 7, size=samples_per_zone)
        available_spots = []

        for h, d in zip(hours, days):
            if d < 5:
                # --- WEEKDAYS (Monday - Friday) ---
                if 9 <= h <= 15:
                    # Peak academic hours: very high congestion (5% - 22% spots left)
                    left = rng.integers(int(total * 0.05), max(int(total * 0.22), int(total * 0.05) + 2))
                elif h in (7, 8):
                    # Morning arrival window (45% - 75% spots left)
                    left = rng.integers(int(total * 0.45), int(total * 0.75))
                elif h == 16:
                    # Afternoon shift / transition (35% - 60% spots left)
                    left = rng.integers(int(total * 0.35), int(total * 0.60))
                else:
                    # Evening (17:00 - 20:00): campus empties out (70% - 95% spots left)
                    left = rng.integers(int(total * 0.70), min(total, int(total * 0.95)))
            elif d == 5:
                # --- SATURDAY (Weekend classes, events, library visitors) ---
                if 10 <= h <= 14:
                    left = rng.integers(int(total * 0.50), int(total * 0.75))
                else:
                    left = rng.integers(int(total * 0.75), int(total * 0.92))
            else:
                # --- SUNDAY (Minimal campus activity) ---
                left = rng.integers(int(total * 0.82), total)

            # Clamp between 0 and total capacity
            clamped = int(np.clip(left, 0, total))
            available_spots.append(clamped)

        df_zone = pd.DataFrame({
            'zone_id': zone['id'],
            'hour': hours,
            'day_of_week': days,
            'available': available_spots
        })
        all_records.append(df_zone)

    return pd.concat(all_records, ignore_index=True)

def train_and_save(model_path=None):
    """
    Train Random Forest regressor on synthetic dataset and save to disk.
    Can be invoked standalone or dynamically by app.py upon model load failure.
    """
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH

    print("📊 Generating parking dataset covering campus hours (7 AM - 8 PM, Mon - Sun)...")
    dataset = generate_synthetic_data()

    X = dataset[['zone_id', 'hour', 'day_of_week']]
    y = dataset['available']

    print("🤖 Training Random Forest Regressor (n_estimators=100)...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    os.makedirs(os.path.dirname(os.path.abspath(model_path)), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"✅ Multi-zone parking model saved cleanly to: {model_path}")
    return model

if __name__ == '__main__':
    train_and_save()
