-- Migration 001: Initial Schema Setup
-- Replicates database/schema.sql for tracked database versioning
\i /docker-entrypoint-initdb.d/01_schema.sql
