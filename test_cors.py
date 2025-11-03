#!/usr/bin/env python3
"""Quick test to verify CORS headers are set"""
import requests

try:
    response = requests.options('http://localhost:5000/api/health')
    print("OPTIONS request to /api/health:")
    print(f"Status: {response.status_code}")
    print("Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"  {key}: {value}")
    
    response = requests.get('http://localhost:5000/api/health')
    print("\nGET request to /api/health:")
    print(f"Status: {response.status_code}")
    print("CORS Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"  {key}: {value}")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure Flask app is running on port 5000")
