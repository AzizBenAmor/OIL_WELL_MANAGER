# simple_ml_pipeline.py
import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# 1. LOAD DATA (Simple version)
# ==============================
def load_data(db_path="oil_wells.db"):
    """Load data from SQLite database"""
    conn = sqlite3.connect(db_path)
    
    # Load only essential tables
    df_prod = pd.read_sql("SELECT * FROM production", conn)
    df_inc = pd.read_sql("SELECT * FROM incidents", conn)
    df_wells = pd.read_sql("SELECT * FROM wells", conn)
    
    conn.close()
    
    # Simple date conversion
    df_prod['timestamp'] = pd.to_datetime(df_prod['timestamp'])
    df_inc['date'] = pd.to_datetime(df_inc['date'])
    
    print(f"✓ Loaded {len(df_prod)} production records")
    print(f"✓ Loaded {len(df_inc)} incidents")
    print(f"✓ Loaded {len(df_wells)} wells")
    
    return df_prod, df_inc, df_wells

# 2. CREATE SIMPLE FEATURES
# ==========================
def create_features(df_prod, df_inc, df_wells):
    """Create basic features for ML models"""
    
    # Start with production data
    data = df_prod.copy()
    
    # Add well info (depth, status)
    data = data.merge(df_wells[['id', 'depth', 'status']], 
                      left_on='well_id', right_on='id', how='left')
    
    # Simple time features
    data['month'] = data['timestamp'].dt.month
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    
    # Convert status to numbers
    data['status_code'] = data['status'].map({
        'active': 1,
        'inactive': 0,
        'maintenance': 2
    }).fillna(0)
    
    # Simple incident count (last 30 days)
    def count_recent_incidents(row):
        well_id, timestamp = row['well_id'], row['timestamp']
        mask = (df_inc['well_id'] == well_id) & \
               (df_inc['date'] >= timestamp - pd.Timedelta(days=30)) & \
               (df_inc['date'] < timestamp)
        return len(df_inc[mask])
    
    data['recent_incidents'] = data.apply(count_recent_incidents, axis=1)
    
    # Simple target: Will there be an incident next week?
    def will_have_incident_next_week(row):
        well_id, timestamp = row['well_id'], row['timestamp']
        mask = (df_inc['well_id'] == well_id) & \
               (df_inc['date'] > timestamp) & \
               (df_inc['date'] <= timestamp + pd.Timedelta(days=7))
        return 1 if len(df_inc[mask]) > 0 else 0
    
    data['incident_next_week'] = data.apply(will_have_incident_next_week, axis=1)
    
    print(f"✓ Created {len(data)} samples with features")
    return data

# 3. TRAIN SIMPLE MODELS
# ======================
def train_models(data):
    """Train two simple models"""
    
    # Features for prediction
    features = ['flow_rate', 'pressure', 'temperature', 
                'depth', 'recent_incidents', 'status_code',
                'month', 'day_of_week']
    
    # MODEL 1: Predict production quantity
    print("\n" + "="*50)
    print("MODEL 1: Production Quantity Predictor")
    print("="*50)
    
    # Remove rows with missing production data
    prod_data = data.dropna(subset=['quantity_produced'] + features)
    X_prod = prod_data[features]
    y_prod = prod_data['quantity_produced']
    
    # Split data
    X_train_prod, X_test_prod, y_train_prod, y_test_prod = train_test_split(
        X_prod, y_prod, test_size=0.2, random_state=42
    )
    
    # Train model
    model_prod = RandomForestRegressor(
        n_estimators=100,  # Simple, fast
        random_state=42,
        n_jobs=-1
    )
    model_prod.fit(X_train_prod, y_train_prod)
    
    # Evaluate
    predictions = model_prod.predict(X_test_prod)
    r2 = r2_score(y_test_prod, predictions)
    print(f"✓ Model trained with R² score: {r2:.3f}")
    print(f"✓ Can predict production from: {features}")
    
    # MODEL 2: Predict if incident will occur
    print("\n" + "="*50)
    print("MODEL 2: Incident Risk Predictor")
    print("="*50)
    
    # Remove rows with missing incident data
    inc_data = data.dropna(subset=['incident_next_week'] + features)
    X_inc = inc_data[features]
    y_inc = inc_data['incident_next_week']
    
    # Split data
    X_train_inc, X_test_inc, y_train_inc, y_test_inc = train_test_split(
        X_inc, y_inc, test_size=0.2, random_state=42, stratify=y_inc
    )
    
    # Train model
    model_inc = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    model_inc.fit(X_train_inc, y_train_inc)
    
    # Evaluate
    predictions_inc = model_inc.predict(X_test_inc)
    accuracy = accuracy_score(y_test_inc, predictions_inc)
    print(f"✓ Model trained with accuracy: {accuracy:.3f}")
    print(f"✓ Can predict if incident will occur in next 7 days")
    
    # Show feature importance
    print("\nMost Important Features:")
    for i, feature in enumerate(features):
        importance = model_inc.feature_importances_[i]
        print(f"  {feature}: {importance:.3f}")
    
    return {
        'production_model': model_prod,
        'incident_model': model_inc,
        'features': features,
        'production_r2': r2,
        'incident_accuracy': accuracy
    }

# 4. SAVE MODELS
# ==============
def save_models(models):
    """Save models for web app"""
    joblib.dump(models['production_model'], 'models/simple_production_model.pkl')
    joblib.dump(models['incident_model'], 'models/simple_incident_model.pkl')
    joblib.dump(models['features'], 'models/features.pkl')
    
    print("\n" + "="*50)
    print("MODELS SAVED SUCCESSFULLY!")
    print("="*50)
    print("Saved in 'models/' folder:")
    print("  • simple_production_model.pkl")
    print("  • simple_incident_model.pkl")
    print("  • features.pkl")
    
    return True

# 5. SIMPLE PREDICTION FUNCTIONS (for web app)
# ============================================
def predict_production(model, features_list, well_data):
    """
    Simple function to predict production for web app
    well_data should be a dictionary with feature values
    """
    # Convert to DataFrame
    input_data = pd.DataFrame([well_data])
    
    # Ensure all features are present
    for feature in features_list:
        if feature not in input_data.columns:
            input_data[feature] = 0
    
    # Predict
    prediction = model.predict(input_data[features_list])
    return float(prediction[0])

def predict_incident_risk(model, features_list, well_data):
    """
    Simple function to predict incident risk for web app
    Returns probability of incident in next 7 days
    """
    # Convert to DataFrame
    input_data = pd.DataFrame([well_data])
    
    # Ensure all features are present
    for feature in features_list:
        if feature not in input_data.columns:
            input_data[feature] = 0
    
    # Predict probability
    probability = model.predict_proba(input_data[features_list])[0, 1]
    return float(probability)

# MAIN EXECUTION
# ==============
if __name__ == "__main__":
    print("SIMPLE ML PIPELINE FOR OIL WELL MONITORING")
    print("="*50)
    
    try:
        # 1. Load data
        print("\n[1/3] Loading data...")
        df_prod, df_inc, df_wells = load_data("oil_wells.db")
        
        # 2. Create features
        print("\n[2/3] Creating features...")
        data = create_features(df_prod, df_inc, df_wells)
        
        # 3. Train models
        print("\n[3/3] Training models...")
        models = train_models(data)
        
        # 4. Save models
        import os
        os.makedirs('models', exist_ok=True)
        save_models(models)
        
        # Show example prediction
        print("\n" + "="*50)
        print("EXAMPLE PREDICTION:")
        print("="*50)
        
        # Example well data
        example_well = {
            'flow_rate': 150.5,
            'pressure': 45.2,
            'temperature': 85.0,
            'depth': 1200.0,
            'recent_incidents': 2,
            'status_code': 1,  # active
            'month': 6,
            'day_of_week': 2
        }
        
        # Make predictions
        prod_pred = predict_production(
            models['production_model'], 
            models['features'], 
            example_well
        )
        
        risk_pred = predict_incident_risk(
            models['incident_model'], 
            models['features'], 
            example_well
        )
        
        print(f"For a well with:")
        for key, value in example_well.items():
            print(f"  {key}: {value}")
        
        print(f"\nPredictions:")
        print(f"  • Expected production: {prod_pred:.1f} units")
        print(f"  • Risk of incident next week: {risk_pred*100:.1f}%")
        
        print("\n✅ Ready for web app integration!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Your database file named 'oil_wells.db'")
        print("2. Required tables: production, incidents, wells")