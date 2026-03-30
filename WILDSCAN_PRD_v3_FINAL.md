# WILDSCAN — Product Requirements Document (Final Simplified)
# AI Wildlife Trafficking Detection Network

**Version**: 3.0 (Simplified + Multi-Model)
**Team Size**: 2
**Hackathon**: Unicorn Mafia x Techbible Hack Night (Bright Data + Cherry Ventures)
**Track**: Web MCP Agents (powered by Bright Data)

---

## 1. Problem Statement

Wildlife trafficking is a $23B criminal enterprise that has moved online. Sellers trade ivory, pangolin scales, rhino horn, and thousands of CITES-protected species across geo-restricted marketplaces using local languages and evolving code words.

The platforms are scattered (Facebook Marketplace, OLX, Carousell, Tokopedia, Shopee, Chợ Tốt), the languages are diverse (Thai, Vietnamese, Bahasa Indonesia, Mandarin, Burmese), and the listings are invisible to anyone outside the target country due to geo-restrictions.

**The geo-proxy requirement is absolute**: you cannot access Thai OLX or Vietnamese Facebook Marketplace from a UK or US IP.

---

## 2. Core Design Principle

**Structured data backbone → Deterministic scoring → AI analysis on top.**

Every detection is grounded in verified data from CITES, IUCN, and seizure records. Bright Data provides live marketplace access. LLMs analyze and generate intelligence — they don't guess at the foundation.

---

## 3. Multi-Model Strategy

WILDSCAN uses the right model for each task rather than routing everything through one provider.

| Task | Model | Why |
|------|-------|-----|
| Image classification (Image Analyst) | **GPT-4o Vision** | Superior fine-grained visual object identification. Better at distinguishing carved ivory from resin, pangolin scales from fish scales. |
| Translation (Linguist Agent) | **GPT-4o** | Stronger multilingual performance on Thai, Vietnamese, Burmese, Bahasa Indonesia. |
| Code word assessment (Linguist Agent LLM fallback) | **Claude Sonnet** | Better nuanced contextual reasoning. Can weigh ambiguous evidence and provide calibrated confidence. |
| Intelligence briefs + investigator chat | **Claude Opus / Sonnet** | Superior structured analytical writing. Better at following complex system prompts and maintaining analytical voice. |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DATA BACKBONE                                        │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Species+     │  │ IUCN Red     │  │ Seizure DB   │  │ Code Word  │ │
│  │ Checklist API│  │ List API     │  │ (extracted   │  │ Lexicon    │ │
│  │              │  │              │  │  from PDFs)  │  │ (static    │ │
│  │ CITES data,  │  │ Conservation │  │              │  │  ~500      │ │
│  │ appendix     │  │ status,      │  │ ~6,000       │  │  entries,  │ │
│  │ listings,    │  │ population   │  │ records from │  │  8 langs)  │ │
│  │ trade bans,  │  │ trends,      │  │ UNODC rpts,  │  │            │ │
│  │ distributions│  │ threats      │  │ TRAFFIC      │  │            │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         └─────────────────┴─────────────────┴───────────────┘         │
│                                  │                                      │
│                       ┌──────────▼──────────┐                          │
│                       │ PostgreSQL + PostGIS │                          │
│                       └──────────┬──────────┘                          │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────┐
│                    BRIGHT DATA LAYER                                     │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                 Bright Data Web Scraper MCP                        │  │
│  │                                                                    │  │
│  │  TH Proxy ──→ OLX.th, Facebook Marketplace TH                    │  │
│  │  VN Proxy ──→ Chợ Tốt, Facebook Marketplace VN                   │  │
│  │                                                                    │  │
│  │  (Architecture supports 25+ platforms across 7 regions.            │  │
│  │   Demo targets: 2 platforms, 1-2 regions.)                        │  │
│  └───────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────┐
│                    AGENT PIPELINE (LangGraph)                            │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌─────────────────────────┐             │
│  │ Scanner  │──▶│ Triage   │──▶│    PARALLEL ANALYSIS     │             │
│  │ Agent    │   │ Agent    │   │                          │             │
│  │          │   │(determ.) │   │ ┌──────────┐ ┌────────┐ │             │
│  │ Bright   │   │          │   │ │ Linguist │ │ Image  │ │             │
│  │ Data MCP │   │ regex +  │   │ │ Agent    │ │Analyst │ │             │
│  │          │   │ category │   │ │          │ │        │ │             │
│  │          │   │ check    │   │ │ Claude + │ │ GPT-4o │ │             │
│  │          │   │          │   │ │ GPT-4o   │ │ Vision │ │             │
│  └──────────┘   └──────────┘   │ └─────┬────┘ └───┬────┘ │             │
│                                 │       └─────┬────┘      │             │
│                                 └─────────────┼───────────┘             │
│                                               │                         │
│                                               ▼                         │
│                                 ┌─────────────────────────┐             │
│                                 │   Species Classifier     │             │
│                                 │   (Species+ / IUCN /     │             │
│                                 │    seizure cross-ref)    │             │
│                                 └────────────┬────────────┘             │
│                                              │                          │
│                                              ▼                          │
│                                 ┌─────────────────────────┐             │
│                                 │   Risk Scorer            │             │
│                                 │   (8 signals, determ.)   │             │
│                                 └────────────┬────────────┘             │
│                                              │                          │
│                                    ┌─────────┴─────────┐               │
│                                    │ score ≥ 60         │               │
│                                    ▼                    ▼               │
│                          ┌──────────────────┐  STORE + DONE             │
│                          │ Intel Analyst     │  (yellow/clear)          │
│                          │ (Claude)          │                          │
│                          └──────────────────┘                          │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼──────────────────────────────────────┐
│                           FRONTEND                                       │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                Globe Visualization (Deck.gl + Mapbox)              │  │
│  │  • Live detection pulses (red / amber / yellow)                   │  │
│  │  • Static trafficking route arcs (pre-loaded UNODC data)          │  │
│  │  • Species heatmap overlay                                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────────────────────────┐│
│  │ Detection  │ │ Species    │ │ Intelligence Brief + Chat (Claude)   ││
│  │ Feed (live)│ │ Panel      │ │                                      ││
│  └────────────┘ └────────────┘ └──────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Sources

### 5.1 Critical (system breaks without these)

| Source | What It Does For You | Access |
|--------|---------------------|--------|
| **Species+ Checklist API** (api.speciesplus.net) | Maps species → CITES appendix (I/II/III), trade suspensions, geographic ranges, common names in local languages. Powers Signal 2 (25 pts) and species-relative geographic risk (Signal 5). | Free REST API. Token required. |
| **IUCN Red List API** (apiv3.iucnredlist.org) | Conservation status (CR/EN/VU/NT/LC), population trends. Powers Signal 3 (12 pts). Adds conservation urgency to detections. | Free REST API. Token required. |
| **Code Word Lexicon** (pre-built) | ~500 entries across 8 languages mapping trafficking slang → species. First-pass deterministic matching. Powers Signal 1 (15 pts). | You build this from published research (Harrison et al. 2016, Xu et al. 2020, TRAFFIC reports). |

### 5.2 Important (strengthens detections, not load-bearing)

| Source | What It Does For You | Access |
|--------|---------------------|--------|
| **Seizure records** (~6,000 records) | Corroborates detections: "this matches 14 prior ivory seizures in Vietnam." Powers Signal 4 (13 pts). Also provides trafficking route data for globe arcs. | Extract from: UNODC World Wildlife Crime Reports (2016, 2020, 2024), TRAFFIC Bulletins (quarterly), UK/US/AU border force published data. All PDFs → tabula-py extraction. |
| **Trafficking routes** (~15-20 routes) | Static GeoJSON arcs on the globe showing known major corridors. Visual impact. | Pre-load from published UNODC route maps. No computation needed. |

### 5.3 Live Data

| Source | What It Does For You | Access |
|--------|---------------------|--------|
| **Bright Data** | Geo-proxied access to marketplace listings. The eyes of the entire system. | Web Scraper API + Scraping Browser MCP. Required for JS-heavy platforms (Facebook). |

### 5.4 Demo Targets

| Region | Platform | Why This One |
|--------|----------|-------------|
| **Thailand** | OLX.th | Simpler HTML structure, good test case for Thai language |
| **Vietnam** | Chợ Tốt | Active wildlife trade marketplace, well-documented code words |
| (stretch) | Facebook Marketplace TH or VN | Proves JS rendering via Scraping Browser works |

---

## 6. Code Word Lexicon

### Structure per entry:
```json
{
  "code_word": "ngà",
  "language": "vi",
  "species_scientific": "Loxodonta africana",
  "product_type": "ivory",
  "cites_appendix": "I",
  "confidence": 0.92,
  "source": "TRAFFIC Vietnam 2020",
  "context_required": [],
  "false_positive_contexts": [],
  "obfuscation_variants": ["ng@", "n.g.a", "nga`"],
  "status": "verified"
}
```

### Key fields:
- **`context_required`**: Co-occurring words needed to trigger. "bone" only matches if "medicine", "traditional", "kg", or "scales" appears nearby.
- **`false_positive_contexts`**: Words that cancel the match. "bone china", "French horn", "shell necklace craft." Grows over time via investigator feedback.
- **`obfuscation_variants`**: Known character substitutions, Unicode tricks, deliberate misspellings.

### Coverage targets:
- Thai: ~80, Vietnamese: ~90, Bahasa Indonesia: ~60, Mandarin: ~100
- English: ~80, Burmese: ~30, Filipino: ~25, Afrikaans: ~15
- Cross-language (emoji patterns, numeric codes): ~20

### Novel code word logging (passive):
When the LLM (Claude Sonnet) analyzes an ambiguous listing and identifies a potential new code word, it gets logged to a `proposed_code_words` table. No auto-promotion, no review queue. Just stored for future reference. Demo talking point: "Here's a code word the system discovered that wasn't in our original lexicon."

---

## 7. Agent Specifications

### 7.0 Pipeline Flow

```
START
  │
  ▼
[Scanner Agent] ─── Bright Data geo-proxied scraping
  │
  │  NormalizedListing[]
  ▼
[Deduplicate] ──── (content_hash match?) ──── SKIP
  │
  │  (new listings)
  ▼
[Triage Agent] ──── deterministic noise filter
  │
  ├── (noise) ──── STORE as "triaged_out", DONE
  │
  │  (passes triage)
  ▼
┌───────────────────────────────────┐
│       PARALLEL ANALYSIS            │
│                                    │
│  ┌──────────────┐ ┌────────────┐  │
│  │ Linguist     │ │ Image      │  │
│  │ Agent        │ │ Analyst    │  │
│  │ (lexicon +   │ │ (GPT-4o   │  │
│  │  GPT-4o +    │ │  Vision)   │  │
│  │  Claude)     │ │            │  │
│  └──────┬───────┘ └─────┬──────┘  │
│         └───────┬───────┘         │
└─────────────────┼─────────────────┘
                  │
                  │  TextAnalysis + ImageAnalysis
                  ▼
[Species Classifier] ── Species+ / IUCN cross-reference
  │                      + species-relative geographic risk
  │                      + seizure correlation
  │
  │  ClassifiedListing
  ▼
[Risk Scorer] ── 8-signal deterministic scoring
  │
  ├── (clear: < 40) ──── STORE, DONE
  ├── (yellow: 40-59) ── STORE, DONE
  │
  │  (amber/red: ≥ 60)
  ▼
[Intelligence Analyst] ── Claude generates brief
  │
  ▼
[Persist + Notify via WebSocket]
  │
  ▼
END
```

### LangGraph State:

```python
class WildScanState(TypedDict):
    # Input
    scan_job_id: str
    raw_listings: list[dict]

    # Scanner
    normalized_listings: list[dict]

    # Dedup
    new_listings: list[dict]
    duplicate_count: int

    # Triage
    triaged_listings: list[dict]
    triaged_out_count: int

    # Parallel analysis
    text_analyses: list[dict]
    image_analyses: list[dict]

    # Classifier
    classified_listings: list[dict]

    # Scorer
    scored_listings: list[dict]
    red_count: int
    amber_count: int
    yellow_count: int
    clear_count: int

    # Intel
    briefs_generated: list[dict]

    # Metadata
    errors: list[str]
    processing_time_ms: int
```

---

### 7.1 Scanner Agent

**Role**: Structured extraction from marketplace listings via Bright Data.
**Model**: None (scraping logic, no LLM).

```
INPUT:
  - target_marketplace: str
  - geo_proxy_region: str
  - search_queries: list[str] (category-based)
  - last_scan_cursor: datetime | null (incremental scanning)

BRIGHT DATA CONFIG:
  - zone: "scraping_browser" for JS-heavy (Facebook)
  - zone: "web_unlocker" for simpler sites (OLX, Chợ Tốt)
  - country: target geo (TH, VN)
  - render_js: true for Facebook, false for OLX

PLATFORM-SPECIFIC EXTRACTORS:
  Each platform has its own extraction logic producing the same output schema.

  OLX Extractor:
    - Simple HTML parsing (BeautifulSoup)
    - Fields available: title, description, price, images, seller_name, location
    - Fields NOT available: seller_rating, transaction_count

  Facebook Marketplace Extractor:
    - JS rendering required (Scraping Browser)
    - React state extraction for listing data
    - Fields available: title, price, images, location, post_date
    - Fields NOT available: seller_rating, seller_join_date (usually hidden)

  Chợ Tốt Extractor:
    - Moderate HTML complexity
    - Fields available: title, description, price, images, seller_id, location

OUTPUT:
  NormalizedListing:
    - listing_id: str
    - title: str (original language)
    - description: str (original language)
    - price: {amount: float, currency: str}
    - images: list[str] (URLs, downloaded + stored locally)
    - seller_id: str
    - seller_name: str
    - seller_join_date: date | null
    - seller_listing_count: int | null
    - location_text: str
    - post_date: datetime
    - platform: str
    - platform_category: str
    - raw_html: str (audit trail)
    - content_hash: str (SHA-256 of title + seller_id + platform)
    - language: str
```

---

### 7.2 Triage Agent

**Role**: Eliminate noise before expensive analysis. Deterministic. No LLM.
**Model**: None.

```
INPUT:
  - NormalizedListing (post-dedup)
  - code_word_lexicon (for fast regex scan)

PROCESS:
  Check 1 — CODE WORD QUICK-SCAN:
    Fast regex against all lexicon entries (exact match only, no fuzzy).
    ANY match → immediately passes triage, skip Check 2.

  Check 2 — CATEGORY + REGION FILTER (only if Check 1 found nothing):
    Is the listing in a high-risk category?
      High-risk: "antiques", "collectibles", "traditional medicine",
                 "pets", "exotic animals", "health", "art"
      Low-risk: "electronics", "vehicles", "clothing", "real estate"
    Is the seller profile suspicious?
      New account (<30 days) OR few listings (<10) → suspicious
      Established account (100+ listings, high rating) → not suspicious

    High-risk category + suspicious seller → passes triage
    High-risk category + established seller → passes triage (but lower priority)
    Low-risk category → triaged out

EXPECTED FILTER RATE: 70-80% of raw listings triaged out.

OUTPUT:
  TriageResult:
    - passed: bool
    - reason: "code_word_match" | "high_risk_category" | "triaged_out"
    - fast_match_code_words: list[str] (if any found)
```

---

### 7.3 Linguist Agent (Text Analysis Path)

**Role**: Code word detection, translation, linguistic risk assessment.
**Models**: GPT-4o (translation), Claude Sonnet (code word assessment).
**Runs in PARALLEL with Image Analyst.**

```
INPUT:
  - NormalizedListing (passed triage)
  - code_word_lexicon (region-filtered)

PROCESS:
  Phase 1 — DETERMINISTIC (no LLM):
    1. Exact match against lexicon
    2. Fuzzy match (Levenshtein distance ≤ 2) for misspellings
    3. Obfuscation variant matching (from lexicon entries)
    4. Context guard: check for false-positive contexts
    5. Context requirement: check for required co-occurring terms
    6. Assign code_word_confidence per match

  Phase 2 — LLM TRANSLATION (GPT-4o):
    Always runs (need English translation for Species Classifier).
    Prompt: "Translate this marketplace listing to English.
             Preserve any unusual terms, slang, or code-like language.
             Return: {translation: str, unusual_terms: list[str]}"

  Phase 3 — LLM CODE WORD ASSESSMENT (Claude Sonnet):
    Triggered ONLY when:
      a) Phase 1 returns 0.3 < confidence < 0.7 (ambiguous)
      b) No lexicon match but triage passed on high-risk category

    Prompt: "You are a wildlife trade linguistic analyst. Given this
             marketplace listing (original + translation), assess whether
             it contains indicators of wildlife trafficking. Consider code
             words, euphemisms, and contextual signals. Be precise about
             confidence. Return structured JSON:
             {
               is_suspicious: bool,
               confidence: float,
               reasoning: str,
               identified_products: [{product, species, confidence}],
               novel_code_words: [{word, language, proposed_species, evidence}]
             }"

  Phase 4 — NOVEL CODE WORD LOGGING (passive):
    If Claude identifies a novel code word with confidence > 0.8:
      INSERT into proposed_code_words table. No further action.

OUTPUT:
  TextAnalysis:
    - translation: str
    - code_word_matches: [{
        word: str,
        species_scientific: str,
        confidence: float,
        match_type: "exact" | "fuzzy" | "obfuscation" | "llm_novel"
      }]
    - linguistic_risk_score: float (0-1)
    - analysis_method: "deterministic" | "llm_assisted"
    - novel_code_words_logged: list[str]
```

---

### 7.4 Image Analyst (Vision Path)

**Role**: Classify wildlife products from listing images.
**Model**: GPT-4o Vision.
**Runs in PARALLEL with Linguist Agent.**

```
INPUT:
  - NormalizedListing.images (downloaded locally)

PROCESS:
  1. IMAGE PRE-FILTER:
     - Skip if no images
     - Skip obvious non-product images (platform logos, stock photos)

  2. CLASSIFICATION (GPT-4o Vision):
     For each image:
     Prompt: "You are a wildlife product identification specialist.
              Analyze this marketplace product image. Identify if the
              product is or contains material from a CITES-listed species.

              Products to check for: ivory (raw and carved), pangolin
              scales, rhino horn, tiger parts (bone, skin, teeth),
              tortoiseshell, shahtoosh wool, bear bile, coral, exotic
              birds (live), reptiles (live and products), shark fin,
              hornbill casque.

              Return JSON:
              {
                product_detected: bool,
                predicted_product: str,
                predicted_species_scientific: str,
                confidence: float,
                visual_evidence: str,
                alternative_explanations: str
              }"

  3. MULTI-IMAGE AGGREGATION:
     - Classify each image independently
     - Primary = highest confidence result
     - Flag inconsistencies across images

  4. CROSS-VALIDATION:
     - Compare with text analysis when both available
     - Agreement → confidence boost
     - Disagreement → flag for review

OUTPUT:
  ImageAnalysis:
    - primary_classification: {
        product_detected: bool,
        predicted_product: str,
        predicted_species: str,
        confidence: float,
        visual_evidence: str,
        alternative_explanations: str
      }
    - per_image_results: list[dict]
    - image_text_agreement: "agree" | "disagree" | "text_only" | "image_only"
    - image_risk_score: float (0-1)
```

---

### 7.5 Species Classifier

**Role**: Cross-reference detections against CITES/IUCN databases, compute species-relative geographic risk.
**Model**: None (database lookups, deterministic).

```
INPUT:
  - TextAnalysis (from Linguist Agent)
  - ImageAnalysis (from Image Analyst)
  - species_ref database (Species+ + IUCN)
  - seizure_records database

PROCESS:
  1. SPECIES RESOLUTION:
     - Merge species candidates from text and image paths
     - Resolve to species_ref records
     - Retrieve: CITES appendix, IUCN status, geographic range, trade suspensions

  2. SPECIES-RELATIVE GEOGRAPHIC RISK:
     Not "is the seller in a dangerous country" but "is this specific
     species/product combination suspicious in this specific location?"

     Examples:
       Rhino horn + South Africa     → HIGH (source country, illegal trade)
       Crocodile leather + Thailand  → LOW (legal CITES-permitted farming)
       Ivory + Vietnam               → HIGH (major destination market)
       Exotic birds + Indonesia      → HIGH (source country, high seizure rate)

     Implementation:
       - Join seller_location against species geographic_range
       - Check if legal_trade_countries includes this product for this country
       - Query seizure_records for this species in this country
       - Output: geographic_risk with score and reasoning

  3. SEIZURE PATTERN MATCHING:
     - Query seizure_records for matching species + region + product
     - Return correlation score + linked seizures as evidence
     - "This matches 14 ivory seizures in Vietnam in the past 3 years"

  4. PRICE CONTEXT (weak signal only):
     - Convert listing price to USD
     - Compare against known ranges
     - Flag "price_likely_not_representative" if placeholder or negotiation signal
     - Do NOT treat as reliable evidence

OUTPUT:
  ClassifiedListing:
    - species_matches: [{
        scientific_name: str,
        common_name: str,
        cites_appendix: "I" | "II" | "III" | null,
        iucn_status: "CR" | "EN" | "VU" | "NT" | "LC",
        trade_suspension_active: bool,
        confidence: float,
        source_path: "text" | "image" | "both"
      }]
    - geographic_risk: {
        score: float (0-1),
        reasoning: str,
        species_relative: true,
        legal_trade_possible: bool,
        supporting_seizures: int
      }
    - seizure_correlations: [{
        seizure_id: str,
        country: str,
        date: date,
        species: str,
        similarity_score: float
      }]
    - price_analysis: {
        listing_price_usd: float,
        expected_range: {low, high},
        price_representative: bool,
        anomaly_type: str
      }
```

---

### 7.6 Risk Scorer (Deterministic)

**Role**: Compute 0-100 risk score from 8 weighted signals. NO LLM. Pure math.
**Model**: None.

```
SCORING MODEL v3:

  Signal 1: CODE WORD CONFIDENCE               max 15 pts
    Exact lexicon match ──────────────────────  15
    Fuzzy match ──────────────────────────────  11
    LLM-detected novel ───────────────────────   7
    No match ─────────────────────────────────   0

  Signal 2: CITES APPENDIX                      max 25 pts
    Appendix I (ban on commercial trade) ─────  25
    Appendix II (regulated trade) ────────────  15
    Appendix III (country-specific) ──────────   8
    Not listed ───────────────────────────────   0

  Signal 3: IUCN CONSERVATION STATUS            max 12 pts
    Critically Endangered ────────────────────  12
    Endangered ───────────────────────────────  10
    Vulnerable ───────────────────────────────   7
    Near Threatened ──────────────────────────   3
    Least Concern ────────────────────────────   0

  Signal 4: SEIZURE CORRELATION                 max 13 pts
    High (same species + region, recent) ─────  13
    Medium ───────────────────────────────────   8
    Low ──────────────────────────────────────   4
    None ─────────────────────────────────────   0

  Signal 5: GEOGRAPHIC RISK (species-relative)  max 10 pts
    High risk for THIS species in THIS place ─  10
    Medium ───────────────────────────────────   6
    Low ──────────────────────────────────────   2
    Legal trade established for this product ─   0

  Signal 6: SELLER BEHAVIOR                     max 10 pts
    Multiple wildlife-adjacent listings ──────  10
    Cross-platform presence detected ─────────   8
    New account (<30 days) ───────────────────   5
    Established account, single listing ──────   0

  Signal 7: PRICE SIGNAL (weak)                 max 3 pts
    Within known black market range ──────────   3
    Anomalous but plausible ──────────────────   1
    Not representative / unknown ─────────────   0

  Signal 8: IMAGE EVIDENCE                      max 12 pts
    High-confidence wildlife product ─────────  12
    Medium-confidence ────────────────────────   8
    Low-confidence ───────────────────────────   3
    No product detected / no images ──────────   0

  TOTAL: 100 pts

  TEXT-IMAGE AGREEMENT BONUS:
    Both text + image independently identify same species → +5 pts
    (capped at 100)

  HARD OVERRIDES:
    Active CITES trade suspension for species + country  → min 80 (Red)
    Appendix I + source country + image evidence         → min 65 (Amber)

  ALERT TIERS:
    🔴 Red    ≥ 80  — High confidence trafficking
    🟠 Amber  ≥ 60  — Significant risk, investigate
    🟡 Yellow ≥ 40  — Moderate risk, monitor
    ⚪ Clear  < 40  — Low risk / likely false positive

OUTPUT:
  ScoredListing:
    - risk_score: int (0-100)
    - alert_tier: "red" | "amber" | "yellow" | "clear"
    - signal_breakdown: {signal_name: {score, max, evidence}}
    - agreement_bonus: int
    - hard_override_applied: bool
    - hard_override_reason: str | null
```

---

### 7.7 Intelligence Analyst

**Role**: Generate structured intelligence briefs for amber/red detections.
**Model**: Claude Opus / Sonnet.

```
INPUT:
  - ScoredListing with all signal breakdowns
  - Species data from DB
  - Seizure correlations
  - Text + image analysis results

SYSTEM PROMPT:
  "You are a wildlife trafficking intelligence analyst working for an
  international enforcement coordination center. You receive structured
  detection data from automated monitoring systems.

  Rules:
  - Cite specific signal scores and evidence
  - Distinguish high-confidence findings from inferences
  - Recommend concrete next steps with relevant jurisdictions
  - Reference applicable laws (CITES, national wildlife protection acts)
  - Always note alternative explanations
  - Be precise about confidence levels"

OUTPUT:
  IntelligenceBrief:
    - executive_summary: str (2-3 sentences)
    - risk_assessment: str
    - key_evidence: [{evidence_type, description, confidence, source}]
    - species_profile: str (conservation context)
    - legal_framework: [{jurisdiction, applicable_law, offense_classification}]
    - recommended_actions: [str]
    - confidence_statement: str
    - alternative_explanations: [str]

INTERACTIVE CHAT:
  - Investigators ask follow-up questions
  - Claude receives full case context + conversation history
  - Streaming via SSE
```

---

## 8. Investigator Feedback Loop (Lightweight)

**Scope**: One endpoint, one table, one update function.

### Endpoint:
```
POST /api/detections/{id}/review
{
  "verdict": "true_positive" | "false_positive" | "uncertain",
  "notes": "This is a bone china teapot, not wildlife",
  "false_positive_trigger": "bone",
  "false_positive_context": "china teapot"
}
```

### What happens:
- **False positive**: Appends `false_positive_context` to the triggering code word's `false_positive_contexts` array in the lexicon. Next time "bone" appears near "china teapot," it won't match.
- **True positive**: Increments `detection_count` on matched code words.
- **Uncertain**: Stored. No automatic action.

### Why it matters for demo:
"The system learns from every investigation. Mark a false positive, and WildScan never makes that mistake again."

---

## 9. Database Schema

```sql
-- =====================================================
-- REFERENCE DATA
-- =====================================================

CREATE TABLE species_ref (
    id SERIAL PRIMARY KEY,
    scientific_name VARCHAR(255) NOT NULL UNIQUE,
    common_name VARCHAR(255),
    common_names_local JSONB,
    cites_appendix VARCHAR(5),
    iucn_status VARCHAR(5),
    population_trend VARCHAR(20),
    geographic_range GEOMETRY(MultiPolygon, 4326),
    trade_suspension_active BOOLEAN DEFAULT FALSE,
    trade_suspension_countries TEXT[],
    typical_products TEXT[],
    legal_trade_countries JSONB,
    black_market_price_range JSONB,
    last_updated TIMESTAMP
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
    transit_countries VARCHAR(3)[],
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
    evidence_sources TEXT[]
);

CREATE TABLE code_word_lexicon (
    id SERIAL PRIMARY KEY,
    code_word VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL,
    species_id INTEGER REFERENCES species_ref(id),
    product_type VARCHAR(100),
    confidence FLOAT,
    context_required TEXT[],
    false_positive_contexts TEXT[],
    obfuscation_variants TEXT[],
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

-- =====================================================
-- LIVE MONITORING
-- =====================================================

CREATE TABLE scan_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    marketplace VARCHAR(100) NOT NULL,
    region VARCHAR(10) NOT NULL,
    proxy_country VARCHAR(3) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    search_queries TEXT[],
    listings_found INTEGER,
    listings_passed_triage INTEGER,
    listings_flagged INTEGER,
    last_scan_cursor TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_job_id UUID REFERENCES scan_jobs(id),
    platform VARCHAR(100) NOT NULL,
    platform_listing_id VARCHAR(255),
    title_original TEXT NOT NULL,
    title_translated TEXT,
    description_original TEXT,
    description_translated TEXT,
    price_amount FLOAT,
    price_currency VARCHAR(10),
    images TEXT[],
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
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),

    -- Linguist Agent (text path)
    code_word_matches JSONB,
    linguistic_risk_score FLOAT,
    analysis_method VARCHAR(20),

    -- Image Analyst (vision path)
    image_classification JSONB,
    image_risk_score FLOAT,
    text_image_agreement VARCHAR(20),

    -- Species Classifier
    species_matches JSONB,
    geographic_risk JSONB,
    seizure_correlations JSONB,
    price_analysis JSONB,

    -- Risk Scorer
    risk_score INTEGER,
    alert_tier VARCHAR(10),
    signal_breakdown JSONB,
    agreement_bonus INTEGER DEFAULT 0,
    hard_override_applied BOOLEAN DEFAULT FALSE,
    hard_override_reason TEXT,

    pipeline_version VARCHAR(20),
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE listing_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),
    verdict VARCHAR(20) NOT NULL,
    notes TEXT,
    false_positive_trigger VARCHAR(255),
    false_positive_context TEXT,
    reviewer VARCHAR(100),
    reviewed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE intelligence_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),
    brief_type VARCHAR(20),
    executive_summary TEXT,
    full_brief JSONB,
    recommended_actions TEXT[],
    jurisdictions TEXT[],
    generated_by VARCHAR(50),
    chat_history JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_listings_platform_seller ON listings(platform, seller_id);
CREATE INDEX idx_listings_content_hash ON listings(content_hash);
CREATE INDEX idx_listings_location ON listings USING GIST(location_point);
CREATE INDEX idx_analysis_risk ON listing_analysis(risk_score DESC);
CREATE INDEX idx_analysis_tier ON listing_analysis(alert_tier);
CREATE INDEX idx_seizures_species ON seizure_records(species_id);
CREATE INDEX idx_seizures_location ON seizure_records USING GIST(seizure_location);
CREATE INDEX idx_species_range ON species_ref USING GIST(geographic_range);
CREATE INDEX idx_code_words_lang ON code_word_lexicon(language, status);
CREATE INDEX idx_routes_geometry ON trafficking_routes USING GIST(route_geometry);
```

---

## 10. API Design

```yaml
# ── Scanning ──
POST   /api/scan/start                    # Trigger scan for marketplace + region
GET    /api/scan/jobs                      # List jobs with status
GET    /api/scan/jobs/{id}                 # Job detail

# ── Detections ──
GET    /api/detections                     # All detections (filter: tier, region, species)
GET    /api/detections/{id}                # Full detail: all signals, evidence chain
GET    /api/detections/feed                # WebSocket: live stream
GET    /api/detections/stats               # Dashboard aggregates
POST   /api/detections/{id}/review         # Investigator feedback

# ── Species ──
GET    /api/species                        # All monitored species
GET    /api/species/{id}                   # Detail + detection count

# ── Intelligence ──
POST   /api/intel/brief/{detection_id}     # Generate Claude brief
POST   /api/intel/chat                     # Chat about case (SSE streaming)

# ── Lexicon ──
GET    /api/lexicon                        # Current lexicon
GET    /api/lexicon/proposed               # Novel code words discovered

# ── Globe ──
GET    /api/globe/detections               # GeoJSON: active detections
GET    /api/globe/routes                   # GeoJSON: static trafficking route arcs
GET    /api/globe/heatmap                  # Heatmap by species/region
GET    /api/globe/stats                    # Global counters
```

---

## 11. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python + FastAPI |
| **Pipeline** | LangGraph (deterministic + parallel branching) |
| **Database** | PostgreSQL 16 + PostGIS 3.4 |
| **Cache / Queue** | Redis |
| **Scraping** | Bright Data Web Scraper API + Scraping Browser MCP |
| **AI — Vision** | GPT-4o Vision (image classification) |
| **AI — Translation** | GPT-4o (multilingual translation) |
| **AI — Reasoning** | Claude Sonnet (code word assessment, ambiguous cases) |
| **AI — Briefs** | Claude Opus/Sonnet (intelligence briefs + chat) |
| **NLP** | spaCy + custom tokenizers (fuzzy matching) |
| **Frontend** | Next.js 14 |
| **Globe** | Deck.gl + Mapbox GL JS |
| **Real-time** | WebSocket + SSE |
| **Deploy** | Docker + Docker Compose |

---

## 12. Frontend

### Globe (Deck.gl + Mapbox)

Layer stack (bottom → top):
1. Dark globe base
2. Trafficking route arcs (static, pre-loaded UNODC data)
3. Detection markers — pulsing dots sized by risk score
   - 🔴 Red ≥ 80 | 🟠 Amber ≥ 60 | 🟡 Yellow ≥ 40
4. Selection highlight on click

### Side Panels:
- **Detection Feed**: Live scrolling list, auto-updates via WebSocket
- **Species Panel**: CITES, IUCN, conservation context for selected species
- **Case Detail**: Full 8-signal breakdown, listing images, evidence chain
- **Intelligence Brief**: Claude-generated analysis + interactive chat
- **Stats Bar**: Total detections, species count, countries, accuracy

---

## 13. Build Priority

### Phase 1: Data Backbone (build first)
1. Species+ API → species_ref table
2. IUCN Red List API → merge into species_ref
3. Code word lexicon (research + manual curation)
4. Seizure data extraction from published PDFs
5. Static trafficking routes (15-20 routes as GeoJSON)

### Phase 2: Core Pipeline
6. Bright Data → Scanner Agent (OLX.th first)
7. Triage Agent
8. Linguist Agent (deterministic + GPT-4o translation + Claude fallback)
9. Image Analyst (GPT-4o Vision)
10. Species Classifier
11. Risk Scorer

### Phase 3: Intelligence + Frontend
12. Intelligence Analyst (Claude briefs)
13. Globe visualization
14. Detection feed + case detail panels
15. Chat interface

### Phase 4: Polish (if time allows)
16. Feedback loop endpoint
17. Second platform extractor (Chợ Tốt or Facebook)
18. Novel code word logging
19. Stats dashboard

---

## 14. Scope Summary

### IN (essential):
- Bright Data geo-proxied scraping (2 platforms)
- 6-agent pipeline: Scanner → Triage → Linguist + Image (parallel) → Species Classifier → Risk Scorer → Intel Analyst
- Multi-model: GPT-4o (vision + translation) + Claude (reasoning + briefs)
- 8-signal deterministic risk scoring
- Species+ and IUCN data backbone
- Static code word lexicon (~500 entries)
- Globe with detection markers + route arcs
- Intelligence briefs + chat
- Investigator feedback endpoint

### OUT (cut for scope):
- Network Mapper (seller network detection)
- Takedown Tracker (listing lifecycle monitoring)
- Lexicon auto-evolution (3-detection threshold, review queue)
- CITES Trade Database (historical volumes)
- More than 2-3 platform extractors
- Scan scheduling / budget management

### PASSIVE (low effort, good story):
- Novel code word logging (just a DB insert)
- Proposed code words table (LLM discoveries stored for reference)
