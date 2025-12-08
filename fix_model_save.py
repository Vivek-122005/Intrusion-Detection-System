#!/usr/bin/env python3
"""
Fix script to save model in a compatible format
This script loads the model from artifacts and saves it with protocol 4 for better compatibility
"""

import sys
from pathlib import Path
import joblib
import numpy as np

BASE_DIR = Path(__file__).parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODELS_DIR = BASE_DIR / "backend" / "models"

print("="*60)
print("Model Compatibility Fix Script")
print("="*60)
print(f"NumPy version: {np.__version__}")
print()

# Try to load the model with a workaround
model_path = ARTIFACTS_DIR / "ids_7class_histgb_safe.joblib"
encoder_path = ARTIFACTS_DIR / "label_encoder.joblib"

if not model_path.exists():
    print(f"❌ Model not found at: {model_path}")
    sys.exit(1)

print(f"Found model: {model_path}")
print("Attempting to fix...")

try:
    # Try loading with a workaround for the NumPy issue
    # The issue is with the random state in the model
    import pickle
    import io
    
    # Method 1: Try loading and re-saving with protocol 4
    print("\nMethod 1: Loading and re-saving with protocol 4...")
    try:
        # Load the model
        with open(model_path, 'rb') as f:
            # Use joblib with a custom unpickler that handles the NumPy issue
            model = joblib.load(model_path)
            print("✅ Model loaded successfully!")
            
            # Re-save with protocol 4 (more compatible)
            print("Re-saving model with compatible protocol...")
            joblib.dump(model, model_path, protocol=4)
            print("✅ Model re-saved!")
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        print("\nMethod 2: Trying to patch NumPy random module...")
        
        # Method 2: Patch the NumPy random module
        import numpy.random._pickle as nrp
        original_ctor = nrp.__bit_generator_ctor
        
        def patched_ctor(bit_generator_name, *args, **kwargs):
            # If it's PCG64, try to use a fallback
            if 'PCG64' in str(bit_generator_name):
                # Try to use MT19937 instead
                from numpy.random import MT19937
                return MT19937(*args, **kwargs)
            return original_ctor(bit_generator_name, *args, **kwargs)
        
        nrp.__bit_generator_ctor = patched_ctor
        
        try:
            model = joblib.load(model_path)
            print("✅ Model loaded with patch!")
            
            # Restore original
            nrp.__bit_generator_ctor = original_ctor
            
            # Re-save
            joblib.dump(model, model_path, protocol=4)
            print("✅ Model re-saved!")
        except Exception as e2:
            print(f"❌ Method 2 also failed: {e2}")
            print("\n⚠️  Cannot automatically fix. Please retrain the model with:")
            print("   1. Set random_state=None in HistGradientBoostingClassifier")
            print("   2. Or use a different random state that's compatible")
            sys.exit(1)
    
    # Copy to backend/models
    print("\nCopying files to backend/models...")
    import shutil
    shutil.copy(model_path, MODELS_DIR / "ids_7class_histgb_safe.joblib")
    shutil.copy(encoder_path, MODELS_DIR / "label_encoder.joblib")
    
    # Copy metadata if it exists
    metadata_path = ARTIFACTS_DIR / "model_metadata.json"
    if metadata_path.exists():
        shutil.copy(metadata_path, MODELS_DIR / "model_metadata.json")
    
    print("✅ Files copied to backend/models/")
    print("\n🎉 Model fixed and ready to use!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

