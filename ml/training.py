# ml/training.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

def train_models():
    """Train simple ML models for your oil well data"""
    print("🔧 Training ML models...")
    
    # Connect to your database (update with your connection string)
    # If using SQLite file:
    engine = create_engine('sqlite:///oil_wells.db')
    # If using PostgreSQL: 'postgresql://user:password@localhost/oil_field'
    
    # Load data using raw SQL to avoid SQLAlchemy column object issues
    with engine.connect() as conn:
        production_df = pd.read_sql(text('SELECT * FROM productions'), conn)
        incidents_df = pd.read_sql(text('SELECT * FROM incidents'), conn)
        wells_df = pd.read_sql(text('SELECT * FROM wells'), conn)
    
    # Convert dates
    production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
    incidents_df['date'] = pd.to_datetime(incidents_df['date'])
    
    # Merge with wells data
    data = production_df.merge(
        wells_df[['id', 'depth', 'status']], 
        left_on='well_id', 
        right_on='id',
        how='left'
    )
    
    # Clean up merged column
    if 'id_y' in data.columns:
        data = data.drop('id_y', axis=1)
    if 'id_x' in data.columns:
        data = data.rename(columns={'id_x': 'id'})
    
    # Simple features
    data['month'] = data['timestamp'].dt.month
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    
    # Convert status to numbers
    status_mapping = {'active': 1, 'inactive': 0, 'maintenance': 2}
    data['status_code'] = data['status'].map(status_mapping).fillna(0).astype(int)
    
    # Simple incident count (last 30 days)
    def count_recent_incidents(row):
        if pd.isna(row['timestamp']):
            return 0
        
        mask = (incidents_df['well_id'] == row['well_id']) & \
               (incidents_df['date'] >= row['timestamp'] - pd.Timedelta(days=30)) & \
               (incidents_df['date'] < row['timestamp'])
        return len(incidents_df[mask])
    
    data['recent_incidents'] = data.apply(count_recent_incidents, axis=1)
    
    # Target: incident next 7 days
    def incident_next_week(row):
        if pd.isna(row['timestamp']):
            return 0
        
        mask = (incidents_df['well_id'] == row['well_id']) & \
               (incidents_df['date'] > row['timestamp']) & \
               (incidents_df['date'] <= row['timestamp'] + pd.Timedelta(days=7))
        return 1 if len(incidents_df[mask]) > 0 else 0
    
    data['incident_next_week'] = data.apply(incident_next_week, axis=1)
    
    # Define features - make sure these columns exist in your data
    features = ['flow_rate', 'pressure', 'temperature', 'depth', 
                'recent_incidents', 'status_code', 'month', 'day_of_week']
    
    print(f"Data shape: {data.shape}")
    print(f"Columns available: {list(data.columns)}")
    
    # Check if features exist
    missing_features = [f for f in features if f not in data.columns]
    if missing_features:
        print(f"⚠️  Missing features: {missing_features}")
        print("Available features:", [c for c in data.columns if c in features])
        # Use only available features
        features = [f for f in features if f in data.columns]
    
    # MODEL 1: Production Predictor
    print("\n📊 Training Production Predictor...")
    
    # Filter rows where we have production data
    prod_mask = data['quantity_produced'].notna()
    for feature in features:
        prod_mask = prod_mask & data[feature].notna()
    
    prod_data = data[prod_mask].copy()
    
    if len(prod_data) < 10:
        print("❌ Not enough production data to train model")
        prod_model = None
    else:
        X_prod = prod_data[features]
        y_prod = prod_data['quantity_produced']
        
        # Convert column names to strings (fixes the error!)
        X_prod.columns = X_prod.columns.astype(str)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_prod, y_prod, test_size=0.2, random_state=42
        )
        
        prod_model = RandomForestRegressor(
            n_estimators=50, 
            random_state=42,
            max_depth=10,
            min_samples_split=5
        )
        prod_model.fit(X_train, y_train)
        
        # Simple evaluation
        train_score = prod_model.score(X_train, y_train)
        test_score = prod_model.score(X_test, y_test) if len(X_test) > 0 else 0
        
        print(f"   Samples: {len(prod_data)}")
        print(f"   Train R²: {train_score:.3f}")
        print(f"   Test R²: {test_score:.3f}")
    
    # MODEL 2: Incident Risk Predictor
    print("\n⚠️  Training Incident Risk Predictor...")
    
    # Filter rows where we have incident target data
    inc_mask = data['incident_next_week'].notna()
    for feature in features:
        inc_mask = inc_mask & data[feature].notna()
    
    inc_data = data[inc_mask].copy()
    
    if len(inc_data) < 10:
        print("❌ Not enough incident data to train model")
        inc_model = None
    else:
        X_inc = inc_data[features]
        y_inc = inc_data['incident_next_week']
        
        # Convert column names to strings (fixes the error!)
        X_inc.columns = X_inc.columns.astype(str)
        
        # Check class distribution
        class_counts = y_inc.value_counts()
        print(f"   Class distribution: {dict(class_counts)}")
        
        if len(class_counts) < 2:
            print("   ⚠️  Only one class present, using dummy model")
            inc_model = None
        else:
            X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(
                X_inc, y_inc, test_size=0.2, random_state=42, stratify=y_inc
            )
            
            inc_model = RandomForestClassifier(
                n_estimators=50, 
                random_state=42, 
                class_weight='balanced',
                max_depth=8
            )
            inc_model.fit(X_train_i, y_train_i)
            
            # Simple evaluation
            train_acc = inc_model.score(X_train_i, y_train_i)
            test_acc = inc_model.score(X_test_i, y_test_i) if len(X_test_i) > 0 else 0
            
            print(f"   Samples: {len(inc_data)}")
            print(f"   Train accuracy: {train_acc:.3f}")
            print(f"   Test accuracy: {test_acc:.3f}")
    
    # Save models
    os.makedirs('ml/models', exist_ok=True)
    
    if prod_model:
        joblib.dump(prod_model, 'ml/models/production_model.pkl')
        print(f"✅ Production model saved")
    else:
        # Create a dummy model if real one couldn't be trained
        dummy_prod_model = RandomForestRegressor(n_estimators=1, random_state=42)
        dummy_prod_model.fit([[0]*len(features)], [0])
        joblib.dump(dummy_prod_model, 'ml/models/production_model.pkl')
        print(f"⚠️  Saved dummy production model (not enough data)")
    
    if inc_model:
        joblib.dump(inc_model, 'ml/models/incident_model.pkl')
        print(f"✅ Incident model saved")
    else:
        # Create a dummy model if real one couldn't be trained
        dummy_inc_model = RandomForestClassifier(n_estimators=1, random_state=42)
        dummy_inc_model.fit([[0]*len(features)], [0])
        joblib.dump(dummy_inc_model, 'ml/models/incident_model.pkl')
        print(f"⚠️  Saved dummy incident model (not enough data)")
    
    # Save features list
    joblib.dump(features, 'ml/models/features.pkl')
    
    print("\n" + "="*50)
    print("📈 MODEL TRAINING COMPLETE")
    print("="*50)
    print(f"Features used: {features}")
    print(f"Total data samples: {len(data)}")
    print(f"Models saved to: ml/models/")
    print("\nNext: Run 'uvicorn main:app --reload' to start your app!")
    
    return {
        'production_model': prod_model,
        'incident_model': inc_model,
        'features': features,
        'data_shape': data.shape
    }

if __name__ == "__main__":
    train_models()