# 🧪 Test Values for Manual Input

This guide provides test values for testing the IDS model classification via the manual input form.

## 📋 Quick Test Values

### ✅ Scenario 1: Normal Benign Traffic (Web Browsing)
**Expected Classification:** `Benign`

Click the **"Fill Sample (Benign Traffic)"** button in the manual input form to automatically fill all 77 features with realistic values representing normal web browsing traffic.

**Key Characteristics:**
- Protocol: 6 (TCP)
- Balanced forward/backward packets
- Normal packet sizes (40-1460 bytes)
- Standard TCP flags (SYN, ACK, FIN)
- Moderate flow duration

### ⚠️ Scenario 2: DDoS Attack Pattern
**Expected Classification:** `DDOS attack-HOIC` or similar DDoS attack

**Key Values:**
```
Protocol: 6
Flow Duration: 50000
Total Fwd Packets: 10000
Total Backward Packets: 10
Fwd Packets Length Total: 500000
Flow Bytes/s: 10000
Flow Packets/s: 200
SYN Flag Count: 10000
ACK Flag Count: 10
Fwd IAT Mean: 50
Flow IAT Mean: 25
```

### 🔴 Scenario 3: Brute Force Attack
**Expected Classification:** `FTP-BruteForce`, `SSH-Bruteforce`, or `Brute Force -Web`

**Key Values:**
```
Protocol: 6
Flow Duration: 20000
Total Fwd Packets: 500
Total Backward Packets: 500
Flow Packets/s: 50
RST Flag Count: 50
FIN Flag Count: 100
Flow IAT Mean: 400
Fwd IAT Mean: 400
```

### 🟡 Scenario 4: SQL Injection Attack
**Expected Classification:** `SQL Injection`

**Key Values:**
```
Protocol: 6
Flow Duration: 15000
Total Fwd Packets: 200
Total Backward Packets: 150
Fwd Header Length: 5000
Bwd Header Length: 2000
PSH Flag Count: 50
Flow Bytes/s: 800
Avg Fwd Segment Size: 150
Avg Bwd Segment Size: 80
```

## 📝 Complete Feature List with Typical Ranges

### Basic Flow Information
- **Protocol**: 6 (TCP), 17 (UDP), 1 (ICMP)
- **Flow Duration**: 1000-1000000 (milliseconds)
- **Total Fwd Packets**: 1-10000+
- **Total Backward Packets**: 1-10000+

### Forward Packets
- **Fwd Packets Length Total**: 40-1000000 (bytes)
- **Fwd Packet Length Max**: 40-1500 (bytes)
- **Fwd Packet Length Min**: 0-1460 (bytes)
- **Fwd Packet Length Mean**: 0-1000 (bytes)
- **Fwd Packet Length Std**: 0-500
- **Fwd Packets/s**: 0-1000
- **Fwd Header Length**: 0-50000
- **Fwd IAT Total**: 0-1000000 (ms)
- **Fwd IAT Mean**: 0-100000 (ms)
- **Fwd IAT Std**: 0-50000
- **Fwd IAT Max**: 0-1000000
- **Fwd IAT Min**: 0-1000
- **Fwd PSH Flags**: 0-100
- **Fwd URG Flags**: 0-10
- **Fwd Act Data Packets**: 0-10000
- **Fwd Seg Size Min**: 0-1460

### Backward Packets
- **Bwd Packets Length Total**: 0-1000000
- **Bwd Packet Length Max**: 0-1500
- **Bwd Packet Length Min**: 0-1460
- **Bwd Packet Length Mean**: 0-1000
- **Bwd Packet Length Std**: 0-500
- **Bwd Packets/s**: 0-1000
- **Bwd Header Length**: 0-50000
- **Bwd IAT Total**: 0-1000000
- **Bwd IAT Mean**: 0-100000
- **Bwd IAT Std**: 0-50000
- **Bwd IAT Max**: 0-1000000
- **Bwd IAT Min**: 0-1000
- **Bwd PSH Flags**: 0-100
- **Bwd URG Flags**: 0-10

### Flow Statistics
- **Flow Bytes/s**: 0-100000
- **Flow Packets/s**: 0-10000
- **Flow IAT Mean**: 0-100000
- **Flow IAT Std**: 0-50000
- **Flow IAT Max**: 0-1000000
- **Flow IAT Min**: 0-1000
- **Down/Up Ratio**: 0-100

### Packet Statistics
- **Packet Length Min**: 0-1460
- **Packet Length Max**: 0-1500
- **Packet Length Mean**: 0-1000
- **Packet Length Std**: 0-500
- **Packet Length Variance**: 0-250000
- **Avg Packet Size**: 0-1000

### TCP Flags
- **FIN Flag Count**: 0-100
- **SYN Flag Count**: 0-10000
- **RST Flag Count**: 0-1000
- **PSH Flag Count**: 0-1000
- **ACK Flag Count**: 0-100000
- **URG Flag Count**: 0-100
- **CWE Flag Count**: 0-100
- **ECE Flag Count**: 0-100

### Timing Statistics
- **Active Mean**: 0-1000000
- **Active Std**: 0-500000
- **Active Max**: 0-1000000
- **Active Min**: 0-100000
- **Idle Mean**: 0-500000
- **Idle Std**: 0-250000
- **Idle Max**: 0-100000
- **Idle Min**: 0-1000

## 🎯 Testing Strategy

1. **Start with Benign Traffic**
   - Click "Fill Sample (Benign Traffic)" button
   - Submit and verify classification is `Benign`

2. **Test Attack Patterns**
   - Modify specific values to match attack characteristics
   - Submit and check classification matches attack type

3. **Edge Cases**
   - Very high/low values
   - Zero values for optional fields
   - Extreme ratios

## 🔍 Model Classes (15 Total)

The model can classify traffic into these categories:
1. Benign
2. Bot
3. Brute Force -Web
4. Brute Force -XSS
5. DDOS attack-HOIC
6. DDOS attack-LOIC-UDP
7. DDoS attacks-LOIC-HTTP
8. DoS attacks-GoldenEye
9. DoS attacks-Hulk
10. DoS attacks-SlowHTTPTest
11. DoS attacks-Slowloris
12. FTP-BruteForce
13. Infilteration
14. SQL Injection
15. SSH-Bruteforce

## 💡 Tips

- Use the "Fill Sample" button as a starting point
- Modify values incrementally to see classification changes
- Focus on key indicators: packet counts, flags, IAT (Inter-Arrival Time)
- DDoS attacks typically show: high packet rates, many SYN flags, low IAT
- Brute force shows: many connection attempts (FIN/RST flags), moderate duration
- Injection attacks show: large headers, specific protocol patterns

