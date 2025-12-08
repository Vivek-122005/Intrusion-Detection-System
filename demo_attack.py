#!/usr/bin/env python3
"""
Demo Attack Simulator for IDS Presentation

This script simulates various attack types for demonstration purposes.
Use with permission and only on your own systems.
"""

import subprocess
import time
import sys
import argparse
from pathlib import Path

def simulate_bruteforce_ssh(target="localhost", port=22, attempts=50):
    """Simulate SSH bruteforce attack using nc (netcat)"""
    print(f"🔥 Simulating BRUTEFORCE attack on {target}:{port}")
    print(f"   Attempting {attempts} connections...")
    
    for i in range(attempts):
        try:
            # Use nc to attempt connection
            result = subprocess.run(
                ["nc", "-zv", "-w", "1", target, str(port)],
                capture_output=True,
                timeout=2
            )
            if i % 10 == 0:
                print(f"   Connection attempt {i+1}/{attempts}")
            time.sleep(0.1)  # Small delay between attempts
        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            print("❌ Error: 'nc' (netcat) not found. Install with: brew install netcat")
            return False
    
    print("✅ Bruteforce simulation complete!")
    return True

def simulate_dos_http(target="http://google.com", requests=200):
    """Simulate DoS attack using curl"""
    print(f"🔥 Simulating DoS attack on {target}")
    print(f"   Sending {requests} rapid requests...")
    
    try:
        # Use curl to send rapid requests
        for i in range(requests):
            subprocess.Popen(
                ["curl", "-s", "-o", "/dev/null", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if i % 20 == 0:
                print(f"   Request {i+1}/{requests}")
            time.sleep(0.05)  # Small delay
        print("✅ DoS simulation complete!")
        return True
    except FileNotFoundError:
        print("❌ Error: 'curl' not found. Install with: brew install curl")
        return False

def simulate_bruteforce_http(target="http://google.com", requests=100):
    """Simulate HTTP bruteforce using curl"""
    print(f"🔥 Simulating HTTP BRUTEFORCE on {target}")
    print(f"   Sending {requests} rapid requests...")
    
    try:
        for i in range(requests):
            subprocess.Popen(
                ["curl", "-s", "-o", "/dev/null", target],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if i % 10 == 0:
                print(f"   Request {i+1}/{requests}")
            time.sleep(0.1)
        print("✅ HTTP Bruteforce simulation complete!")
        return True
    except FileNotFoundError:
        print("❌ Error: 'curl' not found")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Simulate attacks for IDS demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulate SSH bruteforce (requires SSH server running)
  python3 demo_attack.py --type bruteforce --target localhost --port 22

  # Simulate HTTP DoS
  python3 demo_attack.py --type dos --target http://google.com

  # Simulate HTTP bruteforce
  python3 demo_attack.py --type http-bruteforce --target http://google.com
        """
    )
    
    parser.add_argument(
        '--type',
        choices=['bruteforce', 'dos', 'http-bruteforce'],
        default='bruteforce',
        help='Type of attack to simulate (default: bruteforce)'
    )
    
    parser.add_argument(
        '--target',
        default='localhost',
        help='Target host or URL (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=22,
        help='Target port for bruteforce (default: 22)'
    )
    
    parser.add_argument(
        '--attempts',
        type=int,
        default=50,
        help='Number of connection attempts (default: 50)'
    )
    
    parser.add_argument(
        '--requests',
        type=int,
        default=200,
        help='Number of HTTP requests (default: 200)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 IDS DEMO ATTACK SIMULATOR")
    print("=" * 60)
    print(f"Attack Type: {args.type.upper()}")
    print(f"Target: {args.target}")
    print("=" * 60)
    print()
    
    if args.type == 'bruteforce':
        success = simulate_bruteforce_ssh(args.target, args.port, args.attempts)
    elif args.type == 'dos':
        success = simulate_dos_http(args.target, args.requests)
    elif args.type == 'http-bruteforce':
        success = simulate_bruteforce_http(args.target, args.requests)
    else:
        print(f"❌ Unknown attack type: {args.type}")
        return 1
    
    if success:
        print()
        print("=" * 60)
        print("✅ Attack simulation completed!")
        print("   Check your IDS dashboard for alerts.")
        print("=" * 60)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())

