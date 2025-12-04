-- ============================================
-- OIL PRODUCTION DATABASE - FULL SQL SCRIPT
-- Database: Oil Production Management System
-- Version: 1.0
-- ============================================


-- ============================================
-- TABLE 1: SITES (Oil Fields / Locations)
-- ============================================
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    description TEXT
);

INSERT INTO sites (name, location, description) VALUES
('Permian Basin', 'Texas, USA', 'Largest US oilfield with extensive operations'),
('Marcellus Shale', 'Pennsylvania, USA', 'Major gas-producing shale formation'),
('Kern River', 'California, USA', 'Historical oilfield, mature production'),
('Eagle Ford Shale', 'Texas, USA', 'Major shale play with high production'),
('Bakken Formation', 'North Dakota, USA', 'Tight oil formation, significant reserves'),
('Niobrara Shale', 'Colorado, USA', 'Emerging shale play with growth potential'),
('Haynesville Shale', 'Louisiana, USA', 'Gas-rich shale formation'),
('Vaca Muerta', 'Argentina', 'Second largest shale reserves globally'),
('Troll Field', 'North Sea, Norway', 'Major offshore field'),
('Ghawar Field', 'Saudi Arabia', 'World''s largest conventional oil field'),
('Safaniyah Field', 'Saudi Arabia', 'Largest offshore oilfield'),
('Kashagan', 'Caspian Sea, Kazakhstan', 'Major offshore discovery');

-- ============================================
-- TABLE 2: WELLS
-- ============================================
CREATE TABLE IF NOT EXISTS wells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER,
    name TEXT,
    depth REAL,
    status TEXT,
    FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE
);

INSERT INTO wells (site_id, name, depth, status) VALUES
(1, 'API-42131456780001', 9800.5, 'Active'),
(1, 'API-42131456780002', 10120.0, 'Inactive'),
(1, 'API-42131456780003', 8950.25, 'Active'),
(1, 'API-42131456780004', 11200.0, 'Maintenance'),
(2, 'API-37100123450001', 8900.75, 'Active'),
(2, 'API-37100123450002', 9100.0, 'Active'),
(3, 'API-06007123450001', 6500.0, 'Active'),
(3, 'API-06007123450002', 6750.5, 'Inactive'),
(4, 'API-48205987650001', 12300.0, 'Active'),
(4, 'API-48205987650002', 11800.75, 'Active'),
(5, 'API-33025456780001', 10500.0, 'Active'),
(5, 'API-33025456780002', 10800.25, 'Maintenance'),
(6, 'API-08001234567001', 7800.0, 'Active'),
(7, 'API-22015789012001', 9200.5, 'Active'),
(9, 'API-TROLL-001', 1680.0, 'Active'),
(10, 'API-GHAWAR-001', 14000.0, 'Active');

-- ============================================
-- TABLE 3: TEAMS
-- ============================================
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT
);

INSERT INTO teams (name, contact) VALUES
('Alpha Operations', 'ops.alpha@oilco.com'),
('Well Servicing East', 'service.east@oilco.com'),
('West Drillers', 'west.dril@oilco.com'),
('Delta Maintenance', 'maint.delta@oilco.com'),
('Echo Intervention Team', 'interv.echo@oilco.com'),
('Foxtrot Production', 'prod.foxtrot@oilco.com'),
('Golf Offshore Services', 'offshore.golf@oilco.com'),
('Hotel Wireline Services', 'wireline.hotel@oilco.com'),
('India Safety Response', 'safety.india@oilco.com'),
('Juliet Completion Team', 'completion.juliet@oilco.com'),
('Kilo Emergency Response', 'emergency.kilo@oilco.com'),
('Lima Technical Support', 'tech.lima@oilco.com');

-- ============================================
-- TABLE 4: INTERVENTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id INTEGER,
    team_id INTEGER,
    start_time TEXT,
    end_time TEXT,
    operation TEXT,
    notes TEXT,
    FOREIGN KEY(well_id) REFERENCES wells(id) ON DELETE CASCADE,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
);

INSERT INTO interventions (well_id, team_id, start_time, end_time, operation, notes) VALUES
(1, 1, '2025-04-01 07:30', '2025-04-01 09:30', 'Wireline Logging', 'Routine operation, no issues observed.'),
(2, 2, '2025-05-15 08:00', '2025-05-15 13:00', 'Snubbing Operation', 'High pressure snubbing, Class 2, success.'),
(1, 3, '2025-04-20 06:00', '2025-04-20 06:45', 'Workover', 'Minor maintenance, resolved valve issue.'),
(3, 4, '2025-03-10 10:00', '2025-03-10 16:00', 'Well Stimulation', 'Acid treatment completed successfully.'),
(5, 5, '2025-02-28 09:15', '2025-02-28 12:30', 'Tubing Replacement', 'Full tubing run, no complications.'),
(6, 6, '2025-06-05 07:00', '2025-06-05 14:00', 'Production Optimization', 'Choke adjustment and flow optimization.'),
(4, 7, '2025-01-15 08:30', '2025-01-15 11:00', 'Safety Inspection', 'BOP inspection and pressure test.'),
(7, 8, '2025-05-22 06:00', '2025-05-22 18:00', 'Well Logging', 'Comprehensive logging suite completed.'),
(8, 9, '2025-03-05 12:00', '2025-03-05 14:00', 'Emergency Response', 'Pressure relief valve replacement.'),
(9, 10, '2025-04-10 08:00', '2025-04-10 20:00', 'Well Completion', 'Perforations and screen installation.'),
(10, 11, '2025-02-14 09:00', '2025-02-14 17:00', 'Downhole Tools Repair', 'Tool retrieval and maintenance.'),
(11, 12, '2025-06-20 07:30', '2025-06-20 10:15', 'Pressure Test', 'Formation integrity test passed.'),
(12, 1, '2025-05-01 08:00', '2025-05-01 12:00', 'Sand Control', 'Screen installation and testing.'),
(3, 2, '2025-04-25 09:30', '2025-04-25 11:45', 'Flow Line Check', 'Pipeline inspection completed.'),
(5, 3, '2025-06-10 10:00', '2025-06-10 15:30', 'Corrosion Monitoring', 'Corrosion probe installed and baseline set.');

-- ============================================
-- TABLE 5: PRODUCTION
-- ============================================
CREATE TABLE IF NOT EXISTS production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id INTEGER,
    timestamp TEXT,
    flow_rate REAL,
    pressure REAL,
    temperature REAL,
    quantity_produced REAL,
    FOREIGN KEY(well_id) REFERENCES wells(id) ON DELETE CASCADE
);

INSERT INTO production (well_id, timestamp, flow_rate, pressure, temperature, quantity_produced) VALUES
(1, '2025-01-01', 350.5, 2400, 88.5, 120.0),
(1, '2025-02-01', 355.0, 2490, 91.2, 123.5),
(1, '2025-03-01', 348.25, 2380, 87.8, 118.5),
(1, '2025-04-01', 360.75, 2510, 92.1, 125.2),
(1, '2025-05-01', 365.0, 2550, 93.5, 128.0),
(1, '2025-06-01', 358.5, 2420, 90.2, 122.5),
(2, '2025-01-01', 290.0, 2350, 82.0, 100.0),
(2, '2025-02-01', 295.5, 2390, 84.5, 105.5),
(2, '2025-03-01', 285.75, 2310, 80.8, 98.0),
(2, '2025-04-01', 298.0, 2420, 86.2, 108.0),
(2, '2025-05-01', 302.5, 2450, 87.9, 110.5),
(2, '2025-06-01', 288.0, 2360, 81.5, 102.0),
(3, '2025-01-01', 420.0, 2800, 95.0, 145.0),
(3, '2025-02-01', 425.5, 2850, 97.2, 148.5),
(3, '2025-03-01', 415.25, 2780, 94.1, 142.0),
(3, '2025-04-01', 430.0, 2900, 98.5, 152.0),
(4, '2025-01-01', 275.0, 2200, 78.5, 95.0),
(4, '2025-02-01', 278.5, 2240, 80.0, 97.5),
(5, '2025-01-01', 385.0, 2650, 89.5, 132.0),
(6, '2025-01-01', 320.0, 2550, 91.0, 110.0),
(6, '2025-02-01', 325.5, 2600, 92.5, 114.0),
(7, '2025-01-01', 410.0, 2750, 94.0, 140.0),
(9, '2025-01-01', 750.0, 3200, 105.0, 250.0),
(10, '2025-01-01', 1200.0, 3500, 110.0, 380.0),
(11, '2025-01-01', 550.0, 3000, 100.5, 185.0);

-- ============================================
-- TABLE 6: INCIDENTS
-- ============================================
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id INTEGER,
    incident_type TEXT,
    severity TEXT,
    date TEXT,
    description TEXT,
    resolved INTEGER DEFAULT 0,
    FOREIGN KEY(well_id) REFERENCES wells(id) ON DELETE CASCADE
);

INSERT INTO incidents (well_id, incident_type, severity, date, description, resolved) VALUES
(1, 'Blowout', 'High', '2024-12-21', 'Pressurization exceeded control threshold. Contained, no injuries.', 1),
(2, 'Leak', 'Medium', '2024-11-12', 'Detected small tubing leak, repaired during workover.', 1),
(1, 'Valve Failure', 'Low', '2025-01-18', 'Valve replacement required due to slow response.', 1),
(3, 'Equipment Failure', 'Medium', '2025-02-05', 'Pump failure, replaced with backup unit.', 1),
(4, 'Pressure Spike', 'High', '2025-03-12', 'Unexpected pressure surge, safety vented, investigated.', 1),
(5, 'Corrosion Issue', 'Medium', '2025-01-25', 'Tubing corrosion detected, inhibitor treatment applied.', 1),
(6, 'Gas Leak', 'Low', '2025-02-14', 'Minor gas release at surface, sealed with patch.', 1),
(7, 'Fire Incident', 'High', '2024-10-08', 'Small fire at wellhead, extinguished, investigation ongoing.', 1),
(8, 'Production Loss', 'Medium', '2025-04-03', 'Unexpected production drop, choke adjusted.', 1),
(9, 'Temperature Anomaly', 'Low', '2025-03-20', 'Abnormal temperature reading, sensor calibrated.', 1),
(10, 'Sand Production', 'Medium', '2025-05-10', 'Sand entry detected, screen installed to prevent further production.', 1),
(11, 'Plug Failure', 'High', '2025-06-01', 'Cement plug failed, re-plugging initiated.', 0),
(12, 'Fluid Loss', 'Medium', '2025-05-15', 'Lost circulation during drilling, addressed with lost circulation material.', 1),
(3, 'Fatigue Crack', 'Medium', '2025-04-22', 'Minor crack in casing detected via imaging, monitoring ongoing.', 0),
(1, 'Scale Buildup', 'Low', '2025-06-05', 'Mineral scale buildup reduced flow, chemical treatment applied.', 1);

-- ============================================
-- SUMMARY OF DATA
-- ============================================
-- Sites: 12 records
-- Wells: 16 records
-- Teams: 12 records
-- Interventions: 15 records
-- Production: 25 records
-- Incidents: 15 records
-- ============================================
-- END OF SQL SCRIPT
-- ============================================