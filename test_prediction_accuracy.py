#!/usr/bin/env python3
"""
Test script to diagnose prediction accuracy issues and suggest optimizations.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Add paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.live_ids.feature_extractor import extract_features, FEATURE_NAMES
from backend.models.predictor import predict_flows, model, le

def create_test_flows():
    """Create test flows representing common benign network traffic"""
    test_flows = []
    
    # 1. mDNS (multicast DNS) - very common, should be Benign
    test_flows.append({
        "name": "mDNS Query (UDP 5353)",
        "flow_key": ('10.7.19.211', '224.0.0.251', 5353, 5353, 17),
        "flow": {
            "packet_sizes": [100],
            "timestamps": [1000.0],
            "total_bytes": 100
        }
    })
    
    # 2. mDNS with multiple packets
    test_flows.append({
        "name": "mDNS Query (multiple packets)",
        "flow_key": ('10.7.19.211', '224.0.0.251', 5353, 5353, 17),
        "flow": {
            "packet_sizes": [100, 120, 110],
            "timestamps": [1000.0, 1000.1, 1000.2],
            "total_bytes": 330
        }
    })
    
    # 3. SSDP (UPnP discovery)
    test_flows.append({
        "name": "SSDP (UDP 1900)",
        "flow_key": ('10.7.19.211', '239.255.255.250', 50000, 1900, 17),
        "flow": {
            "packet_sizes": [200],
            "timestamps": [1000.0],
            "total_bytes": 200
        }
    })
    
    # 4. DNS Query
    test_flows.append({
        "name": "DNS Query (UDP 53)",
        "flow_key": ('10.7.19.211', '8.8.8.8', 50000, 53, 17),
        "flow": {
            "packet_sizes": [60],
            "timestamps": [1000.0],
            "total_bytes": 60
        }
    })
    
    # 5. DNS Response
    test_flows.append({
        "name": "DNS Response (UDP 53)",
        "flow_key": ('8.8.8.8', '10.7.19.211', 53, 50000, 17),
        "flow": {
            "packet_sizes": [120],
            "timestamps": [1000.1],
            "total_bytes": 120
        }
    })
    
    # 6. HTTPS (TCP 443) - single packet (SYN)
    test_flows.append({
        "name": "HTTPS SYN (TCP 443)",
        "flow_key": ('10.7.19.211', '142.250.182.46', 50000, 443, 6),
        "flow": {
            "packet_sizes": [60],
            "timestamps": [1000.0],
            "total_bytes": 60
        }
    })
    
    # 7. HTTPS with multiple packets
    test_flows.append({
        "name": "HTTPS Flow (multiple packets)",
        "flow_key": ('10.7.19.211', '142.250.182.46', 50000, 443, 6),
        "flow": {
            "packet_sizes": [60, 1500, 1500, 800],
            "timestamps": [1000.0, 1000.01, 1000.02, 1000.03],
            "total_bytes": 3860
        }
    })
    
    # 8. NetBIOS (UDP 137)
    test_flows.append({
        "name": "NetBIOS (UDP 137)",
        "flow_key": ('10.7.19.211', '10.7.31.255', 137, 137, 17),
        "flow": {
            "packet_sizes": [78],
            "timestamps": [1000.0],
            "total_bytes": 78
        }
    })
    
    return test_flows

def analyze_features(df, name):
    """Analyze extracted features"""
    print(f"\n{'='*60}")
    print(f"Flow: {name}")
    print(f"{'='*60}")
    
    # Count non-zero features
    non_zero = (df.iloc[0] != 0).sum()
    zero_count = (df.iloc[0] == 0).sum()
    
    print(f"Total features: {len(df.columns)}")
    print(f"Non-zero features: {non_zero}")
    print(f"Zero features: {zero_count} ({zero_count/len(df.columns)*100:.1f}%)")
    
    # Show key features
    key_features = ['Protocol', 'Flow Duration', 'Total Fwd Packets', 
                   'Fwd Packets Length Total', 'Flow Bytes/s', 'Flow Packets/s']
    print(f"\nKey Features:")
    for feat in key_features:
        if feat in df.columns:
            val = df[feat].iloc[0]
            print(f"  {feat}: {val}")
    
    # Show prediction
    result = predict_flows(df)
    label = result["predicted_label"].iloc[0]
    
    # Get prediction probabilities if available
    if model and hasattr(model, 'predict_proba'):
        try:
            proba = model.predict_proba(df)
            classes = le.classes_ if le else model.classes_
            proba_dict = dict(zip(classes, proba[0]))
            print(f"\nPrediction: {label}")
            print(f"Probabilities:")
            for cls, prob in sorted(proba_dict.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"  {cls}: {prob:.4f}")
        except:
            print(f"\nPrediction: {label}")
    else:
        print(f"\nPrediction: {label}")
    
    return label

def compare_with_training_data():
    """Compare live flow features with training data statistics"""
    print(f"\n{'='*60}")
    print("COMPARING WITH TRAINING DATA")
    print(f"{'='*60}")
    
    metadata_path = BASE_DIR / "backend" / "models" / "model_metadata.json"
    if not metadata_path.exists():
        metadata_path = BASE_DIR / "artifacts" / "model_metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"Training data:")
        print(f"  Total features: {metadata.get('num_features', 0)}")
        print(f"  Classes: {metadata.get('classes', [])}")
        print(f"  Macro F1: {metadata.get('macro_f1', 0):.4f}")
        print(f"  Train samples: {metadata.get('train_samples', 0):,}")
        print(f"  Test samples: {metadata.get('test_samples', 0):,}")

def suggest_optimizations(test_results):
    """Suggest optimizations based on test results"""
    print(f"\n{'='*60}")
    print("OPTIMIZATION SUGGESTIONS")
    print(f"{'='*60}")
    
    benign_count = sum(1 for r in test_results if r == "Benign")
    total = len(test_results)
    accuracy = (benign_count / total * 100) if total > 0 else 0
    
    print(f"\nTest Results: {benign_count}/{total} correctly classified as Benign ({accuracy:.1f}%)")
    
    suggestions = []
    
    # Check for single-packet flows
    if accuracy < 50:
        suggestions.append({
            "issue": "Single-packet flows with zero duration",
            "problem": "Most test flows have only 1 packet with duration=0.000s. The model was trained on flows with multiple packets and meaningful durations.",
            "solutions": [
                "1. Filter out single-packet flows (they're too short to classify accurately)",
                "2. Increase FLOW_TIMEOUT from 5s to 10-15s to capture more packets per flow",
                "3. Add a minimum packet threshold (e.g., only classify flows with 3+ packets)",
                "4. Create a whitelist for known benign single-packet protocols (mDNS, SSDP, DNS queries)"
            ]
        })
    
    # Check feature extraction
    suggestions.append({
        "issue": "Missing bidirectional features",
        "problem": "Only ~28 features are extracted (36% of 77). ~49 features are zeros (bidirectional features).",
        "solutions": [
            "1. Track bidirectional flows (separate forward/backward packets)",
            "2. Extract TCP flags from packet headers (SYN, ACK, FIN, etc.)",
            "3. Extract more packet-level statistics",
            "4. Consider training a model specifically for unidirectional flows"
        ]
    })
    
    # Check protocol-specific issues
    suggestions.append({
        "issue": "Protocol-specific misclassification",
        "problem": "UDP multicast traffic (mDNS, SSDP) is being misclassified despite Protocol=17 being present.",
        "solutions": [
            "1. Add port-based whitelist: port 5353 (mDNS), 1900 (SSDP), 53 (DNS) → always Benign",
            "2. Add multicast IP detection: 224.0.0.0/4 → likely Benign",
            "3. Retrain model with more UDP multicast examples",
            "4. Use a two-stage classifier: first check whitelist, then ML model"
        ]
    })
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['issue']}")
        print(f"   Problem: {suggestion['problem']}")
        print(f"   Solutions:")
        for sol in suggestion['solutions']:
            print(f"     {sol}")
    
    return suggestions

def main():
    print("="*60)
    print("PREDICTION ACCURACY TEST")
    print("="*60)
    
    # Check if model is loaded
    if model is None or le is None:
        print("ERROR: Model not loaded. Please ensure model files exist.")
        return
    
    print(f"\nModel loaded successfully")
    print(f"Classes: {list(le.classes_)}")
    
    # Compare with training data
    compare_with_training_data()
    
    # Test flows
    test_flows = create_test_flows()
    results = []
    
    print(f"\n{'='*60}")
    print("TESTING BENIGN FLOWS")
    print(f"{'='*60}")
    
    for test_flow in test_flows:
        df = extract_features(test_flow["flow_key"], test_flow["flow"])
        if df is not None:
            label = analyze_features(df, test_flow["name"])
            results.append(label)
        else:
            print(f"\nFailed to extract features for: {test_flow['name']}")
            results.append("ERROR")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for i, (test_flow, result) in enumerate(zip(test_flows, results), 1):
        status = "✅" if result == "Benign" else "❌"
        print(f"{status} {i}. {test_flow['name']}: {result}")
    
    # Suggestions
    suggest_optimizations(results)
    
    print(f"\n{'='*60}")
    print("RECOMMENDED IMMEDIATE FIXES")
    print(f"{'='*60}")
    print("""
1. Add a whitelist filter BEFORE ML prediction:
   - Port 5353 (mDNS) → Benign
   - Port 1900 (SSDP) → Benign  
   - Port 53 (DNS) → Benign
   - Multicast IPs (224.0.0.0/4) → Benign

2. Filter single-packet flows:
   - Only classify flows with 2+ packets
   - Or increase FLOW_TIMEOUT to capture more packets

3. Add minimum duration threshold:
   - Skip flows with duration < 0.001s
    """)

if __name__ == "__main__":
    main()

