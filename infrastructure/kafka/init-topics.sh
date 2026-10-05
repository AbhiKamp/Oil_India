#!/bin/bash
# Initialize StrataSentry-NWIS Kafka Topics

set -e

KAFKA_BROKER=${KAFKA_BROKER:-"localhost:9092"}

echo "[*] Creating StrataSentry telemetry topics on $KAFKA_BROKER..."

# Raw high-frequency sensor frames (10 Hz)
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --replication-factor 1 --partitions 3 --topic rig.telemetry.raw

# Standardized and smoothed 1 Hz frames
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --replication-factor 1 --partitions 3 --topic rig.telemetry.standardized

# High-priority instant alerts
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --replication-factor 1 --partitions 1 --topic rig.alerts.immediate

echo "[+] Kafka topics initialized successfully."
