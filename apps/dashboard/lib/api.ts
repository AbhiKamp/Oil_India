import type { AssistantResponse, Decision, DocumentRecord, EvidenceRecord, FormationTop, HistoricalWatch, ReviewEvent, RiskAlert, SourceDocument, TelemetryFrame, TrajectoryStation, Well } from './types';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: init?.body instanceof FormData ? init.headers : { 'Content-Type': 'application/json', ...init?.headers },
    cache: 'no-store',
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const fetchWells = () => request<Well[]>('/wells');
export const fetchNearbyWells = (id: string, radiusKm: number) =>
  request<Well[]>(`/wells/${encodeURIComponent(id)}/nearby?radius_km=${radiusKm}`);
export const fetchHistoricalWatch = (id: string, radiusKm: number) =>
  request<HistoricalWatch[]>(`/wells/${encodeURIComponent(id)}/historical-watch?radius_km=${radiusKm}`);
export const fetchDocumentSource = (name: string) =>
  request<SourceDocument>(`/documents/${encodeURIComponent(name)}/source`);
export const fetchDocuments = () => request<DocumentRecord[]>('/documents');
export const uploadDocument = (file: File, wellId: string) => { const form = new FormData(); form.append('file', file); form.append('well_id', wellId); form.append('provenance', 'synthetic'); return request<DocumentRecord>('/documents', { method: 'POST', body: form }); };
export const fetchReviewEvents = (wellId?: string) => request<ReviewEvent[]>(`/events${wellId ? `?well_id=${encodeURIComponent(wellId)}` : ''}`);
export const reviewEvent = (id: string, review_state: ReviewEvent['review_state'], reviewer: string) => request<ReviewEvent>(`/events/${encodeURIComponent(id)}/review`, { method: 'PATCH', body: JSON.stringify({ review_state, reviewer }) });
export const fetchDecisions = (wellId: string) => request<Decision[]>(`/decisions?well_id=${encodeURIComponent(wellId)}`);
export const saveDecision = (decision: Decision) => request<Decision>('/decisions', { method: 'POST', body: JSON.stringify(decision) });
export const replayDemo = (scenario: 'normal' | 'packoff' | 'kick', step: number, wellId: string) => request<{ scenario: string; step: number; max_steps: number; telemetry?: TelemetryFrame; risk?: RiskAlert }>('/demo/replay', { method: 'POST', body: JSON.stringify({ scenario, step, well_id: wellId }) });
export const documentFileUrl = (name: string) => `${API_BASE}/api/v1/documents/${encodeURIComponent(name)}/file`;
export const fetchTrajectory = (id: string) => request<TrajectoryStation[]>(`/wells/${encodeURIComponent(id)}/trajectory`);
export const fetchFormations = (id: string) => request<FormationTop[]>(`/wells/${encodeURIComponent(id)}/formations`);
export const fetchLatestTelemetry = (id: string) => request<TelemetryFrame>(`/telemetry/${encodeURIComponent(id)}/latest`);
export const fetchCurrentRisk = (id: string) => request<RiskAlert>(`/risks/${encodeURIComponent(id)}/current`);
export const fetchEvidence = (id: string, depth: number) =>
  request<EvidenceRecord[]>(`/documents/evidence?well_id=${encodeURIComponent(id)}&depth=${encodeURIComponent(String(depth))}`);
export const queryAssistant = (query: string, wellId: string, depth: number, formation: string) =>
  request<AssistantResponse>('/assistant/chat', {
    method: 'POST',
    body: JSON.stringify({ query, well_id: wellId, current_depth: depth, formation }),
  });
