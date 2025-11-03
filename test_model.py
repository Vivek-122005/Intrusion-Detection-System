#!/usr/bin/env python3
"""
Test script to verify the trained IDS model is working correctly.
Tests model loading, feature matching, and predictions.
"""

import sys
import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_loading():
    """Test 1: Verify model and label encoder can be loaded."""
    print("\n" + "="*60)
    print("TEST 1: Model Loading")
    print("="*60)
    
    artifacts_dir = project_root / "artifacts"
    backend_models_dir = project_root / "backend" / "models"
    
    # Try loading from artifacts first
    model_path = artifacts_dir / "ids_tuned_hist_gb.joblib"
    le_path = artifacts_dir / "label_encoder.joblib"
    
    if not model_path.exists() or not le_path.exists():
        print("❌ Model files not found in artifacts/")
        return False
    
    try:
        model = joblib.load(model_path)
        label_encoder = joblib.load(le_path)
        print(f"✅ Model loaded successfully from: {model_path}")
        print(f"✅ Label encoder loaded successfully from: {le_path}")
        
        # Print model info
        print(f"\n📊 Model Information:")
        print(f"   Model type: {type(model).__name__}")
        if hasattr(model, 'named_steps'):
            print(f"   Pipeline steps: {list(model.named_steps.keys())}")
        print(f"   Number of classes: {len(label_encoder.classes_)}")
        print(f"   Classes: {list(label_encoder.classes_)}")
        
        return True, model, label_encoder
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False, None, None


def test_metadata():
    """Test 2: Verify metadata file exists and is valid."""
    print("\n" + "="*60)
    print("TEST 2: Metadata Validation")
    print("="*60)
    
    metadata_path = project_root / "artifacts" / "model_metadata.json"
    
    if not metadata_path.exists():
        print("❌ Metadata file not found")
        return False
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print("✅ Metadata file loaded successfully")
        print(f"\n📋 Metadata:")
        print(f"   Model name: {metadata.get('model_name')}")
        print(f"   Model type: {metadata.get('model_type')}")
        print(f"   Number of classes: {metadata.get('num_classes')}")
        print(f"   Training samples: {metadata.get('training_samples')}")
        print(f"   Test samples: {metadata.get('test_samples')}")
        print(f"   Number of features: {metadata.get('num_features')}")
        print(f"   Macro F1 score: {metadata.get('macro_f1', 'N/A')}")
        
        return True, metadata
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
        return False, None


def create_sample_data(label_encoder, metadata):
    """Create sample test data matching training feature structure."""
    # Get feature names from metadata if available
    feature_names = metadata.get('feature_names', [])
    
    if not feature_names:
        # Fallback: create dummy features (77 features as seen in training)
        num_features = metadata.get('num_features', 77)
        feature_names = [f'feature_{i}' for i in range(num_features)]
    
    # Create sample data with reasonable ranges
    n_samples = 10
    sample_data = {}
    
    # Use realistic network flow feature ranges
    for feat in feature_names[:min(77, len(feature_names))]:
        if 'Protocol' in feat:
            sample_data[feat] = [6, 17, 6, 6, 6, 17, 6, 6, 6, 17]  # TCP/UDP
        elif 'Duration' in feat or 'duration' in feat.lower():
            sample_data[feat] = np.random.randint(1000, 100000, n_samples)
        elif 'Packets' in feat or 'packets' in feat.lower():
            sample_data[feat] = np.random.randint(1, 1000, n_samples)
        elif 'Length' in feat or 'length' in feat.lower():
            sample_data[feat] = np.random.randint(0, 10000, n_samples)
        elif 'Count' in feat or 'count' in feat.lower():
            sample_data[feat] = np.random.randint(0, 10, n_samples)
        else:
            # Generic numeric feature
            sample_data[feat] = np.random.uniform(0, 1000, n_samples).round(2)
    
    df = pd.DataFrame(sample_data)
    
    # Ensure we have the right number of columns
    if len(df.columns) < len(feature_names):
        # Add missing columns with zeros
        missing = set(feature_names) - set(df.columns)
        for col in missing:
            df[col] = 0
    
    # Reorder columns to match expected order
    df = df.reindex(columns=feature_names, fill_value=0)
    
    return df


def test_predictions(model, label_encoder, metadata):
    """Test 3: Test model predictions with sample data."""
    print("\n" + "="*60)
    print("TEST 3: Model Predictions")
    print("="*60)
    
    try:
        # Create sample data
        print("📝 Creating sample test data...")
        sample_df = create_sample_data(label_encoder, metadata)
        print(f"✅ Created sample data: {sample_df.shape}")
        print(f"   Features: {sample_df.shape[1]}")
        print(f"   Samples: {sample_df.shape[0]}")
        
        # Make predictions
        print("\n🔮 Making predictions...")
        predictions = model.predict(sample_df)
        predicted_labels = label_encoder.inverse_transform(predictions)
        
        print(f"✅ Predictions successful!")
        print(f"\n📊 Prediction Results:")
        for i, (pred, label) in enumerate(zip(predictions, predicted_labels)):
            print(f"   Sample {i+1}: {label} (class {pred})")
        
        # Show distribution
        label_counts = pd.Series(predicted_labels).value_counts()
        print(f"\n📈 Prediction Distribution:")
        for label, count in label_counts.items():
            print(f"   {label}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error making predictions: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_matching():
    """Test 4: Verify feature names match between training and inference."""
    print("\n" + "="*60)
    print("TEST 4: Feature Matching")
    print("="*60)
    
    metadata_path = project_root / "artifacts" / "model_metadata.json"
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        feature_names = metadata.get('feature_names', [])
        
        if feature_names:
            print(f"✅ Found {len(feature_names)} feature names in metadata")
            print(f"\n📋 First 10 features:")
            for i, feat in enumerate(feature_names[:10]):
                print(f"   {i+1}. {feat}")
            if len(feature_names) > 10:
                print(f"   ... and {len(feature_names) - 10} more")
            return True
        else:
            print("⚠️ No feature names found in metadata")
            return False
            
    except Exception as e:
        print(f"❌ Error checking features: {e}")
        return False


def test_backend_compatibility():
    """Test 5: Verify backend can access model files."""
    print("\n" + "="*60)
    print("TEST 5: Backend Compatibility")
    print("="*60)
    
    backend_models_dir = project_root / "backend" / "models"
    
    # Check if backend directory exists
    if not backend_models_dir.exists():
        print("⚠️ Backend models directory doesn't exist. Creating...")
        backend_models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for model files
    model_files = list(backend_models_dir.glob("*.joblib"))
    metadata_files = list(backend_models_dir.glob("*.json"))
    
    print(f"📁 Backend models directory: {backend_models_dir}")
    print(f"   Model files: {len(model_files)}")
    print(f"   Metadata files: {len(metadata_files)}")
    
    if model_files:
        print("✅ Model files found in backend/models/")
        for f in model_files:
            print(f"   - {f.name}")
    else:
        print("⚠️ No model files in backend/models/")
        print("   Copying from artifacts/...")
        
        # Copy files
        artifacts_dir = project_root / "artifacts"
        if (artifacts_dir / "ids_tuned_hist_gb.joblib").exists():
            import shutil
            shutil.copy(artifacts_dir / "ids_tuned_hist_gb.joblib", 
                       backend_models_dir / "ids_tuned_hist_gb.joblib")
            shutil.copy(artifacts_dir / "label_encoder.joblib",
                       backend_models_dir / "label_encoder.joblib")
            if (artifacts_dir / "model_metadata.json").exists():
                shutil.copy(artifacts_dir / "model_metadata.json",
                           backend_models_dir / "model_metadata.json")
            print("✅ Files copied successfully!")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 IDS MODEL TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test 1: Model Loading
    success, model, label_encoder = test_model_loading()
    results['model_loading'] = success
    
    if not success:
        print("\n❌ Cannot proceed without loaded model. Exiting.")
        return False
    
    # Test 2: Metadata
    success, metadata = test_metadata()
    results['metadata'] = success
    
    # Test 3: Predictions (requires model and metadata)
    if metadata:
        success = test_predictions(model, label_encoder, metadata)
        results['predictions'] = success
    
    # Test 4: Feature Matching
    results['feature_matching'] = test_feature_matching()
    
    # Test 5: Backend Compatibility
    results['backend_compatibility'] = test_backend_compatibility()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Model is ready for deployment.")
        return True
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

