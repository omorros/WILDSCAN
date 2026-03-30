-- Seed: ~15 trafficking route LineStrings
-- Coordinates use representative city/port centroids.
-- Key hubs:
--   Nairobi, Kenya          :  36.8219,  -1.2921
--   Dar es Salaam, Tanzania :  39.2083,  -6.7924
--   Lagos, Nigeria          :   3.3792,   6.4550
--   Yaoundé, Cameroon       :  11.5174,   3.8480
--   Dubai, UAE              :  55.2708,  25.2048
--   Singapore               : 103.8198,   1.3521
--   Bangkok, Thailand       : 100.5018,  13.7563
--   Ho Chi Minh City        : 106.6602,  10.8189
--   Hanoi, Vietnam          : 105.8342,  21.0278
--   Guangzhou, China        : 113.2644,  23.1291
--   Shanghai, China         : 121.4737,  31.2304
--   Jakarta, Indonesia      : 106.8456,  -6.2088
--   Kuala Lumpur, Malaysia  : 101.6869,   3.1390
--   Yangon, Myanmar         :  96.1561,  16.8661
--   Vientiane, Laos         : 102.6331,  17.9757
--   Phnom Penh, Cambodia    : 104.9282,  11.5564
--   Johannesburg, S. Africa :  28.0473, -26.2041

INSERT INTO trafficking_routes
    (species_group, origin_region, destination_region, route_geometry,
     activity_level, evidence_sources)
VALUES

-- ── IVORY (4 routes) ─────────────────────────────────────────────────────────

-- East Africa → Vietnam via Dubai
('ivory', 'East Africa', 'Vietnam',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(36.8219,  -1.2921),   -- Nairobi
         ST_MakePoint(55.2708,  25.2048),   -- Dubai (transit)
         ST_MakePoint(106.6602, 10.8189)    -- Ho Chi Minh City
     ]
 ), 4326),
 'high',
 ARRAY['UNODC WWCR 2024', 'TRAFFIC 2024', 'CITES CoP19 doc']),

-- East Africa → China via Southeast Asia
('ivory', 'East Africa', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(39.2083,  -6.7924),   -- Dar es Salaam
         ST_MakePoint(103.8198,  1.3521),   -- Singapore (transit)
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'high',
 ARRAY['UNODC WWCR 2024', 'WCO Enforcement 2024']),

-- West Africa → Thailand
('ivory', 'West Africa', 'Thailand',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(3.3792,    6.4550),   -- Lagos
         ST_MakePoint(55.2708,  25.2048),   -- Dubai (transit)
         ST_MakePoint(100.5018, 13.7563)    -- Bangkok
     ]
 ), 4326),
 'medium',
 ARRAY['INTERPOL Operation Thunder 2024', 'TRAFFIC 2023']),

-- Southern Africa → China via Mozambique/Vietnam
('ivory', 'Southern Africa', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(28.0473, -26.2041),   -- Johannesburg
         ST_MakePoint(35.3375, -17.9178),   -- Mozambique port (Nacala)
         ST_MakePoint(106.6602, 10.8189),   -- Ho Chi Minh City
         ST_MakePoint(121.4737, 31.2304)    -- Shanghai
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC 2024', 'CITES Trade DB 2023']),

-- ── PANGOLIN (3 routes) ──────────────────────────────────────────────────────

-- Central Africa → Vietnam
('pangolin', 'Central Africa', 'Vietnam',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(11.5174,   3.8480),   -- Yaoundé
         ST_MakePoint(55.2708,  25.2048),   -- Dubai (transit)
         ST_MakePoint(105.8342, 21.0278)    -- Hanoi
     ]
 ), 4326),
 'high',
 ARRAY['UNODC WWCR 2024', 'WCO 2024', 'TRAFFIC Pangolin Report 2023']),

-- Indonesia → China via Malaysia
('pangolin', 'Southeast Asia (Indonesia)', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(106.8456,  -6.2088),  -- Jakarta
         ST_MakePoint(101.6869,   3.1390),  -- Kuala Lumpur
         ST_MakePoint(113.2644,  23.1291)   -- Guangzhou
     ]
 ), 4326),
 'high',
 ARRAY['INTERPOL Thunderball 2024', 'TRAFFIC 2024']),

-- Myanmar → China overland via Thailand
('pangolin', 'Myanmar', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(96.1561,  16.8661),   -- Yangon
         ST_MakePoint(99.0042,  18.7883),   -- Chiang Mai
         ST_MakePoint(100.5018, 13.7563),   -- Bangkok
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC 2024', 'CITES Enforcement Note 2023']),

-- ── RHINO HORN (2 routes) ────────────────────────────────────────────────────

-- South Africa → Vietnam direct
('rhino_horn', 'Southern Africa', 'Vietnam',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(28.0473, -26.2041),   -- Johannesburg
         ST_MakePoint(106.6602, 10.8189)    -- Ho Chi Minh City
     ]
 ), 4326),
 'high',
 ARRAY['UNODC WWCR 2024', 'TRAFFIC 2024', 'SANParks 2024']),

-- Zimbabwe → China via Thailand
('rhino_horn', 'Southern Africa', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(31.0522, -17.8292),   -- Harare
         ST_MakePoint(100.5018, 13.7563),   -- Bangkok (transit)
         ST_MakePoint(121.4737, 31.2304)    -- Shanghai
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC 2023', 'WCO Enforcement 2024']),

-- ── TIGER (2 routes) ─────────────────────────────────────────────────────────

-- Laos → China overland
('tiger', 'Laos', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(102.6331, 17.9757),   -- Vientiane
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC Tiger Report 2024', 'UNODC 2024']),

-- Myanmar tiger farms → Vietnam/China
('tiger', 'Myanmar', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(96.1561,  16.8661),   -- Yangon
         ST_MakePoint(104.9282, 11.5564),   -- Phnom Penh (transit)
         ST_MakePoint(106.6602, 10.8189),   -- Ho Chi Minh City
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC 2023', 'CITES SC74 Doc']),

-- ── ROSEWOOD (2 routes) ──────────────────────────────────────────────────────

-- Cambodia/Laos → China via Vietnam
('rosewood', 'Indochina', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(104.9282, 11.5564),   -- Phnom Penh
         ST_MakePoint(102.6331, 17.9757),   -- Vientiane
         ST_MakePoint(105.8342, 21.0278),   -- Hanoi
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'high',
 ARRAY['UNODC WWCR 2024', 'TRAFFIC Timber Report 2024']),

-- Myanmar → China overland (rosewood)
('rosewood', 'Myanmar', 'China',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(96.1561, 16.8661),    -- Yangon
         ST_MakePoint(100.5018, 13.7563),   -- Bangkok
         ST_MakePoint(113.2644, 23.1291)    -- Guangzhou
     ]
 ), 4326),
 'medium',
 ARRAY['INTERPOL Operation Leaf 2023', 'TRAFFIC 2024']),

-- ── LIVE ANIMALS (2 routes) ──────────────────────────────────────────────────

-- Indonesia → Japan (otters, lorises, turtles as pet trade)
('live_animals', 'Indonesia', 'Japan',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(106.8456,  -6.2088),  -- Jakarta
         ST_MakePoint(103.8198,   1.3521),  -- Singapore (transit)
         ST_MakePoint(139.6917,  35.6895)   -- Tokyo
     ]
 ), 4326),
 'high',
 ARRAY['TRAFFIC 2024', 'CITES Trade DB 2024', 'INTERPOL 2024']),

-- Thailand → Gulf states (exotic pets)
('live_animals', 'Southeast Asia', 'Middle East',
 ST_SetSRID(ST_MakeLine(
     ARRAY[
         ST_MakePoint(100.5018, 13.7563),   -- Bangkok
         ST_MakePoint(55.2708,  25.2048)    -- Dubai
     ]
 ), 4326),
 'medium',
 ARRAY['TRAFFIC 2024', 'WCO Enforcement 2023']);
