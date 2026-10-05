-- TimescaleDB Hypertable conversion and retention policy configuration
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Convert high-frequency telemetry to TimescaleDB hypertable partitioned by time
SELECT create_hypertable('drilling_telemetry', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

-- Compression policy for telemetry older than 7 days
ALTER TABLE drilling_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'wellbore_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('drilling_telemetry', INTERVAL '7 days', if_not_exists => TRUE);
