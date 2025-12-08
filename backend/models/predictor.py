# backend/models/predictor.py

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Get absolute paths
_app_file = Path(__file__).resolve()
MODEL_DIR = _app_file.parent
BASE_DIR = MODEL_DIR.parent.parent

MODEL_PATH = MODEL_DIR / "ids_7class_histgb_safe.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

# Fallback to artifacts if not in models directory
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "artifacts" / "ids_7class_histgb_safe.joblib"
if not ENCODER_PATH.exists():
    ENCODER_PATH = BASE_DIR / "artifacts" / "label_encoder.joblib"
if not METADATA_PATH.exists():
    METADATA_PATH = BASE_DIR / "artifacts" / "model_metadata.json"

# Load model and encoder
model = None
le = None
feature_names = []

def load_model():
    """Load the ML model and label encoder"""
    global model, le, feature_names
    try:
        if MODEL_PATH.exists() and ENCODER_PATH.exists():
            # Try loading with different joblib protocols for compatibility
            try:
                model = joblib.load(MODEL_PATH)
            except Exception as e1:
                # Try with explicit protocol
                try:
                    import pickle
                    with open(MODEL_PATH, 'rb') as f:
                        model = pickle.load(f)
                except Exception as e2:
                    print(f"Error loading model: {e1}, fallback also failed: {e2}")
                    return False
            
            try:
                le = joblib.load(ENCODER_PATH)
            except Exception as e1:
                try:
                    import pickle
                    with open(ENCODER_PATH, 'rb') as f:
                        le = pickle.load(f)
                except Exception as e2:
                    print(f"Error loading encoder: {e1}, fallback also failed: {e2}")
                    return False
            
            # Load feature names from metadata
            if METADATA_PATH.exists():
                with open(METADATA_PATH, 'r') as f:
                    metadata = json.load(f)
                    feature_names = metadata.get('feature_names', [])
            
            return True
        else:
            print(f"Model files not found. Model: {MODEL_PATH.exists()}, Encoder: {ENCODER_PATH.exists()}")
            return False
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

# Load on import
load_model()

def predict_flows(df):
    """
    Predict labels and probabilities for flow features.
    
    Args:
        df: DataFrame with flow features
        
    Returns:
        DataFrame with added 'predicted_label' and 'prediction_confidence' columns
    """
    if model is None or le is None:
        raise ValueError("Model or label encoder not loaded")
    
    # Ensure all required features are present
    if feature_names:
        # Add missing features with zeros
        missing = set(feature_names) - set(df.columns)
        for col in missing:
            df[col] = 0
        
        # Reorder to match training order
        df = df[feature_names]
    
    # Make predictions
    preds = model.predict(df)
    
    # Get probabilities
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(df)
        # Get confidence for the predicted label (max probability)
        confidence = np.max(probs, axis=1)
    else:
        confidence = np.array([1.0] * len(preds))  # Default to 1 if no proba
    
    # Check if predictions are already labels (strings) or indices (integers)
    if isinstance(preds[0], str) or (hasattr(preds, 'dtype') and preds.dtype == object):
        # Predictions are already labels, use them directly
        labels = preds
    else:
        # Predictions are indices, transform them to labels
        labels = le.inverse_transform(preds)
    
    df_out = df.copy()
    df_out["predicted_label"] = labels
    df_out["prediction_confidence"] = confidence
    
    return df_out

