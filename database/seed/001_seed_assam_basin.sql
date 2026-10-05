-- ============================================================================
-- SEED DATA: UPPER ASSAM BASIN OIL WELLS & STRATIGRAPHY
-- ============================================================================

INSERT INTO wells (id, well_name, operator, basin, field_name, surface_latitude, surface_longitude, elevation_kb_meters, spud_date, target_depth_md, target_formation, status)
VALUES 
('11111111-1111-1111-1111-111111111111', 'NHK-421', 'Oil India Limited', 'Assam-Arakan', 'Naharkatiya', 27.2842, 95.3418, 115.0, '2026-09-12', 3950.0, 'Barail Coal-Shale', 'DRILLING_ACTIVE'),
('22222222-2222-2222-2222-222222222222', 'NHK-412', 'Oil India Limited', 'Assam-Arakan', 'Naharkatiya', 27.2890, 95.3452, 114.2, '2024-03-10', 3820.0, 'Barail Coal-Shale', 'COMPLETED'),
('33333333-3333-3333-3333-333333333333', 'MOR-118', 'Oil India Limited', 'Assam-Arakan', 'Moran', 27.1820, 94.9215, 108.5, '2023-08-15', 4100.0, 'Barail Main Sand', 'COMPLETED'),
('44444444-4444-4444-4444-444444444444', 'BGH-07', 'Oil India Limited', 'Assam-Arakan', 'Baghjan', 27.5921, 95.3854, 122.0, '2020-05-20', 3920.0, 'Tipam / Barail', 'SHUT_IN')
ON CONFLICT (well_name) DO NOTHING;

-- Wellbores
INSERT INTO wellbores (id, well_id, wellbore_name, kickoff_depth_md, total_depth_md, total_depth_tvd, status)
VALUES
('a1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'NHK-421-OH', 0.0, 3950.0, 3720.0, 'ACTIVE'),
('a2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'NHK-412-OH', 0.0, 3820.0, 3650.0, 'COMPLETED'),
('a3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 'MOR-118-OH', 0.0, 4100.0, 3890.0, 'COMPLETED')
ON CONFLICT DO NOTHING;

-- Stratigraphic Formation Tops for NHK-421
INSERT INTO formation_tops (wellbore_id, formation_name, md_top, tvd_top, md_bottom, tvd_bottom, primary_lithology, geological_age, comments)
VALUES
('a1111111-1111-1111-1111-111111111111', 'Dihing Formation', 0.0, 0.0, 650.0, 650.0, 'Pebbly sandstone and loose silts', 'Pleistocene', 'Surface casing interval'),
('a1111111-1111-1111-1111-111111111111', 'Tipam Sandstone', 650.0, 650.0, 1850.0, 1820.0, 'Fluvial sandstone, massive', 'Miocene', 'High differential sticking potential'),
('a1111111-1111-1111-1111-111111111111', 'Girujan Clay', 1850.0, 1820.0, 2550.0, 2480.0, 'Plastic swelling shale and clay', 'Miocene', 'Swelling shale, tight hole'),
('a1111111-1111-1111-1111-111111111111', 'Barail Coal-Shale', 2550.0, 2480.0, 3400.0, 3260.0, 'Intercalated sandstones, coals, splintery shales', 'Oligocene', 'High risk of pack-off and gas kicks'),
('a1111111-1111-1111-1111-111111111111', 'Kopili Formation', 3400.0, 3260.0, 3950.0, 3720.0, 'Splintery calcareous shales, overpressured', 'Eocene', 'Severe wellbore instability')
ON CONFLICT DO NOTHING;

-- Historical Drilling Incidents in Offset Wells
INSERT INTO drilling_incidents (wellbore_id, incident_type, depth_md, depth_tvd, formation_name, severity, description, root_cause, hours_npt, cost_loss_usd, mitigation_action, source_document, source_page_ref)
VALUES
('a3333333-3333-3333-3333-333333333333', 'STUCK_PIPE_PACKOFF', 2848.0, 2724.0, 'Barail Coal-Shale', 'CRITICAL', 
 'Mechanical hole pack-off during drillpipe connection. Complete loss of rotation and circulation pressure spiked from 2,800 to 3,600 psi.',
 'Sloughing coal caving into annulus due to insufficient mud circulation time prior to pipe connection.',
 36.5, 420000.0, 
 'Spotted 45 bbls high-viscosity pill, backed off string at safety joint, engaged bumper sub and jarred up at 90 klbs. Pipe freed after 14 hours jarring.',
 'WCR_MOR_118.pdf', 19),

('a2222222-2222-2222-2222-222222222222', 'GAS_KICK', 2912.0, 2780.0, 'Barail Coal-Shale', 'HIGH',
 'Sudden 18 bbl pit volume gain with flow-out increase to 88% while drilling sandstone stringer in Barail series.',
 'Underbalanced drilling into unexpected high-pressure coal-bed gas pocket.',
 18.0, 185000.0,
 'Shut in well with annular BOP. Recorded SIDPP = 320 psi, SICP = 410 psi. Circulated out kick using Driller Method with 1.34 SG kill mud.',
 'WCR_NHK_412.pdf', 24)
ON CONFLICT DO NOTHING;
