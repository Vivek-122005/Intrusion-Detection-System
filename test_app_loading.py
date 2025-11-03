#!/usr/bin/env python3
"""
Test script to verify Flask app can find and load models
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import the path resolution logic from app.py
_app_file = Path(backend_dir / "app.py").resolve()
BASE_DIR = _app_file.parent.parent
MODEL_DIR = BASE_DIR / "backend" / "models"

print("="*60)
print("Testing Flask App Model Loading")
print("="*60)
print(f"\nApp file: {_app_file}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"MODEL_DIR: {MODEL_DIR}")
print(f"\nMODEL_DIR exists: {MODEL_DIR.exists()}")

if MODEL_DIR.exists():
    model_files = list(MODEL_DIR.glob("*.joblib"))
    print(f"Found {len(model_files)} .joblib files:")
    for f in model_files:
        print(f"  ✅ {f.name}")
    
    # Try to find model files (same logic as app.py)
    model_path = None
    le_path = None
    
    for f in model_files:
        if "label_encoder" in f.name:
            le_path = f
        elif "ids_" in f.name or "model" in f.name.lower():
            model_path = f
    
    print(f"\n📍 Resolved paths:")
    print(f"   Model: {model_path}")
    print(f"   Label Encoder: {le_path}")
    
    if model_path and le_path:
        print(f"\n✅ Both files found!")
        print(f"   Model exists: {model_path.exists()}")
        print(f"   Label encoder exists: {le_path.exists()}")
        
        if model_path.exists() and le_path.exists():
            print("\n🧪 Testing actual loading...")
            try:
                import joblib
                model = joblib.load(model_path)
                label_encoder = joblib.load(le_path)
                print(f"✅ Successfully loaded model!")
                print(f"   Model type: {type(model)}")
                print(f"   Classes: {len(label_encoder.classes_)}")
                print(f"\n🎉 Model loading works correctly!")
            except Exception as e:
                print(f"❌ Error loading: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ One or both files don't exist!")
    else:
        print("❌ Could not find model files")
        print(f"   model_path: {model_path}")
        print(f"   le_path: {le_path}")
else:
    print("❌ MODEL_DIR does not exist!")
    print(f"\nChecking alternatives:")
    artifacts_dir = BASE_DIR / "artifacts"
    print(f"   Artifacts dir: {artifacts_dir}")
    print(f"   Artifacts exists: {artifacts_dir.exists()}")

print("\n" + "="*60)

