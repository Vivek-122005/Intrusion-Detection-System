#!/usr/bin/env python3
"""
Test backend Flask app integration with the model.
This simulates what the Flask app does when loading the model.
"""

import sys
from pathlib import Path

# Add backend to path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

def test_backend_model_loading():
    """Test that backend can load model the same way Flask app does."""
    print("\n" + "="*60)
    print("🧪 BACKEND INTEGRATION TEST")
    print("="*60)
    
    try:
        import joblib
        from pathlib import Path
        
        # Simulate what app.py does
        # app.py uses: BASE_DIR = Path(__file__).parent.parent
        # So from app.py's perspective, BASE_DIR is the project root
        # Since we're in project root, MODEL_DIR should be backend/models
        MODEL_DIR = Path(__file__).parent / "backend" / "models"
        
        print(f"\n📁 Looking for models in: {MODEL_DIR}")
        
        if not MODEL_DIR.exists():
            print(f"❌ Model directory doesn't exist: {MODEL_DIR}")
            return False
        
        # Find model files
        model_path = None
        le_path = None
        
        model_files = list(MODEL_DIR.glob("*.joblib"))
        for f in model_files:
            if "label_encoder" in f.name:
                le_path = f
            elif "ids_" in f.name or "model" in f.name.lower():
                model_path = f
        
        if not model_path or not le_path:
            print("❌ Model files not found in backend/models/")
            print(f"   Found files: {[f.name for f in model_files]}")
            return False
        
        print(f"✅ Found model: {model_path.name}")
        print(f"✅ Found label encoder: {le_path.name}")
        
        # Load model (same as Flask app)
        model = joblib.load(model_path)
        label_encoder = joblib.load(le_path)
        
        print(f"\n✅ Model loaded successfully!")
        print(f"   Model type: {type(model).__name__}")
        print(f"   Classes: {len(label_encoder.classes_)}")
        
        # Test prediction (same format as Flask app expects)
        import pandas as pd
        import numpy as np
        
        # Create minimal test data with required features
        test_data = {
            'Protocol': [6, 17],
            'Flow Duration': [100000, 50000],
            'Total Fwd Packets': [10, 5],
            'Total Backward Packets': [5, 3],
        }
        
        # Add remaining features with default values
        # We'll use all features from metadata
        metadata_path = MODEL_DIR / "model_metadata.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            feature_names = metadata.get('feature_names', [])
            
            # Add missing features
            for feat in feature_names:
                if feat not in test_data:
                    test_data[feat] = [0, 0]
            
            df = pd.DataFrame(test_data)
            # Reorder to match training order
            df = df.reindex(columns=feature_names, fill_value=0)
        else:
            # Fallback: create minimal dataframe
            df = pd.DataFrame(test_data)
            # Pad to expected number of features (77)
            for i in range(len(df.columns), 77):
                df[f'feature_{i}'] = 0
        
        print(f"\n🔮 Testing prediction with sample data...")
        print(f"   Input shape: {df.shape}")
        
        predictions = model.predict(df)
        predicted_labels = label_encoder.inverse_transform(predictions)
        
        print(f"✅ Predictions successful!")
        for i, label in enumerate(predicted_labels):
            print(f"   Sample {i+1}: {label}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_backend_model_loading()
    if success:
        print("\n🎉 Backend integration test passed!")
        print("   The Flask app should be able to load and use the model correctly.")
    else:
        print("\n❌ Backend integration test failed!")
        sys.exit(1)

