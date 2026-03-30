import uuid
from datetime import datetime, date

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean, Column, Date, Float, Integer, String, Text, TIMESTAMP, ForeignKey, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class SpeciesRef(Base):
    __tablename__ = "species_ref"
    id = Column(Integer, primary_key=True)
    scientific_name = Column(String(255), nullable=False, unique=True)
    common_name = Column(String(255))
    common_names_local = Column(JSONB, default={})
    cites_appendix = Column(String(5))
    iucn_status = Column(String(5))
    population_trend = Column(String(20))
    range_countries = Column(ARRAY(String(3)), default=[])
    trade_suspension_active = Column(Boolean, default=False)
    trade_suspension_countries = Column(ARRAY(Text), default=[])
    typical_products = Column(ARRAY(Text), default=[])
    legal_trade_countries = Column(JSONB, default={})
    black_market_price_range = Column(JSONB, default={})
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
    code_words = relationship("CodeWordLexicon", back_populates="species")
    seizures = relationship("SeizureRecord", back_populates="species")


class SeizureRecord(Base):
    __tablename__ = "seizure_records"
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)
    source_document = Column(String(255))
    species_id = Column(Integer, ForeignKey("species_ref.id"))
    product_type = Column(String(100))
    quantity = Column(Float)
    quantity_unit = Column(String(20))
    seizure_date = Column(Date)
    seizure_country = Column(String(3))
    seizure_location = Column(Geometry("POINT", srid=4326))
    origin_country = Column(String(3))
    transit_countries = Column(ARRAY(String(3)), default=[])
    destination_country = Column(String(3))
    trafficking_method = Column(String(100))
    seizure_value_usd = Column(Float)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    species = relationship("SpeciesRef", back_populates="seizures")


class TraffickingRoute(Base):
    __tablename__ = "trafficking_routes"
    id = Column(Integer, primary_key=True)
    species_group = Column(String(100))
    origin_region = Column(String(100))
    destination_region = Column(String(100))
    route_geometry = Column(Geometry("LINESTRING", srid=4326))
    activity_level = Column(String(20))
    evidence_sources = Column(ARRAY(Text), default=[])


class CodeWordLexicon(Base):
    __tablename__ = "code_word_lexicon"
    id = Column(Integer, primary_key=True)
    code_word = Column(String(255), nullable=False)
    language = Column(String(10), nullable=False)
    species_id = Column(Integer, ForeignKey("species_ref.id"))
    product_type = Column(String(100))
    confidence = Column(Float)
    context_required = Column(ARRAY(Text), default=[])
    false_positive_contexts = Column(ARRAY(Text), default=[])
    obfuscation_variants = Column(ARRAY(Text), default=[])
    source = Column(String(255))
    status = Column(String(20), default="verified")
    detection_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    species = relationship("SpeciesRef", back_populates="code_words")


class ProposedCodeWord(Base):
    __tablename__ = "proposed_code_words"
    id = Column(Integer, primary_key=True)
    code_word = Column(String(255), nullable=False)
    language = Column(String(10))
    proposed_species = Column(String(255))
    evidence = Column(Text)
    llm_confidence = Column(Float)
    source_listing_id = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class ScanJob(Base):
    __tablename__ = "scan_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketplace = Column(String(100), nullable=False)
    region = Column(String(10), nullable=False)
    proxy_country = Column(String(3), nullable=False)
    status = Column(String(20), default="pending")
    search_queries = Column(ARRAY(Text), default=[])
    listings_found = Column(Integer, default=0)
    listings_passed_triage = Column(Integer, default=0)
    listings_flagged = Column(Integer, default=0)
    last_scan_cursor = Column(TIMESTAMP)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    listings = relationship("Listing", back_populates="scan_job")


class Listing(Base):
    __tablename__ = "listings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id"))
    platform = Column(String(100), nullable=False)
    platform_listing_id = Column(String(255))
    title_original = Column(Text, nullable=False)
    title_translated = Column(Text)
    description_original = Column(Text)
    description_translated = Column(Text)
    price_amount = Column(Float)
    price_currency = Column(String(10))
    images = Column(ARRAY(Text), default=[])
    images_local = Column(ARRAY(Text), default=[])
    seller_id = Column(String(255))
    seller_name = Column(String(255))
    seller_join_date = Column(Date)
    seller_listing_count = Column(Integer)
    location_text = Column(String(500))
    location_point = Column(Geometry("POINT", srid=4326))
    post_date = Column(TIMESTAMP)
    platform_category = Column(String(100))
    raw_html = Column(Text)
    content_hash = Column(String(64))
    language = Column(String(10))
    triage_passed = Column(Boolean)
    triage_reason = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("platform", "platform_listing_id", name="uq_platform_listing"),)
    scan_job = relationship("ScanJob", back_populates="listings")
    analysis = relationship("ListingAnalysis", back_populates="listing", uselist=False)
    reviews = relationship("ListingReview", back_populates="listing")
    briefs = relationship("IntelligenceBrief", back_populates="listing")


class ListingAnalysis(Base):
    __tablename__ = "listing_analysis"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), unique=True)
    code_word_matches = Column(JSONB, default=[])
    linguistic_risk_score = Column(Float, default=0)
    analysis_method = Column(String(20))
    image_classification = Column(JSONB, default={})
    image_risk_score = Column(Float, default=0)
    text_image_agreement = Column(String(20))
    species_matches = Column(JSONB, default=[])
    geographic_risk = Column(JSONB, default={})
    seizure_correlations = Column(JSONB, default=[])
    price_analysis = Column(JSONB, default={})
    risk_score = Column(Integer, default=0)
    alert_tier = Column(String(10), default="clear")
    signal_breakdown = Column(JSONB, default={})
    agreement_bonus = Column(Integer, default=0)
    hard_override_applied = Column(Boolean, default=False)
    hard_override_reason = Column(Text)
    pipeline_version = Column(String(20), default="1.0")
    processed_at = Column(TIMESTAMP, default=datetime.utcnow)
    listing = relationship("Listing", back_populates="analysis")


class ListingReview(Base):
    __tablename__ = "listing_reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"))
    verdict = Column(String(20), nullable=False)
    notes = Column(Text)
    false_positive_trigger = Column(String(255))
    false_positive_context = Column(Text)
    reviewer = Column(String(100))
    reviewed_at = Column(TIMESTAMP, default=datetime.utcnow)
    listing = relationship("Listing", back_populates="reviews")


class IntelligenceBrief(Base):
    __tablename__ = "intelligence_briefs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"))
    brief_type = Column(String(20))
    executive_summary = Column(Text)
    full_brief = Column(JSONB, default={})
    recommended_actions = Column(ARRAY(Text), default=[])
    jurisdictions = Column(ARRAY(Text), default=[])
    generated_by = Column(String(50))
    chat_history = Column(JSONB, default=[])
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)
    listing = relationship("Listing", back_populates="briefs")
