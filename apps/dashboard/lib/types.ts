export interface Well {
  well_id: string;
  well_name: string;
  operator?: string;
  basin?: string;
  field?: string;
  status?: string;
  surface_latitude: number;
  surface_longitude: number;
  elevation_kb_m?: number;
  target_depth_md_m?: number;
  target_formation?: string;
  current_depth_md?: number | null;
  distance_km?: number;
}

export interface TrajectoryStation {
  station_index: number;
  measured_depth: number;
  inclination_deg: number;
  azimuth_deg: number;
  true_vertical_depth: number;
  northing_delta: number;
  easting_delta: number;
  dogleg_severity: number;
  closure_distance: number;
}

export interface FormationTop {
  formation_name: string;
  md_top: number;
  tvd_top: number | null;
  md_bottom?: number | null;
  tvd_bottom?: number | null;
  primary_lithology?: string;
  hazard_warning?: string | null;
  method?: string;
  source_file?: string;
}

export interface HistoricalWatch {
  event_id: string;
  well_id: string;
  event_type: string;
  formation: string;
  measured_depth_md_m: number;
  illustrative_active_md_m: number;
  distance_ahead_md_m: number | null;
  surface_distance_km: number;
  alignment_method: string;
  source_file: string;
  original_name?: string | null;
  page_marker: number | null;
  page_reference_type?: string;
  excerpt: string;
}

export interface TelemetryFrame {
  timestamp: string;
  well_id: string;
  measured_depth: number;
  bit_depth: number;
  rop: number;
  wob: number;
  surface_torque: number;
  rotary_rpm: number;
  standpipe_pressure: number;
  flow_in: number;
  flow_out_pct: number;
  pit_volume: number;
  mud_weight_in: number;
  ecd: number;
  gamma_ray: number;
  gas_total: number;
}

export interface RiskAlert {
  alert_id: string;
  well_id: string;
  timestamp: string;
  measured_depth: number;
  alert_type: string;
  severity: string;
  lead_time_seconds: number;
  lead_time_basis?: string;
  numeric_score_type?: string;
  confidence_score: number;
  ml_probability: number;
  physics_severity: number;
  primary_mechanism: string;
  driller_action_summary: string;
  detailed_sop: string[];
  historical_citations: Record<string, unknown>[];
}

export interface EvidenceRecord {
  chunk_id?: string;
  document_name?: string;
  well_id?: string;
  well_name?: string;
  formation_name?: string;
  md_top?: number;
  md_bottom?: number;
  page_number?: number;
  page_reference_type?: string;
  text?: string;
  score?: number;
}

export interface AssistantResponse {
  answer: string;
  citations: Record<string, unknown>[];
  engine: string;
  evidence_count: number;
}

export interface DocumentRecord { document_name: string; original_name?: string; well_name?: string; type?: string; source_format?: string; status?: string; physical_pdf_available: boolean; document_id?: string }
export interface SourcePage { page_number: number; text: string }
export interface SourceDocument { document_name: string; text: string; physical_pdf_available: boolean; pages: SourcePage[]; provenance?: string }
export interface ReviewEvent { event_id: string; well_id: string; event_type: string; measured_depth_md_m: number | null; formation: string | null; excerpt: string; source_file: string; page_marker: number | null; page_reference_type: string; review_state: 'approved' | 'needs_review' | 'rejected'; mitigation?: string | null; outcome?: string | null }
export interface Decision { decision_id?: string; well_id: string; event_id: string; note: string; actor: string; status: 'acknowledged' | 'monitoring' | 'resolved'; source_snapshot?: Record<string, unknown> }
