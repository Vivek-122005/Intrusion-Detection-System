from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
import logging

app = Flask(__name__)

# Basic logging setup (configurable via LOG_LEVEL env var)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("backend")

# Configure CORS for React frontend on localhost:3000
# Simple, reliable configuration that works with flask-cors 4.0+
CORS(app,
     supports_credentials=True,
     resources={
         r"/api/*": {
             "origins": [
                 "http://localhost:3000",
                 "http://127.0.0.1:3000"
             ]
         }
     })

# Ensure CORS headers are always present (fallback)
# Sometimes Flask-CORS doesn't auto-handle preflight correctly
@app.after_request
def apply_cors(response):
    origin = request.headers.get('Origin')
    # Only apply if request is from allowed origins
    if origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# Load model and label encoder
# Use resolve() to get absolute paths regardless of working directory
_app_file = Path(__file__).resolve()
BASE_DIR = _app_file.parent.parent  # Project root (absolute)
MODEL_DIR = BASE_DIR / "backend" / "models"  # backend/models directory (absolute)

# Try to find the model file
# Prioritize the new 7-class model: ids_7class_histgb_safe.joblib
model_path = None
le_path = None

logger.info(f"Looking for models in: {MODEL_DIR}")

# First, try to find the new model explicitly
new_model_name = "ids_7class_histgb_safe.joblib"
new_model_path = MODEL_DIR / new_model_name
if new_model_path.exists():
    model_path = new_model_path
    logger.info(f"Found new model: {new_model_name}")

# Look for label encoder
if MODEL_DIR.exists():
    model_files = list(MODEL_DIR.glob("*.joblib"))
    logger.info(f"Found {len(model_files)} .joblib files: {[f.name for f in model_files]}")
    for f in model_files:
        if "label_encoder" in f.name:
            le_path = f
        elif model_path is None and ("ids_" in f.name or "model" in f.name.lower()):
            # Only set model_path if we haven't found the new model yet
            model_path = f

# Fallback to artifacts directory in project root
if not model_path or not le_path:
    artifacts_dir = BASE_DIR / "artifacts"
    logger.warning(f"Models not in backend/models, checking: {artifacts_dir}")
    if artifacts_dir.exists():
        # Try new model first in artifacts
        new_model_path_artifacts = artifacts_dir / new_model_name
        if new_model_path_artifacts.exists() and model_path is None:
            model_path = new_model_path_artifacts
            logger.info(f"Found new model in artifacts: {new_model_name}")
        
        for f in artifacts_dir.glob("*.joblib"):
            if "label_encoder" in f.name:
                le_path = f
            elif model_path is None and "ids_" in f.name:
                model_path = f
        if model_path or le_path:
            logger.info("Found models in artifacts directory")

model = None
label_encoder = None

def load_model():
    global model, label_encoder
    try:
        if model_path and le_path and model_path.exists() and le_path.exists():
            model = joblib.load(model_path)
            label_encoder = joblib.load(le_path)
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Label encoder loaded from {le_path}")
            logger.info(f"Model classes: {len(label_encoder.classes_)} classes: {list(label_encoder.classes_)[:5]}{'...' if len(label_encoder.classes_)>5 else ''}")
            # Compare model classes_ vs label encoder if available
            try:
                model_classes = getattr(model, 'classes_', None)
                if model_classes is not None:
                    if list(model_classes) != list(label_encoder.classes_):
                        logger.warning("Model classes_ and label_encoder.classes_ differ. This can cause mislabeling.")
                        logger.debug(f"model.classes_[:10]: {list(model_classes)[:10]}")
                        logger.debug(f"label_encoder.classes_[:10]: {list(label_encoder.classes_)[:10]}")
            except Exception as e:
                logger.debug(f"Could not compare model classes with label encoder: {e}")
        else:
            logger.error("Model files not found. Please train the model first.")
            logger.error(f"Expected model path: {model_path}")
            logger.error(f"Expected label encoder path: {le_path}")
            if model_path:
                logger.error(f"Model file exists: {model_path.exists()}")
            if le_path:
                logger.error(f"Label encoder exists: {le_path.exists()}")
            logger.error(f"Searched in: {MODEL_DIR}")
            logger.error(f"Also checked: {BASE_DIR / 'artifacts'}")
    except Exception as e:
        logger.exception(f"Error loading model: {e}")

load_model()

# Helper functions (from notebook)
EXCLUDE_COLS = {
    'Flow ID', 'Src IP', 'Dst IP', 'Timestamp', 'SimillarHTTP', 'Flow Byts/s', 'Flow Pkts/s'
}

def clean_columns(df):
    to_drop = [c for c in df.columns if c in EXCLUDE_COLS]
    if to_drop:
        df = df.drop(columns=to_drop)
    if 'label' in df.columns and 'Label' not in df.columns:
        df = df.rename(columns={'label': 'Label'})
    return df

def coerce_numeric(df, exclude_cols=None):
    exclude_cols = set(exclude_cols or [])
    converted = 0
    for c in df.columns:
        if c in exclude_cols:
            continue
        if df[c].dtype == 'object':
            df[c] = pd.to_numeric(df[c], errors='coerce')
            converted += 1
    if converted:
        logger.debug(f"Coerced {converted} object columns to numeric")
    return df

def reduce_memory_usage(df):
    for col in df.columns:
        col_dtype = df[col].dtype
        if col_dtype == np.dtype('float64'):
            df[col] = df[col].astype(np.float32)
        elif col_dtype == np.dtype('int64'):
            df[col] = df[col].astype(np.int32)
    return df

def select_features(df, label_col='Label'):
    feature_cols = [c for c in df.columns if c != label_col and pd.api.types.is_numeric_dtype(df[c])]
    X = df[feature_cols].copy()
    if label_col in df.columns:
        y = df[label_col].copy()
        return X, y
    return X, None

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    # Flask-CORS handles OPTIONS automatically
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'label_encoder_loaded': label_encoder is not None
    })


@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """File upload prediction endpoint"""
    # Handle OPTIONS preflight request FIRST
    if request.method == 'OPTIONS':
        return '', 200
    
    if model is None or label_encoder is None:
        logger.error("Prediction requested but model/label encoder not loaded")
        return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500
    
    try:
        # Handle file upload
        if 'file' not in request.files:
            logger.warning("/api/predict called without file")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("/api/predict called with empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file based on extension
        filename = file.filename.lower()
        if filename.endswith('.parquet'):
            df = pd.read_parquet(file)
        elif filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            logger.warning(f"Unsupported file format: {filename}")
            return jsonify({'error': 'Unsupported file format. Please use CSV or Parquet.'}), 400
        
        # Preprocess
        orig_shape = df.shape
        orig_cols = list(df.columns)
        df = clean_columns(df)
        # Convert string numerics to numbers before selecting features
        df = coerce_numeric(df, exclude_cols=['Label'])
        # Replace inf/-inf and fill NaNs as in training
        feature_cols_all = [c for c in df.columns if c != 'Label']
        if feature_cols_all:
            df[feature_cols_all] = df[feature_cols_all].replace([np.inf, -np.inf], np.nan)
            df[feature_cols_all] = df[feature_cols_all].fillna(0.0)
        df = reduce_memory_usage(df)
        X, y_true = select_features(df, label_col='Label')
        logger.info(f"/api/predict file '{file.filename}' read: original shape {orig_shape}, after clean shape {df.shape}")
        logger.debug(f"Original columns: {orig_cols[:10]}{'...' if len(orig_cols)>10 else ''}")
        logger.debug(f"Post-clean numeric feature columns ({len(X.columns)}): {X.columns[:15].tolist()}{'...' if len(X.columns)>15 else ''}")
        if y_true is not None:
            logger.info(f"Ground truth labels provided: {len(y_true)} rows")
        
        # Align features to training order using metadata, if available
        metadata_path = MODEL_DIR / "model_metadata.json"
        if not metadata_path.exists():
            metadata_path = BASE_DIR / "artifacts" / "model_metadata.json"
        if metadata_path.exists():
            import json as json_lib
            with open(metadata_path, 'r') as f:
                metadata = json_lib.load(f)
            training_features = metadata.get('feature_names', [])
            if training_features:
                missing = set(training_features) - set(X.columns)
                for col in missing:
                    X[col] = 0
                X = X[training_features]
                if missing:
                    logger.warning(f"Added {len(missing)} missing features with zeros: {list(missing)[:10]}{'...' if len(missing)>10 else ''}")
        # Get selected features if available (from feature selection step)
        # For now, use all features that match training features
        if hasattr(model, 'named_steps'):
            # Pipeline model - extract feature names if available
            try:
                X_features = X.columns.tolist()
                logger.debug(f"Pipeline detected. Features passed: {len(X_features)}")
                # If model was trained with selected features, we need to match them
                # This is a simplified version - in production, save feature names
                predictions = model.predict(X)
            except Exception as e:
                logger.exception(f"Feature mismatch when predicting: {e}")
                return jsonify({'error': f'Feature mismatch: {str(e)}'}), 400
        else:
            predictions = model.predict(X)

        # Try probabilities if available
        proba_info = None
        try:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                # capture first row and class order
                class_order = getattr(model, 'classes_', None)
                proba_info = {
                    'class_order': class_order.tolist() if class_order is not None else label_encoder.classes_.tolist(),
                    'first_row': proba[0].tolist() if len(proba) > 0 else []
                }
        except Exception as e:
            logger.debug(f"predict_proba not available or failed: {e}")
        
        # Decode predictions
        # Robust decoding:
        # - If predictions are integer class indices, decode with label_encoder
        # - If predictions are already strings, use them directly
        try:
            preds_np = np.asarray(predictions)
            if np.issubdtype(preds_np.dtype, np.integer):
                predicted_labels = label_encoder.inverse_transform(preds_np)
            else:
                predicted_labels = preds_np
        except Exception as e:
            logger.warning(f"Failed to decode predictions; attempting fallback via label_encoder: {e}")
        predicted_labels = label_encoder.inverse_transform(predictions)
        
        # Count predictions
        prediction_counts = pd.Series(predicted_labels).value_counts().to_dict()
        logger.info(f"Predictions done: total={len(predicted_labels)}, counts={prediction_counts}")
        if proba_info:
            logger.debug(f"Class order: {proba_info['class_order']}")
            logger.debug(f"First row probabilities: {proba_info['first_row']}")
        
        # Calculate statistics
        total_samples = len(predictions)
        benign_count = prediction_counts.get('Benign', 0)
        attack_count = total_samples - benign_count
        attack_percentage = (attack_count / total_samples * 100) if total_samples > 0 else 0
        
        # If true labels available, calculate accuracy
        accuracy = None
        if y_true is not None:
            try:
                y_true_encoded = label_encoder.transform(y_true)
                accuracy = (predictions == y_true_encoded).mean()
                logger.info(f"Computed on-file accuracy: {accuracy:.4f}")
            except Exception as e:
                logger.debug(f"Could not compute accuracy vs provided labels: {e}")
        
        return jsonify({
            'success': True,
            'total_samples': int(total_samples),
            'predictions': predicted_labels.tolist(),
            'prediction_counts': prediction_counts,
            'statistics': {
                'benign_count': int(benign_count),
                'attack_count': int(attack_count),
                'attack_percentage': round(attack_percentage, 2),
                'accuracy': round(accuracy, 4) if accuracy is not None else None
            },
            'classes': label_encoder.classes_.tolist()
        })
    
    except Exception as e:
        logger.exception(f"Unhandled error in /api/predict: {e}")
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500


@app.route('/api/predict-batch', methods=['POST', 'OPTIONS'])
def predict_batch():
    """For manual input or CSV data sent as JSON"""
    # Handle OPTIONS preflight request FIRST (before any other processing)
    if request.method == 'OPTIONS':
        # Return empty response with 200 status for preflight
        # CORS headers are added by @app.after_request decorator
        return '', 200
    
    # Only check model after confirming it's not an OPTIONS request
    if model is None or label_encoder is None:
        logger.error("Batch prediction requested but model/label encoder not loaded")
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            logger.warning("/api/predict-batch called without 'data'")
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle manual input with feature names
        if 'feature_names' in data and data['feature_names']:
            # Manual input: data is array of arrays, feature_names is provided
            feature_names = data['feature_names']
            data_array = data['data']
            
            # Create DataFrame with proper column names
            df = pd.DataFrame(data_array, columns=feature_names)
        else:
            # CSV-like data: assume columns match training features
            df = pd.DataFrame(data['data'])
        
        # Preprocess
        logger.info(f"/api/predict-batch rows received: {len(df)}")
        df = clean_columns(df)
        df = coerce_numeric(df, exclude_cols=['Label'])
        feature_cols_all = [c for c in df.columns if c != 'Label']
        if feature_cols_all:
            df[feature_cols_all] = df[feature_cols_all].replace([np.inf, -np.inf], np.nan)
            df[feature_cols_all] = df[feature_cols_all].fillna(0.0)
        df = reduce_memory_usage(df)
        X, _ = select_features(df)
        logger.debug(f"Batch numeric feature columns ({len(X.columns)}): {X.columns[:15].tolist()}{'...' if len(X.columns)>15 else ''}")
        
        # Ensure feature order matches training (important for manual input)
        # Get feature names from metadata if available
        metadata_path = MODEL_DIR / "model_metadata.json"
        if not metadata_path.exists():
            # Fallback to artifacts directory
            metadata_path = BASE_DIR / "artifacts" / "model_metadata.json"
        if metadata_path.exists():
            import json as json_lib
            with open(metadata_path, 'r') as f:
                metadata = json_lib.load(f)
            training_features = metadata.get('feature_names', [])
            
            # Reorder columns to match training order
            if training_features:
                # Add missing columns with zeros
                missing = set(training_features) - set(X.columns)
                for col in missing:
                    X[col] = 0
                # Reorder and select only training features
                X = X[training_features]
                if missing:
                    logger.warning(f"Added {len(missing)} missing features with zeros: {list(missing)[:10]}{'...' if len(missing)>10 else ''}")
                extra = set(X.columns) - set(training_features)
                if extra:
                    logger.info(f"Extra features ignored (after reordering handled via selection): {list(extra)[:10]}{'...' if len(extra)>10 else ''}")
        
        predictions = model.predict(X)
        predicted_labels = label_encoder.inverse_transform(predictions)
        counts = pd.Series(predicted_labels).value_counts().to_dict()
        logger.info(f"Batch predictions done: total={len(predicted_labels)}, counts={counts}")

        # Optional debug info for very small batches (first row proba)
        debug_info = None
        try:
            if len(X) > 0 and hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                class_order = getattr(model, 'classes_', None)
                debug_info = {
                    'class_order': class_order.tolist() if class_order is not None else label_encoder.classes_.tolist(),
                    'first_row_proba': proba[0].tolist() if len(proba) > 0 else []
                }
        except Exception as e:
            logger.debug(f"predict_proba debug in batch failed: {e}")

        response = {
            'success': True,
            'predictions': predicted_labels.tolist(),
            'classes': label_encoder.classes_.tolist()
        }
        if debug_info and len(X) <= 5:
            response['debug'] = debug_info
        return jsonify(response)
    
    except Exception as e:
        logger.exception(f"Unhandled error in /api/predict-batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata', methods=['GET', 'OPTIONS'])
def get_metadata():
    """Return model metadata including feature names"""
    # Flask-CORS handles OPTIONS automatically, no manual handling needed
    
    if model is None or label_encoder is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Try MODEL_DIR first, then artifacts
        metadata_path = MODEL_DIR / "model_metadata.json"
        if not metadata_path.exists():
            metadata_path = BASE_DIR / "artifacts" / "model_metadata.json"
        if metadata_path.exists():
            import json as json_lib
            with open(metadata_path, 'r') as f:
                metadata = json_lib.load(f)
            return jsonify({
                'success': True,
                'feature_names': metadata.get('feature_names', []),
                'num_features': metadata.get('num_features', 0),
                'num_classes': metadata.get('num_classes', 0),
                'classes': metadata.get('classes', []),
                'model_name': metadata.get('model_name', ''),
                'macro_f1': metadata.get('macro_f1', 0),
            })
        else:
            # Fallback if metadata doesn't exist
            return jsonify({
                'success': True,
                'feature_names': [],
                'num_features': 0,
                'num_classes': len(label_encoder.classes_),
                'classes': label_encoder.classes_.tolist(),
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/latest-alerts', methods=['GET', 'OPTIONS'])
def get_latest_alerts():
    """Return the latest IDS alerts from the log file"""
    try:
        from live_ids.logger import read_latest_alerts
        
        # Get number of alerts from query parameter (default 50)
        n = request.args.get('n', 50, type=int)
        alerts = read_latest_alerts(n)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    except Exception as e:
        logger.exception(f"Error reading alerts: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5050, host='localhost')

