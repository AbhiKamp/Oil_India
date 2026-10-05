-- PostGIS Spatial Indexes & Functions for Wellbore Trajectory Proximity Queries

-- Ensure 3D spatial index on wellbore linestrings
CREATE INDEX IF NOT EXISTS idx_wellbores_traj_3d ON wellbores USING GIST (trajectory_geom);

-- Function to find nearest offset wellbores within a given radius (meters)
CREATE OR REPLACE FUNCTION get_offset_wellbores_within_radius(
    p_well_id UUID,
    p_radius_meters DOUBLE PRECISION
)
RETURNS TABLE (
    offset_well_id UUID,
    offset_well_name VARCHAR,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w2.id,
        w2.well_name,
        ST_Distance(w1.surface_geom::geography, w2.surface_geom::geography) AS distance_meters
    FROM wells w1
    CROSS JOIN wells w2
    WHERE w1.id = p_well_id
      AND w2.id != p_well_id
      AND ST_DWithin(w1.surface_geom::geography, w2.surface_geom::geography, p_radius_meters)
    ORDER BY distance_meters ASC;
END;
$$ LANGUAGE plpgsql;
