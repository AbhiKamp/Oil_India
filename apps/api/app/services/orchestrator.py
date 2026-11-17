"""
StrataSentry-NWIS: Core API Service Orchestrator
Bridges domain microservices with FastAPI gateway routes.
"""

import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app import service_packages  # Register hyphenated service packages for direct callers.

from services.well_geometry.trajectory_builder import TrajectoryBuilder
from services.risk_engine.inference.predictor import DrillingRiskPredictor
from services.physics_validation.hydraulics import BinghamPlasticHydraulics
from services.physics_validation.ecd import DynamicECDCalculator
from services.rag_engine.retrieval.qdrant_retriever import QdrantRetriever
from services.rag_engine.llm.mistral_client import MistralDrillingCopilot
from services.risk_fusion.fusion_engine import RiskFusionEngine
from services.telemetry_ingestion.consumers.stream_processor import TelemetryStreamProcessor
from .report_data import events as source_events
from .report_data import formations as source_formations

class DomainOrchestrator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DomainOrchestrator, cls).__new__(cls)
            cls._instance._init_services()
        return cls._instance

    def _init_services(self):
        self.traj_builder = TrajectoryBuilder()
        self.risk_predictor = DrillingRiskPredictor()
        self.hydraulics = BinghamPlasticHydraulics()
        self.ecd_calc = DynamicECDCalculator()
        self.retriever = QdrantRetriever()
        self.copilot = MistralDrillingCopilot()
        self.fusion = RiskFusionEngine()
        self.stream_processors = {}

        # Load synthetic initial state
        self._load_synthetic_data()

    def _load_synthetic_data(self):
        # 1. Load Wells
        wells_path = os.path.join(PROJECT_ROOT, 'data', 'synthetic', 'wells', 'wells.json')
        if os.path.exists(wells_path):
            with open(wells_path, 'r') as f:
                self.wells = json.load(f)
        else:
            self.wells = []

        # 2. Load Surveys & Trajectory for NHK-421
        surveys_path = os.path.join(PROJECT_ROOT, 'data', 'synthetic', 'surveys', 'nhk421_directional_surveys.csv')
        if os.path.exists(surveys_path):
            df_surveys = pd.read_csv(surveys_path)
            surveys_list = df_surveys.to_dict('records')
            self.trajectory_nhk421 = self.traj_builder.build_trajectory(surveys_list)
        else:
            self.trajectory_nhk421 = []

        self.refresh_knowledge()

        # Replay starts only when the operator explicitly submits frames.

    def refresh_knowledge(self):
        """Rebuild the small local index from persisted, approved evidence only."""
        from .knowledge_store import list_events

        self.retriever.local_chunks = []
        for event in list_events(review_state="approved"):
            formation = event["formation"]
            if formation and formation.endswith(" Formation"):
                formation = formation.removesuffix(" Formation")
            self.retriever.add_local_chunks([{
                "chunk_id": event["event_id"],
                "well_name": event["well_id"],
                "formation_name": formation,
                "md_top": event["measured_depth_md_m"],
                "md_bottom": None,
                "document_name": event["source_file"],
                "page_number": event["page_marker"],
                "page_reference_type": event["page_reference_type"],
                "review_state": event["review_state"],
                "provenance": event.get("provenance", "synthetic"),
                "text": event["excerpt"],
            }])

    def processor_for(self, well_id: str) -> TelemetryStreamProcessor:
        if well_id not in {well["well_id"] for well in self.wells}:
            raise KeyError(well_id)
        if well_id not in self.stream_processors:
            self.stream_processors[well_id] = TelemetryStreamProcessor(window_size=120)
        return self.stream_processors[well_id]

    @property
    def stream_processor(self) -> TelemetryStreamProcessor:
        """Compatibility for existing single-well callers; never retain a stale reset buffer."""
        return self.processor_for("NHK-421")

    def get_latest_telemetry(self, well_id: str = "NHK-421") -> Dict[str, Any]:
        recent = self.processor_for(well_id).get_recent_history(1)
        return recent[0] if recent else {}

    def ingest_telemetry_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        return self.processor_for(frame["well_id"]).process_frame(frame)

    def evaluate_live_risk(self, well_id: str = "NHK-421") -> Dict[str, Any]:
        window = self.processor_for(well_id).get_recent_history(30)
        if not window:
            return {}

        current_md = window[-1].get("measured_depth", 2845.0)
        interval = next((top for top in source_formations(well_id) or []
                         if top["md_top"] <= current_md < top["md_bottom"]), None)
        formation = interval["formation_name"] if interval else "Unknown formation"

        # ML Prediction
        ml_pred = self.risk_predictor.evaluate_window(window, formation=formation)

        # Physics Validation
        hyd_res = self.hydraulics.calculate_annular_pressure_loss(
            flow_rate_lpm=window[-1].get("flow_in", 2400.0),
            hole_diameter_in=8.5,
            pipe_od_in=5.0,
            tvd_m=2765.0
        )
        ecd_res = self.ecd_calc.calculate_dynamic_ecd(
            static_mud_weight_sg=window[-1].get("mud_weight_in", 1.28),
            annular_pressure_loss_psi=hyd_res["annular_pressure_loss_psi"],
            tvd_m=2765.0
        )

        physics = {
            "hydraulics": hyd_res,
            "ecd": ecd_res
        }

        # Offset evidence retrieval
        self.refresh_knowledge()
        offset_chunks = self.retriever.retrieve(
            query="stuck pipe packoff coal caving",
            formation=formation,
            depth_md=current_md,
            limit=2
        )

        # Multi-domain Risk Fusion
        alert = self.fusion.fuse_risk_assessment(
            well_id=well_id,
            measured_depth=current_md,
            formation=formation,
            ml_prediction=ml_pred,
            physics_validation=physics,
            offset_evidence=offset_chunks
        )

        return alert
