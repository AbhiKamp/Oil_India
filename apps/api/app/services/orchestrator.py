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

from services.well_geometry.trajectory_builder import TrajectoryBuilder
from services.risk_engine.inference.predictor import DrillingRiskPredictor
from services.physics_validation.hydraulics import BinghamPlasticHydraulics
from services.physics_validation.ecd import DynamicECDCalculator
from services.rag_engine.retrieval.qdrant_retriever import QdrantRetriever
from services.rag_engine.llm.mistral_client import MistralDrillingCopilot
from services.risk_fusion.fusion_engine import RiskFusionEngine
from services.telemetry_ingestion.consumers.stream_processor import TelemetryStreamProcessor

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
        self.stream_processor = TelemetryStreamProcessor(window_size=120)

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

        # 3. Pre-seed Knowledge Base with WCR chunks for RAG
        reports_dir = os.path.join(PROJECT_ROOT, 'data', 'synthetic', 'reports')
        if os.path.exists(reports_dir):
            for r_file in os.listdir(reports_dir):
                if r_file.endswith('.txt'):
                    with open(os.path.join(reports_dir, r_file), 'r', encoding='utf-8') as f:
                        txt = f.read()
                    well_name = r_file.replace('WCR_', '').replace('.txt', '')
                    self.retriever.add_local_chunks([
                        {
                            "chunk_id": f"{well_name}_c1",
                            "well_name": well_name,
                            "formation_name": "Barail Coal-Shale" if "MOR" in well_name or "NHK" in well_name else "Tipam Sandstone",
                            "md_top": 2848.0 if "MOR" in well_name else (2912.0 if "NHK" in well_name else 1642.0),
                            "md_bottom": 2865.0,
                            "page_number": 19 if "MOR" in well_name else 24,
                            "text": txt[:1200]
                        }
                    ])

        # 4. Load initial telemetry frame buffer
        telemetry_path = os.path.join(PROJECT_ROOT, 'data', 'synthetic', 'telemetry', 'telemetry_packoff_incident.csv')
        if os.path.exists(telemetry_path):
            df_tel = pd.read_csv(telemetry_path)
            for frame in df_tel.to_dict('records')[:30]:
                self.stream_processor.process_frame(frame)

    def get_latest_telemetry(self) -> Dict[str, Any]:
        recent = self.stream_processor.get_recent_history(1)
        return recent[0] if recent else {}

    def ingest_telemetry_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        return self.stream_processor.process_frame(frame)

    def evaluate_live_risk(self, well_id: str = "NHK-421") -> Dict[str, Any]:
        window = self.stream_processor.get_recent_history(30)
        if not window:
            return {}

        current_md = window[-1].get("measured_depth", 2845.0)
        formation = "Barail Coal-Shale" if current_md > 2550.0 else "Girujan Clay"

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
