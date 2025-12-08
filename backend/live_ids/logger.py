# backend/live_ids/logger.py

import json
import time
from pathlib import Path

# Get absolute path to logs directory
_logger_file = Path(__file__).resolve()
BACKEND_DIR = _logger_file.parent.parent
LOG_FILE = BACKEND_DIR / "logs" / "ids_alerts.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_alert(flow_key, label, confidence=None):
    """
    Log an alert to the JSON lines log file.
    
    Args:
        flow_key: Tuple representing the flow (src_ip, dst_ip, src_port, dst_port, protocol)
        label: Predicted label (e.g., "DDoS", "Benign", etc.)
        confidence: Optional confidence score
    """
    entry = {
        "timestamp": time.time(),
        "flow": str(flow_key),
        "label": label
    }
    
    if confidence is not None:
        entry["confidence"] = confidence
    
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

