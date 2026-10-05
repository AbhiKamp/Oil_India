-- ============================================================================
-- STRATASENTRY-NWIS: RELATIONAL, TIMESERIES & GEOSPATIAL MASTER SCHEMA
-- Target DB: PostgreSQL 16 + TimescaleDB 2.14+ + PostGIS 3.4+
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
-- Note: TimescaleDB extension is loaded when running against TimescaleDB image:
-- CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ----------------------------------------------------------------------------
-- 1. Wells Master Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wells (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_name VARCHAR(100) NOT NULL UNIQUE,
    operator VARCHAR(100) NOT NULL DEFAULT 'Oil India Limited',
    basin VARCHAR(100) NOT NULL DEFAULT 'Assam-Arakan',
    field_name VARCHAR(100) NOT NULL,
    block_name VARCHAR(100),
    surface_latitude DOUBLE PRECISION NOT NULL,
    surface_longitude DOUBLE PRECISION NOT NULL,
    surface_geom GEOMETRY(Point, 4326),
    elevation_kb_meters DOUBLE PRECISION NOT NULL DEFAULT 112.5,
    water_depth_meters DOUBLE PRECISION DEFAULT 0.0,
    spud_date DATE,
    completion_date DATE,
    target_depth_md DOUBLE PRECISION NOT NULL,
    target_formation VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'DRILLING_ACTIVE',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wells_geom ON wells USING GIST (surface_geom);
CREATE INDEX IF NOT EXISTS idx_wells_basin_field ON wells (basin, field_name);

-- ----------------------------------------------------------------------------
-- 2. Wellbores Table (Allows sidetracks and multilateral branches)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wellbores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id UUID NOT NULL REFERENCES wells(id) ON DELETE CASCADE,
    wellbore_name VARCHAR(100) NOT NULL,
    wellbore_type VARCHAR(50) DEFAULT 'ORIGINAL_HOLE', -- ORIGINAL_HOLE, SIDETRACK_1, etc.
    kickoff_depth_md DOUBLE PRECISION DEFAULT 0.0,
    total_depth_md DOUBLE PRECISION NOT NULL,
    total_depth_tvd DOUBLE PRECISION NOT NULL,
    trajectory_geom GEOMETRY(LineStringZ, 4326),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wellbores_traj ON wellbores USING GIST (trajectory_geom);

-- ----------------------------------------------------------------------------
-- 3. Directional Surveys (Minimum Curvature Stations)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS directional_surveys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wellbore_id UUID NOT NULL REFERENCES wellbores(id) ON DELETE CASCADE,
    station_index INT NOT NULL,
    measured_depth DOUBLE PRECISION NOT NULL,
    inclination_deg DOUBLE PRECISION NOT NULL,
    azimuth_deg DOUBLE PRECISION NOT NULL,
    true_vertical_depth DOUBLE PRECISION NOT NULL,
    northing_delta DOUBLE PRECISION NOT NULL,
    easting_delta DOUBLE PRECISION NOT NULL,
    dogleg_severity DOUBLE PRECISION DEFAULT 0.0,
    vertical_section DOUBLE PRECISION DEFAULT 0.0,
    survey_tool VARCHAR(50) DEFAULT 'MWD_CONTINUOUS',
    survey_time TIMESTAMPTZ,
    CONSTRAINT uq_wellbore_survey_station UNIQUE(wellbore_id, measured_depth)
);

CREATE INDEX IF NOT EXISTS idx_surveys_wellbore_md ON directional_surveys (wellbore_id, measured_depth);

-- ----------------------------------------------------------------------------
-- 4. Stratigraphic Formation Tops
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS formation_tops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wellbore_id UUID NOT NULL REFERENCES wellbores(id) ON DELETE CASCADE,
    formation_name VARCHAR(100) NOT NULL,
    md_top DOUBLE PRECISION NOT NULL,
    tvd_top DOUBLE PRECISION NOT NULL,
    md_bottom DOUBLE PRECISION,
    tvd_bottom DOUBLE PRECISION,
    primary_lithology VARCHAR(100) NOT NULL,
    geological_age VARCHAR(100),
    pore_pressure_gradient_sg DOUBLE PRECISION,
    fracture_gradient_sg DOUBLE PRECISION,
    is_prognosed BOOLEAN DEFAULT FALSE,
    comments TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_formations_wellbore ON formation_tops (wellbore_id, md_top);

-- ----------------------------------------------------------------------------
-- 5. Real-Time High-Frequency Drilling Telemetry (Timeseries)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drilling_telemetry (
    time TIMESTAMPTZ NOT NULL,
    wellbore_id UUID NOT NULL,
    measured_depth DOUBLE PRECISION NOT NULL,
    bit_depth DOUBLE PRECISION NOT NULL,
    rop DOUBLE PRECISION,                     -- Rate of Penetration (m/hr)
    wob DOUBLE PRECISION,                     -- Weight on Bit (metric tons)
    surface_torque DOUBLE PRECISION,          -- Surface Torque (kN.m)
    rotary_rpm DOUBLE PRECISION,              -- Rotary Speed (RPM)
    standpipe_pressure DOUBLE PRECISION,      -- Standpipe Pressure (psi)
    pump_spm_total DOUBLE PRECISION,          -- Total Pump Strokes Per Minute
    flow_in DOUBLE PRECISION,                 -- Mud Flow In (L/min)
    flow_out_pct DOUBLE PRECISION,            -- Flow Out Percentage (%)
    pit_volume DOUBLE PRECISION,              -- Active Pit Volume (m^3)
    mud_weight_in DOUBLE PRECISION,           -- Active Mud Density In (SG)
    mud_weight_out DOUBLE PRECISION,          -- Mud Density Out (SG)
    ecd DOUBLE PRECISION,                     -- Dynamic Equivalent Circulating Density (SG)
    gamma_ray DOUBLE PRECISION,               -- LWD/MWD Gamma Ray (API)
    resistivity_deep DOUBLE PRECISION,        -- LWD Deep Resistivity (ohm.m)
    gas_total_units DOUBLE PRECISION,         -- Total Gas Units (units)
    mse DOUBLE PRECISION,                     -- Mechanical Specific Energy (MPa)
    d_exponent DOUBLE PRECISION,              -- Corrected d-exponent
    rig_state VARCHAR(50) DEFAULT 'DRILLING'  -- DRILLING, CONNECTION, TRIPPING, CIRCULATING
);

-- If TimescaleDB is installed, convert to hypertable:
-- SELECT create_hypertable('drilling_telemetry', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_telemetry_well_time ON drilling_telemetry (wellbore_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_well_depth ON drilling_telemetry (wellbore_id, measured_depth DESC);

-- ----------------------------------------------------------------------------
-- 6. Historical & Real-Time Drilling Incidents
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drilling_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wellbore_id UUID NOT NULL REFERENCES wellbores(id) ON DELETE CASCADE,
    incident_type VARCHAR(100) NOT NULL, -- STUCK_PIPE_PACKOFF, STUCK_PIPE_DIFF, GAS_KICK, LOST_CIRCULATION
    depth_md DOUBLE PRECISION NOT NULL,
    depth_tvd DOUBLE PRECISION NOT NULL,
    formation_name VARCHAR(100),
    incident_timestamp TIMESTAMPTZ,
    severity VARCHAR(50) NOT NULL DEFAULT 'HIGH', -- LOW, MEDIUM, HIGH, CRITICAL
    description TEXT NOT NULL,
    root_cause TEXT,
    hours_npt DOUBLE PRECISION DEFAULT 0.0,
    cost_loss_usd DOUBLE PRECISION DEFAULT 0.0,
    mitigation_action TEXT,
    success_status VARCHAR(50) DEFAULT 'RESOLVED', -- RESOLVED, SIDETRACKED, ABANDONED
    source_document VARCHAR(255),
    source_page_ref INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incidents_wellbore ON drilling_incidents (wellbore_id, incident_type);

-- ----------------------------------------------------------------------------
-- 7. Real-Time Risk Alerts & Driller Advisories
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wellbore_id UUID NOT NULL REFERENCES wellbores(id) ON DELETE CASCADE,
    alert_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    measured_depth DOUBLE PRECISION NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL, -- INFO, WATCH, WARNING, CRITICAL
    lead_time_seconds INT DEFAULT 0,
    confidence_score DOUBLE PRECISION NOT NULL,
    ml_probability DOUBLE PRECISION,
    physics_severity DOUBLE PRECISION,
    primary_mechanism TEXT NOT NULL,
    driller_action_summary TEXT NOT NULL,
    detailed_sop JSONB,
    historical_citations JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    driller_feedback VARCHAR(50) -- ACCURATE, FALSE_POSITIVE, MITIGATED
);

CREATE INDEX IF NOT EXISTS idx_alerts_well_time ON risk_alerts (wellbore_id, alert_timestamp DESC);

-- ----------------------------------------------------------------------------
-- 8. Document Intelligence & Knowledge Chunks
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    well_id UUID REFERENCES wells(id),
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- WCR, MUDLOG, DDR, CASING_REPORT
    file_path VARCHAR(512),
    file_hash_sha256 VARCHAR(64) NOT NULL,
    total_pages INT DEFAULT 1,
    extraction_status VARCHAR(50) DEFAULT 'COMPLETED',
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    page_number INT,
    well_name VARCHAR(100),
    formation_name VARCHAR(100),
    md_top DOUBLE PRECISION,
    md_bottom DOUBLE PRECISION,
    chunk_text TEXT NOT NULL,
    vector_id VARCHAR(100), -- ID inside Qdrant collection
    confidence_score DOUBLE PRECISION DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_formation ON document_chunks (formation_name);
