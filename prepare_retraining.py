#!/usr/bin/env python3
"""
Script to prepare for retraining: extract the list of features we can actually compute live.
This ensures training and live inference use the same feature set.
"""

import json
from pathlib import Path

# Features we can actually extract from live unidirectional flows
# Based on backend/live_ids/feature_extractor.py
LIVE_EXTRACTABLE_FEATURES = [
    "Protocol",                    # From flow_key[4]
    "Flow Duration",               # times[-1] - times[0]
    "Total Fwd Packets",           # len(sizes)
    "Fwd Packets Length Total",    # sum(sizes)
    "Fwd Packet Length Max",       # np.max(sizes)
    "Fwd Packet Length Min",       # np.min(sizes)
    "Fwd Packet Length Mean",      # np.mean(sizes)
    "Fwd Packet Length Std",       # np.std(sizes)
    "Flow Bytes/s",                # total_bytes / duration
    "Flow Packets/s",              # total_packets / duration
    "Flow IAT Mean",               # np.mean(iat)
    "Flow IAT Std",                # np.std(iat)
    "Flow IAT Max",                # np.max(iat)
    "Flow IAT Min",                # np.min(iat)
    "Fwd IAT Total",               # sum(iat)
    "Fwd IAT Mean",                # np.mean(iat)
    "Fwd IAT Std",                 # np.std(iat)
    "Fwd IAT Max",                 # np.max(iat)
    "Fwd IAT Min",                 # np.min(iat)
    "Fwd Packets/s",               # total_packets / duration
    "Packet Length Min",           # np.min(sizes)
    "Packet Length Max",           # np.max(sizes)
    "Packet Length Mean",           # np.mean(sizes)
    "Packet Length Std",            # np.std(sizes)
    "Packet Length Variance",       # np.var(sizes)
    "Avg Packet Size",              # np.mean(sizes)
    "Avg Fwd Segment Size",        # np.mean(sizes)
    "Subflow Fwd Packets",         # total_packets (approximate)
    "Subflow Fwd Bytes",           # total_bytes (approximate)
    "Fwd Act Data Packets",        # total_packets (approximate)
]

def main():
    print("="*60)
    print("LIVE FEATURE EXTRACTION ANALYSIS")
    print("="*60)
    
    print(f"\nTotal features we can extract live: {len(LIVE_EXTRACTABLE_FEATURES)}")
    print(f"\nFeatures list:")
    for i, feat in enumerate(LIVE_EXTRACTABLE_FEATURES, 1):
        print(f"  {i:2d}. {feat}")
    
    # Load current model metadata to compare
    metadata_path = Path("backend/models/model_metadata.json")
    if not metadata_path.exists():
        metadata_path = Path("artifacts/model_metadata.json")
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        training_features = metadata.get('feature_names', [])
        print(f"\n{'='*60}")
        print("COMPARISON WITH TRAINING DATA")
        print(f"{'='*60}")
        print(f"Training features: {len(training_features)}")
        print(f"Live extractable: {len(LIVE_EXTRACTABLE_FEATURES)}")
        print(f"Missing from live: {len(training_features) - len(LIVE_EXTRACTABLE_FEATURES)}")
        
        missing = set(training_features) - set(LIVE_EXTRACTABLE_FEATURES)
        print(f"\nFeatures in training but NOT extractable live ({len(missing)}):")
        for feat in sorted(missing):
            print(f"  - {feat}")
        
        extra = set(LIVE_EXTRACTABLE_FEATURES) - set(training_features)
        if extra:
            print(f"\nFeatures extractable live but NOT in training ({len(extra)}):")
            for feat in sorted(extra):
                print(f"  - {feat}")
    
    # Save the feature list for use in training
    output_path = Path("LIVE_FEATURES.json")
    with open(output_path, 'w') as f:
        json.dump({
            "feature_names": LIVE_EXTRACTABLE_FEATURES,
            "num_features": len(LIVE_EXTRACTABLE_FEATURES),
            "description": "Features that can be extracted from live unidirectional flows"
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Saved feature list to: {output_path}")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Use this feature list in main1.ipynb to retrain the model")
    print("2. Update feature_extractor.py to match exactly")
    print("3. Copy retrained model to backend/models/")

if __name__ == "__main__":
    main()

