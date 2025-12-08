# backend/live_ids/logger.py

import json
import time
from pathlib import Path
import numpy as np

# Get absolute path to logs directory
_logger_file = Path(__file__).resolve()
BACKEND_DIR = _logger_file.parent.parent
LOG_FILE = BACKEND_DIR / "logs" / "ids_alerts.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_alert(flow_key, label, confidence=None, features=None):
    """
    Log an alert to the JSON lines log file.
    
    Args:
        flow_key: Tuple representing the flow (src_ip, dst_ip, src_port, dst_port, protocol)
        label: Predicted label (e.g., "DDoS", "Benign", etc.)
        confidence: Optional confidence score
        features: Optional dict of feature values
    """
    entry = {
        "timestamp": time.time(),
        "flow": str(flow_key),
        "label": label
    }
    
    if confidence is not None:
        entry["confidence"] = round(confidence, 4)
    
    if features is not None:
        # Convert numpy types to native Python types for JSON serialization
        features_clean = {}
        for k, v in features.items():
            if hasattr(v, 'item'):  # numpy scalar
                features_clean[k] = v.item()
            elif isinstance(v, (np.integer, np.floating)):
                features_clean[k] = float(v) if isinstance(v, np.floating) else int(v)
            elif isinstance(v, (int, float, str, bool)) or v is None:
                features_clean[k] = v
            else:
                # Fallback: convert to string
                features_clean[k] = str(v)
        entry["features"] = features_clean
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_latest_alerts(n=50):
    """
    Read the latest n alerts from the log file.
    
    Args:
        n: Number of latest alerts to return
        
    Returns:
        List of alert dictionaries
    """
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            # Get last n lines
            recent_lines = lines[-n:] if len(lines) > n else lines
            alerts = []
            for line in recent_lines:
                try:
                    alerts.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            return alerts
    except Exception:
        return []

