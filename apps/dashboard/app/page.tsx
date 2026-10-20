'use client';

import { useEffect, useRef, useState } from 'react';
import {
  documentFileUrl, fetchCurrentRisk, fetchDecisions, fetchDocumentSource, fetchDocuments,
  fetchFormations, fetchHistoricalWatch, fetchLatestTelemetry, fetchNearbyWells,
  fetchReviewEvents, fetchTrajectory, fetchWells, queryAssistant, replayDemo,
  reviewEvent, saveDecision, uploadDocument,
} from '../lib/api';
import type {
  AssistantResponse, Decision, DocumentRecord, FormationTop, HistoricalWatch,
  ReviewEvent, RiskAlert, SourceDocument, TelemetryFrame, TrajectoryStation, Well,
} from '../lib/types';

type View = 'operations' | 'knowledge' | 'handover';
type Scenario = 'normal' | 'packoff' | 'kick';

export default function DashboardPage() {
  const [view, setView] = useState<View>('operations');
  const [wells, setWells] = useState<Well[]>([]);
  const [wellId, setWellId] = useState('');
  const [uploadWellId, setUploadWellId] = useState('');
  const [radius, setRadius] = useState(50);
  const [nearby, setNearby] = useState<Well[]>([]);
  const [selectedWell, setSelectedWell] = useState('');
  const [watches, setWatches] = useState<HistoricalWatch[]>([]);
  const [formations, setFormations] = useState<FormationTop[]>([]);
  const [compareFormations, setCompareFormations] = useState<FormationTop[]>([]);
  const [trajectory, setTrajectory] = useState<TrajectoryStation[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryFrame | null>(null);
  const [risk, setRisk] = useState<RiskAlert | null>(null);
  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [events, setEvents] = useState<ReviewEvent[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [source, setSource] = useState<(SourceDocument & { name: string; page: number | null; textMarker: number | null; referenceType: string }) | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const selectedSourceRef = useRef<HTMLElement>(null);
  const [decisionEventId, setDecisionEventId] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState('Why is this historical event relevant?');
  const [answer, setAnswer] = useState<AssistantResponse | null>(null);
  const [asking, setAsking] = useState(false);
  const requestWell = useRef('');
  const contextGeneration = useRef(0);
  const questionGeneration = useRef(0);
  const [scenario, setScenario] = useState<Scenario>('normal');
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [replayStatus, setReplayStatus] = useState('Step 0 resets the synthetic replay.');
  const replayBusy = useRef(false);
  const replayQueue = useRef<Promise<void>>(Promise.resolve());
  const replayGeneration = useRef(0);

  useEffect(() => {
    fetchWells().then((items) => { setWells(items); setWellId(items[0]?.well_id || ''); setUploadWellId(items[0]?.well_id || ''); })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!wellId) return;
    let stale = false;
    Promise.all([fetchDocuments(), fetchReviewEvents(), fetchDecisions(wellId)])
      .then(([documents, records, log]) => {
        if (!stale) { setDocs(documents); setEvents(records); setDecisions(log); }
      }).catch((e) => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [wellId]);

  useEffect(() => {
    if (!wellId) return;
    let stale = false;
    Promise.all([
      fetchNearbyWells(wellId, radius), fetchHistoricalWatch(wellId, radius),
      fetchFormations(wellId), fetchTrajectory(wellId),
      fetchLatestTelemetry(wellId).catch(() => null), fetchCurrentRisk(wellId).catch(() => null),
    ]).then(([offsets, watch, tops, path, frame, alert]) => {
      if (stale) return;
      setNearby(offsets); setWatches(watch); setFormations(tops); setTrajectory(path);
      setTelemetry(frame); setRisk(alert);
      setSelectedWell((old) => offsets.some((w) => w.well_id === old) ? old : offsets[0]?.well_id || wellId);
    }).catch((e) => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [wellId, radius]);

  useEffect(() => {
    if (!wellId) return;
    let stale = false;
    const poll = async () => {
      try {
        const watch = await fetchHistoricalWatch(wellId, radius);
        if (stale) return;
        setWatches(watch);
        if (step === 0) {
          const [frame, alert] = await Promise.all([fetchLatestTelemetry(wellId).catch(() => null), fetchCurrentRisk(wellId).catch(() => null)]);
          if (!stale) { setTelemetry(frame); setRisk(alert); }
        }
      } catch (e) { if (!stale) setError(e instanceof Error ? e.message : 'Unable to refresh operations data'); }
    };
    const timer = setInterval(poll, 3000);
    return () => { stale = true; clearInterval(timer); };
  }, [wellId, radius, step]);

  useEffect(() => {
    if (!selectedWell || selectedWell === wellId) { setCompareFormations(formations); return; }
    let stale = false;
    fetchFormations(selectedWell).then((tops) => { if (!stale) setCompareFormations(tops); })
      .catch((e) => { if (!stale) setError(e.message); });
    return () => { stale = true; };
  }, [selectedWell, wellId, formations]);

  useEffect(() => {
    if (source) dialog.current?.showModal();
    else if (dialog.current?.open) dialog.current.close();
    if (source?.textMarker != null) requestAnimationFrame(() => selectedSourceRef.current?.scrollIntoView({ block: 'start' }));
  }, [source]);

  useEffect(() => {
    contextGeneration.current++;
    questionGeneration.current++;
    setAsking(false);
    setStep(0); setPlaying(false); setNote(''); setAnswer(null);
    setNearby([]); setWatches([]); setFormations([]); setCompareFormations([]);
    setTrajectory([]); setTelemetry(null); setRisk(null);
    requestWell.current = wellId;
  }, [wellId]);

  useEffect(() => {
    if (!wellId || wellId !== 'NHK-421' || !playing) return;
    const timer = setInterval(() => {
      if (!replayBusy.current) setStep((current) => Math.min(80, current + 1));
    }, 850);
    return () => clearInterval(timer);
  }, [wellId, playing]);

  useEffect(() => {
    if (!wellId) return;
    if (wellId !== 'NHK-421') { setReplayStatus('Replay is available for NHK-421 only.'); return; }
    const generation = ++replayGeneration.current;
    replayBusy.current = true;
    replayQueue.current = replayQueue.current.catch(() => undefined).then(async () => {
      try {
        const result = await replayDemo(scenario, step, wellId);
        if (generation !== replayGeneration.current) return;
        setReplayStatus(`Synthetic replay · ${result.scenario} · step ${result.step}/${result.max_steps}${result.telemetry ? ` · ${result.telemetry.measured_depth.toFixed(1)} m MD` : ''}${result.risk ? ` · ${result.risk.severity} assessment` : ''}`);
        setTelemetry(result.telemetry || null);
        setRisk(result.risk || null);
        if (result.step >= 80) setPlaying(false);
      } catch (e) {
        if (generation === replayGeneration.current) {
          setError(e instanceof Error ? e.message : 'Replay request failed'); setPlaying(false);
        }
      } finally {
        if (generation === replayGeneration.current) replayBusy.current = false;
      }
    });
    return () => { if (generation === replayGeneration.current) replayGeneration.current++; };
  }, [wellId, scenario, step]);

  const active = wells.find((well) => well.well_id === wellId);
  const mapWells = [...(active ? [active] : []), ...nearby.filter((well) => well.well_id !== wellId)];
  const longitudes = mapWells.map((well) => well.surface_longitude);
  const latitudes = mapWells.map((well) => well.surface_latitude);
  const minLongitude = Math.min(...longitudes), maxLongitude = Math.max(...longitudes);
  const minLatitude = Math.min(...latitudes), maxLatitude = Math.max(...latitudes);
  const mapPoint = (well: Well, index: number) => ({
    x: 24 + ((well.surface_longitude - minLongitude) / (maxLongitude - minLongitude || 1)) * 312,
    y: 24 + (1 - (well.surface_latitude - minLatitude) / (maxLatitude - minLatitude || 1)) * 150,
    anchor: (index % 2 ? 'start' : 'end') as 'start' | 'end',
    labelX: index % 2 ? 10 : -10,
    labelY: index % 2 ? 16 : -9,
  });
  const currentDepth = telemetry?.measured_depth ?? active?.current_depth_md ?? null;
  const activeFormation = formations.find((formation) => currentDepth != null && currentDepth >= formation.md_top && (formation.md_bottom == null || currentDepth < formation.md_bottom))?.formation_name;
  const currentFormation = activeFormation;
  const assistantFormation = activeFormation || active?.target_formation || 'Formation not reported';
  const comparisonDepths = [...formations, ...compareFormations].flatMap((formation) =>
    [formation.md_top, ...(formation.md_bottom == null ? [] : [formation.md_bottom])]);
  const depthDomain = {min: Math.min(...comparisonDepths), max: Math.max(...comparisonDepths)};

  async function openSource(name: string, marker: number | null = null, eventId?: string, referenceType = '') {
    try {
      const document = await fetchDocumentSource(name);
      const physicalPage = marker != null && referenceType === 'physical_pdf_page' ? marker : null;
      const textMarker = marker != null && referenceType !== 'physical_pdf_page' ? marker : null;
      setSource({ ...document, name: document.document_name, page: physicalPage, textMarker, referenceType });
      if (eventId) { setDecisionEventId(eventId); setView('handover'); }
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to open source'); }
  }

  async function upload(file?: File) {
    if (!file || !uploadWellId) return;
    setBusy(true); setError('');
    try {
      const uploaded = await uploadDocument(file, uploadWellId);
      setDocs((all) => [uploaded, ...all.filter((doc) => doc.document_name !== uploaded.document_name)]);
      setEvents(await fetchReviewEvents());
    } catch (e) { setError(e instanceof Error ? `Upload or event refresh failed: ${e.message}` : 'Upload or event refresh failed'); }
    finally { setBusy(false); }
  }

  async function decide() {
    if (!decisionEventId || !note.trim()) return;
    const generation = contextGeneration.current;
    setBusy(true);
    try {
      const saved = await saveDecision({ well_id: wellId, event_id: decisionEventId, note: note.trim(), actor: 'Engineer (self-entered)', status: 'acknowledged' });
      if (generation !== contextGeneration.current) return;
      setDecisions((all) => [saved, ...all]); setNote(''); setError('');
    } catch (e) { if (generation === contextGeneration.current) setError(e instanceof Error ? e.message : 'Decision could not be saved'); }
    finally { setBusy(false); }
  }

  async function ask() {
    if (!wellId || !question.trim()) return;
    const targetWell = wellId;
    const generation = ++questionGeneration.current;
    requestWell.current = targetWell; setAsking(true); setAnswer(null);
    try {
      const result = await queryAssistant(question, targetWell, currentDepth ?? 0, assistantFormation);
      if (generation === questionGeneration.current && requestWell.current === targetWell) setAnswer(result);
    } catch (e) {
      if (generation === questionGeneration.current && requestWell.current === targetWell) setError(e instanceof Error ? e.message : 'Evidence search failed');
    } finally { if (generation === questionGeneration.current && requestWell.current === targetWell) setAsking(false); }
  }

  const ahead = watches.filter((watch) => watch.distance_ahead_md_m != null && watch.distance_ahead_md_m >= 0);
  const currentView = view === 'operations' ? 'operations-view' : view === 'knowledge' ? 'knowledge-view' : 'handover-view';
  return <main className="app-shell">
    <header className="topbar">
      <a className="wordmark" href="#main" aria-label="StrataSentry NWIS home"><span className="mark">S</span><span>STRATASENTRY <i>NWIS</i></span></a>
      <div className="demo-state"><span className="status-dot"/> SYNTHETIC DEMONSTRATION <span className="divider">/</span> READ-ONLY DECISION SUPPORT</div>
      <label className="active-selector"><span>ACTIVE WELL</span><select aria-label="Active well" value={wellId} onChange={(event) => setWellId(event.target.value)}>{wells.map((well) => <option key={well.well_id} value={well.well_id}>{well.well_name || well.well_id}</option>)}</select></label>
    </header>
     <div className="intro"><div><p className="eyebrow">NEARBY WELLS INTELLIGENCE SYSTEM · {view.toUpperCase()}</p><h1>{view === 'operations' ? 'Context for the interval ahead.' : view === 'knowledge' ? 'Evidence, connected to its source.' : 'A decision carried to the next shift.'}</h1><p className="subhead">Historical well evidence for engineering review.</p></div><div className="intro-status">{view==='operations'&&<div className="depth-readout"><span>ACTIVE WELL · {telemetry?'REPLAY DEPTH':'DEMO POSITION'}</span><strong>{active?.well_name||wellId||'—'}</strong><b>{currentDepth==null?'Depth unavailable':`${currentDepth.toLocaleString(undefined,{maximumFractionDigits:1})} m`} <small>MD</small></b><em>{currentFormation||active?.target_formation||'Formation not reported'}</em></div>}<span className="data-label">Synthetic demonstration data · not field observations</span></div></div>
    <nav className="view-tabs" role="tablist" aria-label="Dashboard views">{([['operations','Operations'],['knowledge','Knowledge & review'],['handover','Handover']] as const).map(([key,label]) => <button key={key} id={`tab-${key}`} role="tab" aria-selected={view === key} aria-controls={`${key}-view`} tabIndex={view === key ? 0 : -1} data-testid={`tab-${key}`} onClick={() => setView(key)} onKeyDown={(event) => { if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); const next = event.key === 'ArrowRight' ? (key === 'operations' ? 'knowledge' : key === 'knowledge' ? 'handover' : 'operations') : (key === 'operations' ? 'handover' : key === 'knowledge' ? 'operations' : 'knowledge'); setView(next); document.getElementById(`tab-${next}`)?.focus(); } }}>{label}</button>)}</nav>
    {error && <p className="notice" role="alert">{error}</p>}

    {view === 'operations' && <>
      <fieldset className="replay-fieldset" disabled={wellId !== 'NHK-421'}>
        <section className="panel replay-panel" data-testid="demo-replay">
          <span className="eyebrow">SYNTHETIC REPLAY · NOT LIVE eRTMAC DATA</span>
          <label>Scenario <select aria-label="Replay scenario" value={scenario} onChange={(event) => { setPlaying(false); setScenario(event.target.value as Scenario); setStep(0); }}><option value="normal">Normal</option><option value="packoff">Pack-off</option><option value="kick">Kick</option></select></label>
          <button onClick={() => { if (step >= 80) setStep(0); setPlaying((value) => !value); }}>{playing ? 'Pause' : step >= 80 ? 'Replay' : 'Play'}</button>
          <input aria-label="Replay step" type="range" min="0" max="80" value={step} onChange={(event) => { setPlaying(false); setStep(Number(event.target.value)); }}/>
          <span>{step} / 80</span><small aria-live="polite">{replayStatus}</small>
        </section>
      </fieldset>

      <section id="operations-view" role="tabpanel" aria-labelledby="tab-operations" className="ops-restored" data-testid="operations-evidence">
        <article className="panel nearby-panel">
          <div className="panel-heading"><div><p className="eyebrow">SPATIAL CONTEXT</p><h2>Nearby wells</h2></div><span>{nearby.length} OFFSETS · {radius} KM</span></div>
          <label htmlFor="radius-range">Search radius <strong>{radius} km</strong></label>
          <input id="radius-range" aria-label="Search radius in kilometres" type="range" min="5" max="250" step="5" value={radius} onChange={(event) => setRadius(Number(event.target.value))}/>
          <div className="schematic-map real-coordinate-map"><svg viewBox="0 0 360 200" role="img" aria-label="Coordinate schematic based on returned surface coordinates; not a basemap"><title>Coordinate schematic · no basemap</title>
            {mapWells.map((well,index) => { const point=mapPoint(well,index); return <g key={well.well_id} role="button" tabIndex={0} aria-label={`Compare ${well.well_id}${well.well_id===wellId?', active well':`, ${well.distance_km?.toFixed(1)??'unknown'} km away`}`} onClick={()=>setSelectedWell(well.well_id)} onKeyDown={(event)=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();setSelectedWell(well.well_id)}}}><circle cx={point.x} cy={point.y} r={well.well_id===wellId?8:6} className={well.well_id===wellId?'coordinate-active':'coordinate-offset'}/><text x={point.x+point.labelX} y={point.y+point.labelY} textAnchor={point.anchor}>{well.well_id.slice(-7)}</text></g>; })}
          </svg><small>Reported coordinates · schematic projection · no map tiles</small></div>
          <div className="well-list">{nearby.length ? nearby.map((well)=><button className={`well-row ${selectedWell===well.well_id?'is-selected':''}`} key={well.well_id} onClick={()=>setSelectedWell(well.well_id)} aria-pressed={selectedWell===well.well_id}><span className="well-name">{well.well_name||well.well_id}<small>{well.field||'Field not reported'}</small></span><span>{typeof well.distance_km==='number'?`${well.distance_km.toFixed(1)} km`:'Distance unavailable'}</span></button>) : <p className="list-empty">No nearby wells returned for this radius.</p>}</div>
        </article>

        <article className="panel comparison-panel"><div className="panel-heading"><div><p className="eyebrow">GEOLOGICAL CONTEXT</p><h2>Formation comparison</h2></div><span className="method-label">DEPTH INTERVALS · MD</span></div>
          <label>Compare with <select aria-label="Comparison well" value={selectedWell} onChange={(event)=>setSelectedWell(event.target.value)}><option value={wellId}>{wellId} · active</option>{nearby.map((well)=><option key={well.well_id} value={well.well_id}>{well.well_name||well.well_id}</option>)}</select></label>
          <div className="formation-tracks"><Track title={active?.well_name||wellId} items={formations} domain={depthDomain}/><Track title={mapWells.find((well)=>well.well_id===selectedWell)?.well_name||selectedWell} items={compareFormations} domain={depthDomain}/></div>
          <small className="comparison-caveat">Shared formation names are comparison cues, not validated correlation. Active survey: {trajectory.length} stations.</small>
        </article>

        <article className="panel watch-panel"><div className="panel-heading"><div><p className="eyebrow amber">HISTORICAL APPROACH WATCH</p><h2>Comparable intervals ahead</h2></div><span>{ahead.length} AHEAD</span></div>
          {ahead.length ? ahead.map((watch)=><article className="watch-card" key={watch.event_id}><strong>{watch.event_type}</strong><p>{watch.well_id} · {watch.formation} · {watch.distance_ahead_md_m?.toFixed(1)} m MD ahead</p><small>{watch.alignment_method}</small><details><summary>Evidence excerpt · {watch.page_reference_type?.includes('not_verified_pdf_page') ? `text marker ${watch.page_marker ?? 'not provided'} · not a PDF page` : watch.page_marker == null ? 'source marker not provided' : `page ${watch.page_marker}`}</summary><p>{watch.excerpt}</p></details><button className="source-link" onClick={()=>void openSource(watch.source_file,watch.page_marker,watch.event_id,watch.page_reference_type)}>{watch.source_file} · inspect source &amp; prepare handover</button></article>) : <p className="list-empty">No source-backed comparable interval ahead.</p>}
        </article>

        <article className="panel telemetry-panel"><div className="panel-heading"><div><p className="eyebrow">API TELEMETRY SNAPSHOT</p><h2>Measurements &amp; risk</h2></div><span>{telemetry?new Date(telemetry.timestamp).toLocaleTimeString():'NO FRAME RETURNED'}</span></div>
          {telemetry ? <div className="telemetry-values">{[['Bit depth',telemetry.bit_depth,'m MD'],['ROP',telemetry.rop,'m/h'],['Standpipe pressure',telemetry.standpipe_pressure,'psi'],['Surface torque',telemetry.surface_torque,'kN·m'],['Flow out',telemetry.flow_out_pct,'%'],['Gas total',telemetry.gas_total,'gas units']].map(([label,value,unit])=><div key={String(label)}><span>{label}</span><strong>{typeof value==='number'?value.toLocaleString(undefined,{maximumFractionDigits:1}):'—'} {unit}</strong></div>)}</div> : <p className="list-empty">Telemetry unavailable. No placeholder readings shown.</p>}
          {risk ? <div className="risk-card"><p className="eyebrow amber">API RISK ASSESSMENT · {risk.severity}</p><h3>{risk.alert_type}</h3><p>{risk.primary_mechanism}</p><small>{risk.measured_depth.toFixed(1)} m MD · {risk.driller_action_summary}</small><p>Assessment for engineering review; not an instruction or probability claim.</p></div> : <p className="quiet-state">No current risk assessment returned.</p>}
        </article>
      </section>

      <details className="assistant-collapse" data-testid="assistant-evidence"><summary>Ask the reports · local evidence lookup, no language model</summary><section className="panel assistant-panel"><form onSubmit={(event)=>{event.preventDefault();void ask()}}><label htmlFor="assistant-query">Search the active well evidence · {currentDepth == null ? 'depth unavailable' : `${currentDepth.toFixed(1)} m MD`} · {currentFormation ? `formation ${currentFormation}` : `expected target ${assistantFormation}`}</label><div><input id="assistant-query" value={question} onChange={(event)=>setQuestion(event.target.value)}/><button disabled={asking}>{asking?'Searching…':'Search evidence'}</button></div></form>{answer&&<div aria-live="polite"><p>{answer.answer}</p><small>{answer.engine} · {answer.evidence_count} source records</small></div>}</section></details>
    </>}

    {view === 'knowledge' && <section id="knowledge-view" role="tabpanel" aria-labelledby="tab-knowledge" className="workbench" data-testid="documents-workbench">
      <article className="panel workbench-upload"><p className="eyebrow">DOCUMENT LIBRARY · SYNTHETIC PROVENANCE</p><h2>Bring a report into review</h2><p>Uploaded report provenance is explicitly marked synthetic.</p><label htmlFor="upload-well">Report well</label><select id="upload-well" aria-label="Report well" value={uploadWellId} onChange={(event)=>setUploadWellId(event.target.value)}>{wells.map((well)=><option key={well.well_id} value={well.well_id}>{well.well_name||well.well_id}</option>)}</select><label className="upload-control">Choose PDF<input aria-label="Upload synthetic PDF" type="file" accept="application/pdf,.pdf" disabled={busy} onChange={(event)=>void upload(event.target.files?.[0])}/></label>{busy&&<p role="status">Uploading and refreshing event records…</p>}</article>
      <article className="panel"><div className="panel-heading"><h2>Documents</h2><span>{docs.length} RECORDS</span></div>{docs.length?docs.map((doc)=><div className="document-row" key={doc.document_id||doc.document_name}><div><strong>{doc.original_name||doc.document_name}</strong><small>{doc.well_name||'Well not reported'} · {doc.type||doc.source_format||'type not reported'} · {doc.status||'status not reported'}</small></div><div>{doc.physical_pdf_available&&<a href={documentFileUrl(doc.document_name)} target="_blank" rel="noreferrer">Open PDF</a>} <button onClick={()=>void openSource(doc.document_name)}>Inspect</button></div></div>):<p className="list-empty">No documents returned.</p>}</article>
      <article className="panel"><div className="panel-heading"><h2>Event review</h2><span>{events.length} EVENTS</span></div>{events.length?events.map((event)=><ReviewCard key={event.event_id} event={event} onReview={async(state)=>{await reviewEvent(event.event_id,state,'Engineer');setEvents((all)=>all.map((item)=>item.event_id===event.event_id?{...item,review_state:state}:item))}} onSource={()=>void openSource(event.source_file,event.page_marker,event.event_id,event.page_reference_type)} onError={setError}/>):<p className="list-empty">No events returned.</p>}</article>
    </section>}

    {view === 'handover' && <section id="handover-view" role="tabpanel" aria-labelledby="tab-handover" className="workbench" data-testid="handover-workbench"><article className="panel"><p className="eyebrow">ENGINEER-RECORDED · SELF-ENTERED ACTOR</p><h2>Shift decision</h2><p>Decision target: active well <strong>{wellId||'—'}</strong>. Source event may belong to a historical offset well.</p><label htmlFor="decision-event">Historical source event</label><select id="decision-event" value={decisionEventId} onChange={(event)=>setDecisionEventId(event.target.value)}><option value="">Choose a reviewed event</option>{events.filter((event)=>event.review_state!=='rejected').map((event)=><option key={event.event_id} value={event.event_id}>{event.well_id} · {event.event_type} · {event.formation||'formation unknown'}</option>)}</select><label htmlFor="decision-note">Decision note</label><textarea id="decision-note" value={note} onChange={(event)=>setNote(event.target.value)} placeholder="Record evidence reviewed and context for the next shift"/><button disabled={!note.trim()||!decisionEventId||busy} onClick={()=>void decide()}>Save acknowledged decision</button></article><article className="panel"><div className="panel-heading"><h2>Handover log</h2><span>{decisions.length} ENTRIES</span></div>{decisions.length?decisions.map((decision,index)=><div className="decision-entry" key={decision.decision_id||index}><strong>{decision.status}</strong><p>{decision.note}</p><small>{decision.actor} · source event {decision.event_id}</small></div>):<p className="list-empty">No decisions recorded.</p>}</article></section>}

    <dialog className="source-dialog" ref={dialog} aria-label={source?`Source ${source.name}`:'Source viewer'} onCancel={()=>setSource(null)}><section className="source-sheet"><div className="panel-heading"><div><p className="eyebrow">{source?.physical_pdf_available?'SOURCE PDF AVAILABLE':'TEXT SOURCE · PDF UNAVAILABLE'}{source?.page?` · PHYSICAL PDF PAGE ${source.page}`:source?.textMarker!=null?` · TEXT MARKER ${source.textMarker} · NOT A PDF PAGE`:' · NO VERIFIED PDF PAGE REFERENCE'} · {source?.provenance||'PROVENANCE NOT REPORTED'}</p><h2>{source?.name}</h2></div><button onClick={()=>setSource(null)}>Close</button></div>{source?.physical_pdf_available&&<iframe title={`PDF source ${source.name}`} src={`${documentFileUrl(source.name)}${source.page?`#page=${source.page}`:''}`}/>}<div className="source-pages">{source?.pages?.length?source.pages.map((page)=>{const isTextMarker=source.textMarker===page.page_number;return <article key={page.page_number} ref={isTextMarker?selectedSourceRef:null} className={isTextMarker?'source-cited':''}><h3>{source.referenceType==='physical_pdf_page'?`PDF page ${page.page_number}`:isTextMarker?`Text marker ${page.page_number}`:`Text section ${page.page_number}`}{isTextMarker?' · cited evidence':''}</h3><pre>{page.text}</pre></article>}):<pre ref={selectedSourceRef as React.RefObject<HTMLPreElement>} className={source?.textMarker!=null?'source-cited':''}>{source?.text}</pre>}</div></section></dialog>
    <footer className="footer"><span>STRATASENTRY NWIS · READ-ONLY DECISION SUPPORT</span><span>SYNTHETIC DEMONSTRATION · NOT FIELD DATA</span></footer>
  </main>;
}

function Track({title,items,domain}:{title:string;items:FormationTop[];domain:{min:number;max:number}}) {
  const {min,max}=domain;
  return <div className="formation-track"><h3>{title}</h3>{items.length? <div className="formation-depths" aria-label={`${title} formation depth intervals`}>
    <div className="depth-axis"><span>{min.toLocaleString()} m</span><span>{max.toLocaleString()} m MD</span></div>
    <div className="depth-bands">{items.map((formation,index)=>{const bottom=formation.md_bottom??formation.md_top;const topPct=max===min?0:((formation.md_top-min)/(max-min))*100;const height=max===min?0:Math.max(0,((bottom-formation.md_top)/(max-min))*100);return <div className="depth-band" key={`${formation.formation_name}-${index}`} style={{top:`${topPct}%`,height:`${height}%`}} title={`${formation.formation_name}: ${formation.md_top}–${formation.md_bottom??'not reported'} m MD`}><strong>{formation.formation_name}</strong><span>{formation.md_top.toLocaleString()} m MD{formation.md_bottom==null?'':` – ${formation.md_bottom.toLocaleString()}`}</span></div>;})}</div>
    <div className="formation-row"><small>{items[0].method||'Method not reported'}{items[0].source_file?` · ${items[0].source_file}`:''}</small></div>
  </div>:<p className="list-empty">Formation records unavailable.</p>}</div>;
}

function ReviewCard({event,onReview,onSource,onError}:{event:ReviewEvent;onReview:(state:ReviewEvent['review_state'])=>Promise<void>;onSource:()=>void;onError:(error:string)=>void}) {
  async function update(state:ReviewEvent['review_state']) { try { await onReview(state); } catch (error) { onError(error instanceof Error?error.message:'Event review failed'); } }
  return <article className="review-event"><div><strong>{event.event_type}</strong><small>{event.well_id} · {event.formation||'Formation unknown'} · {event.measured_depth_md_m==null?'Depth unknown':`${event.measured_depth_md_m} m MD`} · {event.source_file}{event.page_marker==null?'':` · ${event.page_reference_type} ${event.page_marker}`}</small><details><summary>Source excerpt</summary><p>{event.excerpt}</p></details><button onClick={onSource}>Open cited source</button></div><span className={`review-state ${event.review_state}`}>{event.review_state.replace('_',' ')}</span>{event.review_state==='needs_review'&&<div className="review-actions"><button onClick={()=>void update('approved')}>Approve</button><button onClick={()=>void update('rejected')}>Reject</button></div>}</article>;
}
