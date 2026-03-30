import asyncio

from langgraph.graph import StateGraph, END

from backend.agents.state import WildScanState
from backend.agents.triage import triage_listing
from backend.agents.risk_scorer import score_listing
from backend.agents.linguist import analyze_text
from backend.agents.image_analyst import analyze_images
from backend.agents.species_classifier import classify_species
from backend.agents.intel_analyst import generate_brief


def scanner_node(state: WildScanState) -> dict:
    return {"normalized_listings": state.get("raw_listings", [])}


def triage_node(state: WildScanState) -> dict:
    triaged = []
    triaged_out = 0
    lexicon = state.get("_lexicon_entries", [])
    for listing in state.get("normalized_listings", []):
        result = triage_listing(listing, lexicon)
        listing["triage_passed"] = result["passed"]
        listing["triage_reason"] = result["reason"]
        listing["triage_code_words"] = result.get("fast_match_code_words", [])
        if result["passed"]:
            triaged.append(listing)
        else:
            triaged_out += 1
    return {"triaged_listings": triaged, "triaged_out_count": triaged_out}


async def linguist_node(state: WildScanState) -> dict:
    """Run lexicon matching + GPT-4o translation + Claude fallback on each listing."""
    lexicon = state.get("_lexicon_entries", [])
    analyses = []
    for listing in state.get("triaged_listings", []):
        text_result = await analyze_text(listing, lexicon)
        listing["text_analysis"] = text_result
        analyses.append(text_result)
    return {"text_analyses": analyses}


async def image_analyst_node(state: WildScanState) -> dict:
    """Run GPT-4o Vision on each listing's images."""
    analyses = []
    for listing in state.get("triaged_listings", []):
        image_result = await analyze_images(listing)
        listing["image_analysis"] = image_result
        analyses.append(image_result)
    return {"image_analyses": analyses}


async def species_classifier_node(state: WildScanState) -> dict:
    """Cross-reference detections against species DB."""
    db_session = state.get("_db_session")
    classified = []

    for listing in state.get("triaged_listings", []):
        text_analysis = listing.get("text_analysis", {})
        image_analysis = listing.get("image_analysis", {})

        if db_session:
            classification = await classify_species(text_analysis, image_analysis, listing, db_session)
        else:
            classification = {
                "species_matches": [],
                "geographic_risk": {"score": 0, "reasoning": "No DB session", "legal_trade_possible": False, "supporting_seizures": 0},
                "seizure_correlations": [],
                "text_image_agreement": "none",
            }

        # Build signals for the risk scorer
        code_matches = text_analysis.get("code_word_matches", [])
        img_primary = image_analysis.get("primary_classification", {})
        species_matches = classification.get("species_matches", [])
        top_species = species_matches[0] if species_matches else {}
        geo_risk = classification.get("geographic_risk", {})

        # Determine code word confidence level
        if code_matches:
            best_match = max(code_matches, key=lambda m: m.get("confidence", 0))
            code_confidence = best_match.get("match_type", "none")
        else:
            code_confidence = "none"

        # Determine image evidence level
        img_confidence = img_primary.get("confidence", 0) if img_primary.get("product_detected") else 0
        if img_confidence >= 0.7:
            image_evidence = "high"
        elif img_confidence >= 0.4:
            image_evidence = "medium"
        elif img_confidence > 0:
            image_evidence = "low"
        else:
            image_evidence = "none"

        # Determine seizure correlation
        seizure_count = geo_risk.get("supporting_seizures", 0)
        if seizure_count >= 5:
            seizure_corr = "high"
        elif seizure_count >= 2:
            seizure_corr = "medium"
        elif seizure_count >= 1:
            seizure_corr = "low"
        else:
            seizure_corr = "none"

        # Determine geographic risk level
        geo_score = geo_risk.get("score", 0)
        if geo_score >= 0.7:
            geo_level = "high"
        elif geo_score >= 0.4:
            geo_level = "medium"
        elif geo_score > 0:
            geo_level = "low"
        else:
            geo_level = "low"

        # Text-image agreement
        agreement = classification.get("text_image_agreement", "none")
        text_image_agree = agreement == "agree"

        signals = {
            "code_word_confidence": code_confidence,
            "cites_appendix": top_species.get("cites_appendix"),
            "iucn_status": top_species.get("iucn_status"),
            "seizure_correlation": seizure_corr,
            "geographic_risk": geo_level,
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": image_evidence,
            "text_image_agreement": text_image_agree,
            "trade_suspension_active": top_species.get("trade_suspension_active", False),
        }

        listing["classification"] = classification
        listing["signals"] = signals
        classified.append(listing)

    return {"classified_listings": classified}


def risk_scorer_node(state: WildScanState) -> dict:
    scored = []
    counts = {"red": 0, "amber": 0, "yellow": 0, "clear": 0}
    for listing in state.get("classified_listings", []):
        signals = listing.get("signals", {})
        result = score_listing(signals)
        listing["risk_result"] = result
        scored.append(listing)
        counts[result["alert_tier"]] = counts.get(result["alert_tier"], 0) + 1
    return {
        "scored_listings": scored,
        "red_count": counts["red"],
        "amber_count": counts["amber"],
        "yellow_count": counts["yellow"],
        "clear_count": counts["clear"],
    }


async def intel_analyst_node(state: WildScanState) -> dict:
    """Generate Claude intelligence briefs for amber/red detections."""
    briefs = []
    for listing in state.get("scored_listings", []):
        risk = listing.get("risk_result", {})
        if risk.get("alert_tier") in ("red", "amber"):
            detection = {
                "platform": listing.get("platform", ""),
                "title_original": listing.get("title", listing.get("title_original", "")),
                "title_translated": listing.get("text_analysis", {}).get("translation", ""),
                "location_text": listing.get("location_text", ""),
                "risk_score": risk.get("risk_score", 0),
                "alert_tier": risk.get("alert_tier", ""),
                "signal_breakdown": risk.get("signal_breakdown", {}),
                "species_matches": listing.get("classification", {}).get("species_matches", []),
                "code_word_matches": listing.get("text_analysis", {}).get("code_word_matches", []),
                "geographic_risk": listing.get("classification", {}).get("geographic_risk", {}),
                "seizure_correlations": listing.get("classification", {}).get("seizure_correlations", []),
                "image_classification": listing.get("image_analysis", {}).get("primary_classification", {}),
            }
            brief = await generate_brief(detection)
            listing["brief"] = brief
            briefs.append(brief)
    return {"briefs_generated": briefs}


def should_generate_brief(state: WildScanState) -> str:
    if state.get("red_count", 0) > 0 or state.get("amber_count", 0) > 0:
        return "intel_analyst"
    return "end"


def build_pipeline() -> StateGraph:
    graph = StateGraph(WildScanState)
    graph.add_node("scanner", scanner_node)
    graph.add_node("triage", triage_node)
    graph.add_node("linguist", linguist_node)
    graph.add_node("image_analyst", image_analyst_node)
    graph.add_node("species_classifier", species_classifier_node)
    graph.add_node("risk_scorer", risk_scorer_node)
    graph.add_node("intel_analyst", intel_analyst_node)
    graph.set_entry_point("scanner")
    graph.add_edge("scanner", "triage")
    graph.add_edge("triage", "linguist")
    graph.add_edge("triage", "image_analyst")
    graph.add_edge("linguist", "species_classifier")
    graph.add_edge("image_analyst", "species_classifier")
    graph.add_edge("species_classifier", "risk_scorer")
    graph.add_conditional_edges("risk_scorer", should_generate_brief, {
        "intel_analyst": "intel_analyst",
        "end": END,
    })
    graph.add_edge("intel_analyst", END)
    return graph.compile()


pipeline = build_pipeline()
