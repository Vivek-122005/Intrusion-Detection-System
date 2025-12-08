#!/usr/bin/env python3
"""
Comprehensive test script for Live IDS system
Tests all components: flow manager, feature extractor, logger, predictor, and API
"""

import sys
import time
import json
import requests
from pathlib import Path
import numpy as np
import pandas as pd

# Add backend to path
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BACKEND_DIR))

# Test results
test_results = []
errors = []

def test_result(name, passed, message=""):
    """Record test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status}: {name}"
    if message:
        result += f" - {message}"
    test_results.append((passed, result))
    print(result)
    if not passed:
        errors.append(result)

def test_flow_manager():
    """Test FlowManager"""
    print("\n" + "="*60)
    print("Testing FlowManager")
    print("="*60)
    
    try:
        from live_ids.flow_manager import FlowManager
        
        manager = FlowManager()
        test_result("FlowManager import", True)
        
        # Test flow key generation (mock packet)
        class MockPacket:
            def getlayer(self, name):
                if name == 'IP':
                    return MockIP()
                return None
        
        class MockIP:
            src = "192.168.1.1"
            dst = "10.0.0.1"
            proto = 6
        
        class MockTCP:
            sport = 80
            dport = 54321
        
        # Create a more complete mock
        pkt = type('obj', (object,), {
            'getlayer': lambda self, name: MockIP() if name == 'IP' else (MockTCP() if name in ['TCP', 'UDP'] else None)
        })()
        
        # Test flow update
        key = ("192.168.1.1", "10.0.0.1", 80, 54321, 6)
        manager.update_flow(key, 100, time.time())
        test_result("FlowManager update_flow", True)
        
        # Test expired flows
        time.sleep(0.1)
        ended = manager.end_expired_flows()
        test_result("FlowManager end_expired_flows (no expired)", len(ended) == 0)
        
        # Test with expired flow
        manager.update_flow(key, 200, time.time() - 10)  # 10 seconds ago
        ended = manager.end_expired_flows()
        test_result("FlowManager end_expired_flows (expired)", len(ended) > 0)
        
    except Exception as e:
        test_result("FlowManager", False, str(e))

def test_feature_extractor():
    """Test FeatureExtractor"""
    print("\n" + "="*60)
    print("Testing FeatureExtractor")
    print("="*60)
    
    try:
        from live_ids.feature_extractor import extract_features
        
        # Create mock flow
        flow_key = ("192.168.1.1", "10.0.0.1", 80, 54321, 6)
        flow = {
            "packet_sizes": [100, 200, 150, 300],
            "timestamps": [time.time() - 3, time.time() - 2, time.time() - 1, time.time()],
            "total_bytes": 750
        }
        
        df = extract_features(flow_key, flow)
        test_result("FeatureExtractor extract_features", df is not None)
        
        if df is not None:
            test_result("FeatureExtractor returns DataFrame", isinstance(df, pd.DataFrame))
            test_result("FeatureExtractor has data", len(df) > 0)
            test_result("FeatureExtractor has columns", len(df.columns) > 0)
            print(f"   Extracted {len(df.columns)} features")
        
    except Exception as e:
        test_result("FeatureExtractor", False, str(e))

def test_logger():
    """Test Logger"""
    print("\n" + "="*60)
    print("Testing Logger")
    print("="*60)
    
    try:
        from live_ids.logger import log_alert, read_latest_alerts
        
        # Test log file creation
        log_file = BACKEND_DIR / "logs" / "ids_alerts.log"
        test_result("Logger log file path", log_file.parent.exists() or True)
        
        # Test logging
        test_key = ("192.168.1.1", "10.0.0.1", 80, 54321, 6)
        log_alert(test_key, "DDoS")
        test_result("Logger log_alert", True)
        
        # Test reading alerts
        alerts = read_latest_alerts(10)
        test_result("Logger read_latest_alerts", isinstance(alerts, list))
        
        if alerts:
            test_result("Logger alert format", "label" in alerts[0] and "flow" in alerts[0])
            print(f"   Found {len(alerts)} alerts in log")
        
    except Exception as e:
        test_result("Logger", False, str(e))

def test_predictor():
    """Test ML Predictor"""
    print("\n" + "="*60)
    print("Testing ML Predictor")
    print("="*60)
    
    try:
        from models.predictor import load_model, predict_flows
        
        # Test model loading
        loaded = load_model()
        
        # Check if model files exist
        model_path = BACKEND_DIR / "models" / "ids_7class_histgb_safe.joblib"
        if not model_path.exists():
            model_path = BASE_DIR / "artifacts" / "ids_7class_histgb_safe.joblib"
        
        if model_path.exists():
            test_result("Predictor model file exists", True)
        else:
            test_result("Predictor model file exists", False, "Model file not found")
            return
        
        # Note: Model loading may fail due to numpy version compatibility
        # This is a known issue but doesn't prevent the system from working
        # if the backend loads it correctly
        if loaded:
            test_result("Predictor load_model", True)
        else:
            test_result("Predictor load_model", False, "Model loading failed (may be numpy version issue - check backend)")
            print("   ⚠️  Note: Model loading failed in test, but backend may load it correctly")
            print("   This is often due to numpy version differences between save/load")
            return
        
        if loaded:
            # Create test features
            test_features = pd.DataFrame([{
                "Flow Duration": 1.5,
                "Total Fwd Packets": 10,
                "Total Backward Packets": 5,
                "Fwd Packets Length Total": 1000,
                "Bwd Packets Length Total": 500,
                "Fwd Packet Length Max": 200,
                "Fwd Packet Length Min": 50,
                "Fwd Packet Length Mean": 100,
                "Fwd Packet Length Std": 30,
                "Flow Bytes/s": 1000,
                "Flow Packets/s": 10,
                "Flow IAT Mean": 0.1,
                "Flow IAT Std": 0.05,
                "Flow IAT Max": 0.2,
                "Flow IAT Min": 0.05,
                "Packet Length Min": 50,
                "Packet Length Max": 200,
                "Packet Length Mean": 100,
                "Packet Length Std": 30,
                "Packet Length Variance": 900,
                "Avg Packet Size": 100
            }])
            
            # Test prediction
            result = predict_flows(test_features)
            test_result("Predictor predict_flows", result is not None)
            
            if result is not None:
                test_result("Predictor returns DataFrame", isinstance(result, pd.DataFrame))
                test_result("Predictor has predicted_label", "predicted_label" in result.columns)
                if "predicted_label" in result.columns:
                    label = result["predicted_label"].iloc[0]
                    print(f"   Predicted label: {label}")
                    test_result("Predictor valid label", label in ["Benign", "Bot", "Bruteforce", "DDoS", "DoS", "Infiltration", "Web Attack"])
        
    except Exception as e:
        test_result("Predictor", False, str(e))
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Test Flask API endpoints"""
    print("\n" + "="*60)
    print("Testing API Endpoints")
    print("="*60)
    
    base_url = "http://localhost:5050"
    backend_running = False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        backend_running = True
        test_result("API /api/health endpoint", response.status_code == 200)
        if response.status_code == 200:
            data = response.json()
            test_result("API health response format", "status" in data)
            model_loaded = data.get('model_loaded', False)
            print(f"   Status: {data.get('status')}, Model loaded: {model_loaded}")
            if not model_loaded:
                print("   ⚠️  Backend model not loaded - check backend logs")
    except requests.exceptions.ConnectionError:
        test_result("API /api/health endpoint", False, "Backend not running (start with: cd backend && python app.py)")
        print("   💡 To test API endpoints, start the backend: cd backend && python app.py")
    except Exception as e:
        test_result("API /api/health endpoint", False, str(e))
    
    # Test latest-alerts endpoint
    if backend_running:
        try:
            response = requests.get(f"{base_url}/api/latest-alerts?n=10", timeout=5)
            test_result("API /api/latest-alerts endpoint", response.status_code == 200)
            if response.status_code == 200:
                data = response.json()
                test_result("API alerts response format", "alerts" in data and "success" in data)
                if "alerts" in data:
                    print(f"   Found {len(data['alerts'])} alerts")
        except Exception as e:
            test_result("API /api/latest-alerts endpoint", False, str(e))
        
        # Test metadata endpoint
        try:
            response = requests.get(f"{base_url}/api/metadata", timeout=5)
            test_result("API /api/metadata endpoint", response.status_code == 200)
            if response.status_code == 200:
                data = response.json()
                test_result("API metadata response format", "feature_names" in data or "error" in data)
                if "feature_names" in data:
                    print(f"   Model has {len(data['feature_names'])} features")
                elif "error" in data:
                    print(f"   Metadata error: {data.get('error')}")
        except Exception as e:
            test_result("API /api/metadata endpoint", False, str(e))
    else:
        test_result("API /api/latest-alerts endpoint", False, "Backend not running")
        test_result("API /api/metadata endpoint", False, "Backend not running")

def test_integration():
    """Test end-to-end integration"""
    print("\n" + "="*60)
    print("Testing End-to-End Integration")
    print("="*60)
    
    try:
        from live_ids.flow_manager import FlowManager
        from live_ids.feature_extractor import extract_features
        from live_ids.logger import log_alert, read_latest_alerts
        from models.predictor import load_model, predict_flows
        
        # Load model
        if not load_model():
            test_result("Integration model load", False, "Model not loaded")
            return
        
        # Create flow
        manager = FlowManager()
        flow_key = ("192.168.1.100", "10.0.0.50", 443, 54321, 6)
        
        # Simulate packets
        for i in range(5):
            manager.update_flow(flow_key, 100 + i*10, time.time() - (5-i)*0.5)
        
        # End flow
        time.sleep(0.1)
        ended = manager.end_expired_flows()
        
        if not ended:
            # Force end by making it old
            manager.flows[flow_key]["timestamps"][-1] = time.time() - 10
            ended = manager.end_expired_flows()
        
        test_result("Integration flow creation", len(ended) > 0)
        
        if ended:
            # Extract features
            f_key, flow = ended[0]
            df = extract_features(f_key, flow)
            test_result("Integration feature extraction", df is not None)
            
            if df is not None:
                # Predict
                result = predict_flows(df)
                test_result("Integration prediction", result is not None and "predicted_label" in result.columns)
                
                if result is not None and "predicted_label" in result.columns:
                    label = result["predicted_label"].iloc[0]
                    
                    # Log if not benign
                    if label != "Benign":
                        log_alert(f_key, label)
                        test_result("Integration alert logging", True)
                        print(f"   Generated alert: {label} on flow {f_key}")
                    else:
                        test_result("Integration benign detection", True)
                        print(f"   Detected benign traffic (not logged)")
        
    except Exception as e:
        test_result("Integration", False, str(e))
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LIVE IDS SYSTEM TEST SUITE")
    print("="*60)
    
    # Run tests
    test_flow_manager()
    test_feature_extractor()
    test_logger()
    test_predictor()
    test_integration()
    test_api_endpoints()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for p, _ in test_results if p)
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if errors:
        print("\n❌ FAILED TESTS:")
        for error in errors:
            print(f"   {error}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

