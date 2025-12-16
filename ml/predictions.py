# ml/predictions.py
import joblib
import pandas as pd
from datetime import datetime

# Load models (they'll be loaded once when the app starts)
try:
    production_model = joblib.load('ml/models/production_model.pkl')
    incident_model = joblib.load('ml/models/incident_model.pkl')
    features = joblib.load('ml/models/features.pkl')
    MODELS_LOADED = True
except:
    print("⚠️  ML models not found. Run training.py first.")
    MODELS_LOADED = False
    production_model = None
    incident_model = None
    features = []

def predict_production(well_data: dict) -> float:
    """Predict production for a well"""
    if not MODELS_LOADED:
        return 0.0
    
    # Prepare input
    input_data = prepare_input(well_data)
    
    # Predict
    try:
        prediction = production_model.predict([input_data])[0]
        return float(prediction)
    except:
        return 0.0

def predict_incident_risk(well_data: dict) -> dict:
    """Predict incident risk for a well"""
    if not MODELS_LOADED:
        return {"risk": 0.0, "level": "Unknown"}
    
    # Prepare input
    input_data = prepare_input(well_data)
    
    # Predict
    try:
        probability = incident_model.predict_proba([input_data])[0, 1]
        
        # Determine risk level
        if probability > 0.7:
            level = "High"
        elif probability > 0.4:
            level = "Medium"
        else:
            level = "Low"
        
        return {
            "risk": float(probability),
            "level": level,
            "percentage": float(probability * 100)
        }
    except:
        return {"risk": 0.0, "level": "Unknown", "percentage": 0.0}

def prepare_input(well_data: dict) -> list:
    """Prepare input data for ML models"""
    # Default values
    defaults = {
        'flow_rate': 100.0,
        'pressure': 50.0,
        'temperature': 75.0,
        'depth': 1000.0,
        'recent_incidents': 0,
        'status_code': 1,  # active
        'month': datetime.now().month,
        'day_of_week': datetime.now().weekday()
    }
    
    # Use provided data or defaults
    input_dict = {}
    for feature in features:
        if feature in well_data:
            input_dict[feature] = well_data[feature]
        elif feature in defaults:
            input_dict[feature] = defaults[feature]
        else:
            input_dict[feature] = 0
    
    # Ensure correct order
    return [input_dict.get(f, 0) for f in features]

def get_recommendations(risk_level: str, production: float, predicted_production: float) -> list:
    """Get simple recommendations based on predictions"""
    recommendations = []
    
    if risk_level == "High":
        recommendations.append("Schedule immediate maintenance inspection")
        recommendations.append("Increase monitoring frequency")
    
    elif risk_level == "Medium":
        recommendations.append("Monitor closely for any changes")
    
    if predicted_production < production * 0.8:
        recommendations.append("Production may drop - Check equipment calibration")
    
    return recommendations