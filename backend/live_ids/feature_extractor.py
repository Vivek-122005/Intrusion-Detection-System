# backend/live_ids/feature_extractor.py

import numpy as np
import pandas as pd
import json
from pathlib import Path

# Get absolute paths
_extractor_file = Path(__file__).resolve()
MODEL_DIR = _extractor_file.parent.parent / "models"
BASE_DIR = _extractor_file.parent.parent.parent

METADATA_PATH = MODEL_DIR / "model_metadata.json"
if not METADATA_PATH.exists():
    METADATA_PATH = BASE_DIR / "artifacts" / "model_metadata.json"

FEATURE_NAMES = []
if METADATA_PATH.exists():
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
        FEATURE_NAMES = metadata.get('feature_names', [])
else:
    print(f"WARNING: model_metadata.json not found at {METADATA_PATH}. Feature extraction might be incomplete.")


def extract_features(flow_key, flow):
    """
    Extract features from a flow for ML prediction, matching the full 77 features
    from model_metadata.json.
    """
    sizes = flow["packet_sizes"]
    times = flow["timestamps"]

    if len(times) == 0:
        return None

    duration = times[-1] - times[0] if len(times) > 1 else 0
    iat = np.diff(times) if len(times) > 1 else [0]
    
    total_packets = len(sizes)
    total_bytes = sum(sizes)
    
    # Calculate rates
    flow_bytes_per_s = total_bytes / duration if duration > 0 else 0
    flow_packets_per_s = total_packets / duration if duration > 0 else 0
    
    # Extract protocol from flow_key (5th element: protocol number)
    # Protocol: 6=TCP, 17=UDP, 1=ICMP, etc.
    protocol = flow_key[4] if len(flow_key) >= 5 else 0

    # Initialize a dictionary with all expected features set to 0
    features_dict = {name: 0 for name in FEATURE_NAMES} if FEATURE_NAMES else {}

    # Populate the features that can be derived from the live flow
    features_dict.update({
        "Protocol": protocol,  # CRITICAL: This was missing!
        "Flow Duration": duration,
        "Total Fwd Packets": total_packets,
        "Fwd Packets Length Total": total_bytes,
        "Fwd Packet Length Max": np.max(sizes) if len(sizes) > 0 else 0,
        "Fwd Packet Length Min": np.min(sizes) if len(sizes) > 0 else 0,
        "Fwd Packet Length Mean": np.mean(sizes) if len(sizes) > 0 else 0,
        "Fwd Packet Length Std": np.std(sizes) if len(sizes) > 0 else 0,
        "Flow Bytes/s": flow_bytes_per_s,
        "Flow Packets/s": flow_packets_per_s,
        "Flow IAT Mean": np.mean(iat) if len(iat) > 0 else 0,
        "Flow IAT Std": np.std(iat) if len(iat) > 0 else 0,
        "Flow IAT Max": np.max(iat) if len(iat) > 0 else 0,
        "Flow IAT Min": np.min(iat) if len(iat) > 0 else 0,
        "Fwd IAT Total": sum(iat) if len(iat) > 0 else 0,
        "Fwd IAT Mean": np.mean(iat) if len(iat) > 0 else 0,
        "Fwd IAT Std": np.std(iat) if len(iat) > 0 else 0,
        "Fwd IAT Max": np.max(iat) if len(iat) > 0 else 0,
        "Fwd IAT Min": np.min(iat) if len(iat) > 0 else 0,
        "Fwd Packets/s": flow_packets_per_s,  # Same as Flow Packets/s for unidirectional
        "Packet Length Min": np.min(sizes) if len(sizes) > 0 else 0,
        "Packet Length Max": np.max(sizes) if len(sizes) > 0 else 0,
        "Packet Length Mean": np.mean(sizes) if len(sizes) > 0 else 0,
        "Packet Length Std": np.std(sizes) if len(sizes) > 0 else 0,
        "Packet Length Variance": np.var(sizes) if len(sizes) > 0 else 0,
        "Avg Packet Size": np.mean(sizes) if len(sizes) > 0 else 0,
        "Avg Fwd Segment Size": np.mean(sizes) if len(sizes) > 0 else 0,
        "Subflow Fwd Packets": total_packets,  # Approximate
        "Subflow Fwd Bytes": total_bytes,  # Approximate
        "Fwd Act Data Packets": total_packets,  # Approximate
    })

    df = pd.DataFrame([features_dict])

    # Ensure column order matches training features
    if FEATURE_NAMES:
        df = df[FEATURE_NAMES]

    return df

