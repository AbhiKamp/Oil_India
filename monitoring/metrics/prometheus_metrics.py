"""
StrataSentry-NWIS: Prometheus Drilling & Inference Metrics
"""

class DrillingMetrics:
    def __init__(self):
        self.telemetry_frames_ingested = 0
        self.alerts_generated = 0
        self.rag_queries_served = 0

    def record_frame(self):
        self.telemetry_frames_ingested += 1

    def record_alert(self):
        self.alerts_generated += 1

    def record_rag_query(self):
        self.rag_queries_served += 1

    def get_metrics_summary(self):
        return {
            "telemetry_frames_total": self.telemetry_frames_ingested,
            "alerts_generated_total": self.alerts_generated,
            "rag_queries_total": self.rag_queries_served
        }
