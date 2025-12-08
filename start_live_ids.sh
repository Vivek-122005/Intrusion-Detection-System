#!/bin/bash

echo "🚀 Starting Live IDS Packet Sniffer..."
echo "⚠️  Note: This requires sudo privileges for packet capture"
echo ""

# Detect interface (macOS or Linux)
IFACE=""

# macOS interface detection
if command -v route >/dev/null 2>&1; then
    IFACE=$(route get default 2>/dev/null | awk '/interface: / {print $2}')
fi

# Linux interface detection
if [[ -z "$IFACE" ]] && command -v ip >/dev/null 2>&1; then
    IFACE=$(ip route | awk '/default/ {print $5}')
fi

# Fallback to common macOS interface
if [[ -z "$IFACE" ]]; then
    # Try common macOS interfaces
    if ifconfig en0 >/dev/null 2>&1; then
        IFACE="en0"
    elif ifconfig en1 >/dev/null 2>&1; then
        IFACE="en1"
    else
        echo "❌ Could not detect network interface. Please specify manually:"
        echo "   sudo ./start_live_ids.sh <interface_name>"
        echo ""
        echo "Available interfaces:"
        ifconfig -l 2>/dev/null || ip link show 2>/dev/null || echo "Use: ifconfig or ip link show"
        exit 1
    fi
fi

echo "📡 Using network interface: $IFACE"
echo ""

# Change to project directory
cd "$(dirname "$0")" || exit 1

# Start the packet sniffer with --iface flag
sudo python3 -m backend.live_ids.packet_sniffer --iface "$IFACE"
