# Telemetry Ingestion Service

High-speed streaming ingestion pipeline for rig-site MWD, LWD, and surface instrumentation.

---

## Components

- **`witsml/`**:
  - `witsml_parser.py`: Parses WITSML 1.4.1/2.0 XML logs and real-time records.
  - `soap_client.py`: Client for interacting with rig WITSML servers.
- **`kafka/`**:
  - `producer.py`: Publishes standardized sensor packets to partitioned Kafka topics.
  - `consumer.py`: Consumer reading streaming sensor frames.
- **`producers/`**:
  - `mock_rig_producer.py`: Generates continuous drilling streams with configurable anomalies.
- **`consumers/`**:
  - `stream_processor.py`: In-memory sliding buffer calculating rolling derivatives: $\frac{d(SPP)}{dt}$, torque volatility, flow delta, and Mechanical Specific Energy ($\text{MSE}$).
