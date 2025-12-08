# backend/live_ids/flow_manager.py

import time

FLOW_TIMEOUT = 5  # seconds of inactivity = flow end


class FlowManager:
    def __init__(self):
        self.flows = {}

    def get_flow_key(self, pkt):
        try:
            # Extract IP layer
            ip_layer = pkt.getlayer('IP')
            if ip_layer is None:
                return None
            
            # Extract transport layer (TCP/UDP)
            transport = pkt.getlayer('TCP') or pkt.getlayer('UDP')
            if transport is None:
                return None
            
            # Create flow key: (src_ip, dst_ip, src_port, dst_port, protocol)
            return (
                ip_layer.src,
                ip_layer.dst,
                transport.sport,
                transport.dport,
                ip_layer.proto
            )
        except Exception:
            return None

    def update_flow(self, key, packet_size, timestamp):
        flow = self.flows.setdefault(key, {
            "packet_sizes": [],
            "timestamps": [],
            "total_bytes": 0
        })

        flow["packet_sizes"].append(packet_size)
        flow["timestamps"].append(timestamp)
        flow["total_bytes"] += packet_size

    def end_expired_flows(self):
        now = time.time()
        ended = []

        for key, flow in list(self.flows.items()):
            if len(flow["timestamps"]) > 0:
                if now - flow["timestamps"][-1] > FLOW_TIMEOUT:
                    ended.append((key, flow))
                    del self.flows[key]

        return ended

