export interface Detection {
  id: string;
  platform: string;
  title: string;
  risk_score: number;
  alert_tier: "red" | "amber" | "yellow" | "clear";
  species: string | null;
  lat: number | null;
  lng: number | null;
  location_text?: string;
  post_date?: string | null;
}

export interface DetectionDetail {
  id: string;
  platform: string;
  title_original: string;
  title_translated: string | null;
  description_original: string | null;
  description_translated: string | null;
  price_amount: number | null;
  price_currency: string | null;
  images: string[];
  images_local: string[];
  seller_id: string | null;
  seller_name: string | null;
  seller_join_date: string | null;
  seller_listing_count: number | null;
  location: { lat: number; lng: number; text: string } | null;
  post_date: string | null;
  language: string | null;
  risk_score: number;
  alert_tier: "red" | "amber" | "yellow" | "clear";
  signal_breakdown: Record<string, { score: number; max: number }>;
  agreement_bonus: number | null;
  hard_override_applied: boolean;
  hard_override_reason: string | null;
  code_word_matches: CodeWordMatch[];
  linguistic_risk_score: number | null;
  analysis_method: string | null;
  image_classification: ImageClassification | null;
  image_risk_score: number | null;
  text_image_agreement: string | null;
  species_matches: SpeciesMatch[];
  geographic_risk: GeographicRisk | null;
  seizure_correlations: SeizureCorrelation[];
  brief: IntelBrief | null;
}

export interface CodeWordMatch {
  id: number;
  code_word: string;
  species_scientific: string;
  product_type: string;
  match_type: "exact" | "fuzzy" | "obfuscation" | "llm_novel";
  confidence: number;
}

export interface ImageClassification {
  product_detected: boolean;
  predicted_product: string;
  predicted_species: string;
  confidence: number;
  visual_evidence: string;
  alternative_explanations: string;
}

export interface SpeciesMatch {
  scientific_name: string;
  common_name: string;
  cites_appendix: string;
  iucn_status: string;
  trade_suspension_active: boolean;
  confidence: number;
  source_path: string;
}

export interface GeographicRisk {
  score: number;
  reasoning: string;
  legal_trade_possible: boolean;
  supporting_seizures: number;
}

export interface SeizureCorrelation {
  seizure_id: string;
  country: string;
  date: string;
  species: string;
  product_type: string;
  quantity: number;
  quantity_unit: string;
}

export interface IntelBrief {
  executive_summary: string;
  risk_assessment: string;
  key_evidence: { evidence_type: string; description: string; confidence: string; source: string }[];
  species_profile: string;
  legal_framework: { jurisdiction: string; applicable_law: string; offense_classification: string }[];
  recommended_actions: string[];
  confidence_statement: string;
  alternative_explanations: string[];
}

export interface GlobeResponse {
  detections: {
    type: "FeatureCollection";
    features: {
      type: "Feature";
      geometry: { type: "Point"; coordinates: [number, number] };
      properties: Detection;
    }[];
  };
  routes: {
    type: "FeatureCollection";
    features: {
      type: "Feature";
      geometry: { type: "LineString"; coordinates: [number, number][] };
      properties: { species_group: string; origin: string; destination: string; activity_level: string };
    }[];
  };
  stats: GlobeStats;
}

export interface GlobeStats {
  total_detections: number;
  red: number;
  amber: number;
  yellow: number;
  countries: number;
}

export interface ScanJob {
  id: string;
  marketplace: string;
  region: string;
  status: "running" | "completed" | "failed";
  listings_found: number | null;
  listings_passed_triage: number | null;
  listings_flagged: number | null;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}
