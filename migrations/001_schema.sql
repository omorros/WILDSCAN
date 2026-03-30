CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE species_ref (
    id SERIAL PRIMARY KEY,
    scientific_name VARCHAR(255) NOT NULL UNIQUE,
    common_name VARCHAR(255),
    common_names_local JSONB DEFAULT '{}',
    cites_appendix VARCHAR(5),
    iucn_status VARCHAR(5),
    population_trend VARCHAR(20),
    range_countries VARCHAR(3)[] DEFAULT '{}',
    trade_suspension_active BOOLEAN DEFAULT FALSE,
    trade_suspension_countries TEXT[] DEFAULT '{}',
    typical_products TEXT[] DEFAULT '{}',
    legal_trade_countries JSONB DEFAULT '{}',
    black_market_price_range JSONB DEFAULT '{}',
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE seizure_records (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    source_document VARCHAR(255),
    species_id INTEGER REFERENCES species_ref(id),
    product_type VARCHAR(100),
    quantity FLOAT,
    quantity_unit VARCHAR(20),
    seizure_date DATE,
    seizure_country VARCHAR(3),
    seizure_location GEOMETRY(Point, 4326),
    origin_country VARCHAR(3),
    transit_countries VARCHAR(3)[] DEFAULT '{}',
    destination_country VARCHAR(3),
    trafficking_method VARCHAR(100),
    seizure_value_usd FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE trafficking_routes (
    id SERIAL PRIMARY KEY,
    species_group VARCHAR(100),
    origin_region VARCHAR(100),
    destination_region VARCHAR(100),
    route_geometry GEOMETRY(LineString, 4326),
    activity_level VARCHAR(20),
    evidence_sources TEXT[] DEFAULT '{}'
);

CREATE TABLE code_word_lexicon (
    id SERIAL PRIMARY KEY,
    code_word VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    species_id INTEGER REFERENCES species_ref(id),
    product_type VARCHAR(100),
    confidence FLOAT,
    context_required TEXT[] DEFAULT '{}',
    false_positive_contexts TEXT[] DEFAULT '{}',
    obfuscation_variants TEXT[] DEFAULT '{}',
    source VARCHAR(255),
    status VARCHAR(20) DEFAULT 'verified',
    detection_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE proposed_code_words (
    id SERIAL PRIMARY KEY,
    code_word VARCHAR(255) NOT NULL,
    language VARCHAR(10),
    proposed_species VARCHAR(255),
    evidence TEXT,
    llm_confidence FLOAT,
    source_listing_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scan_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    marketplace VARCHAR(100) NOT NULL,
    region VARCHAR(10) NOT NULL,
    proxy_country VARCHAR(3) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    search_queries TEXT[] DEFAULT '{}',
    listings_found INTEGER DEFAULT 0,
    listings_passed_triage INTEGER DEFAULT 0,
    listings_flagged INTEGER DEFAULT 0,
    last_scan_cursor TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_job_id UUID REFERENCES scan_jobs(id),
    platform VARCHAR(100) NOT NULL,
    platform_listing_id VARCHAR(255),
    title_original TEXT NOT NULL,
    title_translated TEXT,
    description_original TEXT,
    description_translated TEXT,
    price_amount FLOAT,
    price_currency VARCHAR(10),
    images TEXT[] DEFAULT '{}',
    images_local TEXT[] DEFAULT '{}',
    seller_id VARCHAR(255),
    seller_name VARCHAR(255),
    seller_join_date DATE,
    seller_listing_count INTEGER,
    location_text VARCHAR(500),
    location_point GEOMETRY(Point, 4326),
    post_date TIMESTAMP,
    platform_category VARCHAR(100),
    raw_html TEXT,
    content_hash VARCHAR(64),
    language VARCHAR(10),
    triage_passed BOOLEAN,
    triage_reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, platform_listing_id)
);

CREATE TABLE listing_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id) UNIQUE,
    code_word_matches JSONB DEFAULT '[]',
    linguistic_risk_score FLOAT DEFAULT 0,
    analysis_method VARCHAR(20),
    image_classification JSONB DEFAULT '{}',
    image_risk_score FLOAT DEFAULT 0,
    text_image_agreement VARCHAR(20),
    species_matches JSONB DEFAULT '[]',
    geographic_risk JSONB DEFAULT '{}',
    seizure_correlations JSONB DEFAULT '[]',
    price_analysis JSONB DEFAULT '{}',
    risk_score INTEGER DEFAULT 0,
    alert_tier VARCHAR(10) DEFAULT 'clear',
    signal_breakdown JSONB DEFAULT '{}',
    agreement_bonus INTEGER DEFAULT 0,
    hard_override_applied BOOLEAN DEFAULT FALSE,
    hard_override_reason TEXT,
    pipeline_version VARCHAR(20) DEFAULT '1.0',
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE listing_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id),
    verdict VARCHAR(20) NOT NULL,
    notes TEXT,
    false_positive_trigger VARCHAR(255),
    false_positive_context TEXT,
    reviewer VARCHAR(100),
    reviewed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE intelligence_briefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id),
    brief_type VARCHAR(20),
    executive_summary TEXT,
    full_brief JSONB DEFAULT '{}',
    recommended_actions TEXT[] DEFAULT '{}',
    jurisdictions TEXT[] DEFAULT '{}',
    generated_by VARCHAR(50),
    chat_history JSONB DEFAULT '[]',
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_listings_platform_seller ON listings(platform, seller_id);
CREATE INDEX idx_listings_content_hash ON listings(content_hash);
CREATE INDEX idx_listings_location ON listings USING GIST(location_point);
CREATE INDEX idx_analysis_risk ON listing_analysis(risk_score DESC);
CREATE INDEX idx_analysis_tier ON listing_analysis(alert_tier);
CREATE INDEX idx_seizures_species ON seizure_records(species_id);
CREATE INDEX idx_seizures_location ON seizure_records USING GIST(seizure_location);
CREATE INDEX idx_code_words_lang ON code_word_lexicon(language, status);
CREATE INDEX idx_routes_geometry ON trafficking_routes USING GIST(route_geometry);
