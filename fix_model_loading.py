#!/usr/bin/env python3
"""
Script to fix model loading issue by retraining with current NumPy version
This will create a new model file compatible with your current environment
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import HistGradientBoostingClassifier

print("="*60)
print("Model Loading Fix Script")
print("="*60)
print(f"NumPy version: {np.__version__}")
print()

# Check if we can load the old model
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "backend" / "models" / "ids_7class_histgb_safe.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "artifacts" / "ids_7class_histgb_safe.joblib"

if MODEL_PATH.exists():
    print(f"Found existing model: {MODEL_PATH}")
    print("Attempting to load...")
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully! No fix needed.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print()
        print("This script will help you retrain the model.")
        print("However, you need the training data to retrain.")
        print()
        print("To fix this issue:")
        print("1. Run main1.ipynb to retrain the model with current NumPy version")
        print("2. Or update NumPy to match the version used during training")
        print()
        print("To check what NumPy version was used, check the training notebook.")
        sys.exit(1)
else:
    print("❌ Model file not found!")
    print(f"Expected at: {MODEL_PATH}")
    sys.exit(1)

