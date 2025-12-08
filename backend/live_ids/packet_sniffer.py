# backend/live_ids/packet_sniffer.py

from scapy.all import sniff
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BACKEND_DIR))

# Try different import paths
try:
    from live_ids.flow_manager import FlowManager
    from live_ids.feature_extractor import extract_features
    from live_ids.logger import log_alert
    from models.predictor import predict_flows, load_model
except ImportError:
    # Fallback for different execution contexts
    from backend.live_ids.flow_manager import FlowManager
    from backend.live_ids.feature_extractor import extract_features
    from backend.live_ids.logger import log_alert
    from backend.models.predictor import predict_flows, load_model

flow_manager = FlowManager()

# Whitelist for known benign protocols/ports
BENIGN_WHITELIST = {
    'ports': {53, 67, 68, 123, 1900, 5353, 137, 138, 139},  # DNS, DHCP, NTP, SSDP, mDNS, NetBIOS
    'multicast_prefixes': ['224.0.0.', '239.255.255.', '239.0.0.'],  # Multicast IPs
    'ip_prefixes': [
        '8.8.8.',      # Google DNS
        '8.8.4.',
        '142.250.',    # Google (expanded)
        '142.251.',    # Google (expanded)
        '142.252.',    # Google (expanded)
        '172.217.',    # Google
        '216.58.',     # Google
        '17.248.',     # Apple
        '35.186.',     # GCP
        '34.160.',     # GCP
        '100.24.'      # AWS
    ]
}

# Only run ML on "interesting" ports that might be attack targets
SUSPECT_PORTS = {21, 22, 23, 80, 8080, 443}  # FTP, SSH, Telnet, HTTP, HTTP-alt, HTTPS

def is_whitelisted(flow_key):
    """
    Check if a flow should be whitelisted as Benign based on port/IP patterns.
    Returns True if flow should be considered Benign without ML prediction.
    """
    if len(flow_key) < 5:
        return False
    
    src_ip, dst_ip, src_port, dst_port, protocol = flow_key
    
    # Fix #1: QUIC/HTTP3 traffic (UDP 443) - whitelist all UDP:443
    # QUIC uses UDP 443 with big bursts, looks like DoS/Bruteforce to ML
    if protocol == 17 and dst_port == 443:  # UDP protocol = 17
        return True
    
    # Check ports
    if src_port in BENIGN_WHITELIST['ports'] or dst_port in BENIGN_WHITELIST['ports']:
        return True
    
    # Check multicast IPs
    for prefix in BENIGN_WHITELIST['multicast_prefixes']:
        if dst_ip.startswith(prefix):
            return True
    
    # Fix #2: Expanded cloud IP prefixes
    for prefix in BENIGN_WHITELIST.get('ip_prefixes', []):
        if src_ip.startswith(prefix) or dst_ip.startswith(prefix):
            return True
    
    return False


def should_process_flow(flow_key, flow):
    """
    Determine if a flow should be sent to ML model.
    
    Filters out flows that don't match CICIDS training data patterns:
    - Single-packet or very small flows (< 5 packets)
    - Ultra-short flows (duration < 0.01s)
    - Private LAN traffic (10.x.x.x to 10.x.x.x)
    - Whitelisted benign protocols
    
    Returns:
        tuple: (should_process: bool, reason: str)
    """
    if len(flow_key) < 5:
        return False, "Invalid flow key"
    
    src_ip, dst_ip, src_port, dst_port, protocol = flow_key
    
    # 1. Check whitelist first (skip ML for known benign protocols)
    if is_whitelisted(flow_key):
        return False, "Whitelisted port/IP"
    
    # 2. Calculate flow statistics
    packet_count = len(flow['packet_sizes'])
    if len(flow['timestamps']) > 1:
        duration = flow['timestamps'][-1] - flow['timestamps'][0]
    else:
        duration = 0
    
    # 3. Ignore flows with < 5 packets (CICIDS never has such small flows)
    if packet_count < 5:
        return False, f"Too few packets ({packet_count} < 5)"
    
    # 4. Ignore ultra-short flows (duration < 0.01s)
    # CICIDS flows have meaningful durations (0.2s - 100s)
    if duration < 0.01:
        return False, f"Duration too short ({duration:.4f}s < 0.01s)"
    
    # 5. Ignore private LAN traffic (10.x.x.x to 10.x.x.x)
    # This is typically local network noise, not internet traffic like CICIDS
    if src_ip.startswith("10.") and dst_ip.startswith("10."):
        return False, "Private LAN traffic"
    
    # 6. Only run ML on "interesting" ports that might be attack targets
    # This reduces false positives from random ports
    if dst_port not in SUSPECT_PORTS:
        return False, f"Non-suspect port ({dst_port})"
    
    # Flow passes all filters - should be processed by ML
    return True, "OK"

def process_packet(pkt):
    """Process each captured packet"""
    key = flow_manager.get_flow_key(pkt)
    if key is None:
        return

    size = len(pkt)
    timestamp = time.time()
    flow_manager.update_flow(key, size, timestamp)

    # Handle ended flows
    ended = flow_manager.end_expired_flows()

    for f_key, flow in ended:
        try:
            # Apply comprehensive filtering before ML prediction
            should_process, reason = should_process_flow(f_key, flow)
            
            if not should_process:
                # Flow filtered out - skip ML prediction
                # Uncomment for debugging: print(f"⏭️  Filtered: {reason} - Flow {f_key[:2]}")
                continue
            
            # Extract features
            df = extract_features(f_key, flow)
            if df is None:
                continue

            # Make prediction with probabilities
            result = predict_flows(df)
            label = result["predicted_label"].iloc[0]
            confidence = result["prediction_confidence"].iloc[0]
            
            # Calculate flow stats once for validation and debugging
            packet_count = len(flow['packet_sizes'])
            if len(flow['timestamps']) > 1:
                duration = flow['timestamps'][-1] - flow['timestamps'][0]
            else:
                duration = 0
            
            protocol = f_key[4] if len(f_key) >= 5 else 0
            protocol_name = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(protocol, f"Proto-{protocol}")
            
            # Debug: Print protocol and key features
            print(f"🔍 Flow {f_key[:2]} Protocol={protocol_name}({protocol}), "
                  f"Packets={packet_count}, "
                  f"Duration={duration:.3f}s, "
                  f"Prediction={label} (Confidence: {confidence:.4f})")

            # Fix #3: Protocol-based validation
            # UDP flows can NEVER be Bruteforce or Infiltration (these are TCP-only attacks)
            if protocol == 17 and label in ["Bruteforce", "Infiltration"]:  # UDP = 17
                print(f"⚠️  Rejected: {label} on UDP flow (impossible attack signature) - Flow {f_key[:2]}")
                continue  # Ignore impossible predictions
            
            # Fix #4: Realistic flow validation for Bruteforce
            # CICIDS Bruteforce flows were: TCP only, 30-200 packets, duration >1s, ports 22/80/443
            if label == "Bruteforce":
                # Bruteforce must be TCP (protocol 6)
                if protocol != 6:
                    print(f"⚠️  Rejected: Bruteforce on non-TCP flow (protocol {protocol}) - Flow {f_key[:2]}")
                    continue
                
                # Bruteforce must have at least 30 packets (CICIDS minimum)
                if packet_count < 30:
                    print(f"⚠️  Rejected: Bruteforce with only {packet_count} packets (need 30+) - Flow {f_key[:2]}")
                    continue
                
                # Bruteforce must have duration > 1s
                if duration < 1.0:
                    print(f"⚠️  Rejected: Bruteforce with duration {duration:.3f}s (need >1s) - Flow {f_key[:2]}")
                    continue
            
            # Only alert if:
            # 1. Not Benign AND
            # 2. Confidence meets class-specific threshold
            #    - Infiltration/Bruteforce: 0.99 (very high - these are often false positives)
            #    - Other classes: 0.9 (high confidence)
            if label != "Benign":
                if label in ["Infiltration", "Bruteforce"]:
                    min_conf = 0.99
                else:
                    min_conf = 0.9
                
                if confidence >= min_conf:
                    log_alert(f_key, label, confidence)
                    print(f"🚨 ALERT: {label} detected on flow {f_key} (Confidence: {confidence:.4f})")
            # else:
                # Optional: print benign flows for debugging (can be removed)
                # print(f"✅ BENIGN: {label} detected on flow {f_key} (Confidence: {confidence:.4f})")
        except Exception as e:
            print(f"Error processing flow {f_key}: {e}")
            import traceback
            traceback.print_exc()


def start_sniffer(interface=None):
    """
    Start the packet sniffer.
    
    Args:
        interface: Network interface name (e.g., 'en0' for macOS, 'eth0' for Linux)
                   If None, uses default interface
    """
    # Load model first
    if not load_model():
        print("ERROR: Failed to load ML model. Cannot start sniffer.")
        return
    
    print("Starting live IDS...")
    print("Press Ctrl+C to stop")
    
    try:
        if interface:
            sniff(iface=interface, prn=process_packet, store=False)
        else:
            # Use default interface
            sniff(prn=process_packet, store=False)
    except KeyboardInterrupt:
        print("\nStopping packet sniffer...")
    except Exception as e:
        print(f"Error in packet sniffer: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Live IDS Packet Sniffer')
    parser.add_argument('--iface', type=str, help='Network interface name (e.g., en0, eth0)')
    parser.add_argument('interface', nargs='?', help='Network interface name (positional argument)')
    
    args = parser.parse_args()
    
    # Use --iface flag first, then positional argument, then None
    interface = args.iface or args.interface
    
    start_sniffer(interface)

