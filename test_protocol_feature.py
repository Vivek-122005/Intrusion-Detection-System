#!/usr/bin/env python3
"""
Quick test to verify Protocol feature is being extracted correctly
"""

import sys
from pathlib import Path

# Add paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.live_ids.feature_extractor import extract_features

# Create a test flow
flow_key = ('10.7.19.211', '224.0.0.251', 5353, 5353, 17)  # UDP mDNS
flow = {
    "packet_sizes": [100, 120, 110],
    "timestamps": [1000.0, 1000.1, 1000.2],
    "total_bytes": 330
}

# Extract features
df = extract_features(flow_key, flow)

if df is not None:
    print("✅ Feature extraction successful")
    print(f"\nProtocol value: {df['Protocol'].iloc[0]}")
    print(f"Expected: 17 (UDP)")
    print(f"Match: {'✅ YES' if df['Protocol'].iloc[0] == 17 else '❌ NO'}")
    
    print(f"\nTotal features extracted: {len([c for c in df.columns if df[c].iloc[0] != 0])}")
    print(f"Total features (including zeros): {len(df.columns)}")
    
    # Show first 10 non-zero features
    print("\nFirst 10 non-zero features:")
    non_zero = {col: df[col].iloc[0] for col in df.columns if df[col].iloc[0] != 0}
    for i, (col, val) in enumerate(list(non_zero.items())[:10]):
        print(f"  {col}: {val}")
else:
    print("❌ Feature extraction failed")

