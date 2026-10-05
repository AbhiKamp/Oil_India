"""
StrataSentry-NWIS: Telemetry Kafka Consumer
Consumes real-time sensor packets from Kafka and pushes to analytical queues.
"""

import json
from typing import Iterator, Dict, Any

class TelemetryKafkaConsumer:
    def __init__(self, bootstrap_servers: str = "localhost:9092", topic: str = "rig.telemetry.raw", group_id: str = "nwis-telemetry-workers"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None

    def stream_telemetry(self) -> Iterator[Dict[str, Any]]:
        try:
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            for msg in self.consumer:
                yield msg.value
        except Exception:
            # Yield empty generator if Kafka is unavailable
            return
