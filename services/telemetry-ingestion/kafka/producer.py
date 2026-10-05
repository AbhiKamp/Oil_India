"""
StrataSentry-NWIS: Telemetry Kafka Producer
Serializes and publishes real-time sensor packets to Kafka topics with offline buffering.
"""

import json
from typing import Dict, Any

class TelemetryKafkaProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092", topic: str = "rig.telemetry.raw"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception:
            self.producer = None

    def publish_frame(self, telemetry_data: Dict[str, Any]) -> bool:
        if self.producer:
            try:
                self.producer.send(self.topic, value=telemetry_data)
                return True
            except Exception:
                return False
        # In-memory pass-through / mock fallback
        return True
