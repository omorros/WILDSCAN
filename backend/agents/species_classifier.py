from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def classify_species(text_analysis: dict, image_analysis: dict, listing: dict, db: AsyncSession) -> dict:
    candidates = []
    for match in text_analysis.get("code_word_matches", []):
        if match.get("species_scientific"):
            candidates.append({"scientific_name": match["species_scientific"], "source_path": "text", "confidence": match.get("confidence", 0.5)})

    img_primary = image_analysis.get("primary_classification", {})
    if img_primary.get("product_detected") and img_primary.get("predicted_species"):
        candidates.append({"scientific_name": img_primary["predicted_species"], "source_path": "image", "confidence": img_primary.get("confidence", 0.5)})

    if not candidates:
        return {
            "species_matches": [],
            "geographic_risk": {"score": 0, "reasoning": "No species identified", "legal_trade_possible": False, "supporting_seizures": 0},
            "seizure_correlations": [],
            "text_image_agreement": "none",
        }

    species_matches = []
    for candidate in candidates:
        row = await db.execute(text("SELECT * FROM species_ref WHERE scientific_name = :name"), {"name": candidate["scientific_name"]})
        species = row.mappings().first()
        if species:
            both = any(c["source_path"] == "text" for c in candidates if c["scientific_name"] == candidate["scientific_name"]) and \
                   any(c["source_path"] == "image" for c in candidates if c["scientific_name"] == candidate["scientific_name"])
            species_matches.append({
                "scientific_name": species["scientific_name"], "common_name": species["common_name"],
                "cites_appendix": species["cites_appendix"], "iucn_status": species["iucn_status"],
                "trade_suspension_active": species["trade_suspension_active"],
                "confidence": candidate["confidence"], "source_path": "both" if both else candidate["source_path"],
            })

    seen = {}
    for sm in species_matches:
        name = sm["scientific_name"]
        if name not in seen or sm["confidence"] > seen[name]["confidence"]:
            seen[name] = sm
    species_matches = list(seen.values())

    seller_country = _extract_country(listing)
    geo_risk = await _compute_geographic_risk(species_matches, seller_country, db)
    seizure_corrs = await _find_seizure_correlations(species_matches, seller_country, db)

    text_species = {c["scientific_name"] for c in candidates if c["source_path"] == "text"}
    image_species = {c["scientific_name"] for c in candidates if c["source_path"] == "image"}
    if text_species and image_species:
        agreement = "agree" if text_species & image_species else "disagree"
    elif text_species:
        agreement = "text_only"
    elif image_species:
        agreement = "image_only"
    else:
        agreement = "none"

    return {"species_matches": species_matches, "geographic_risk": geo_risk, "seizure_correlations": seizure_corrs, "text_image_agreement": agreement}


async def _compute_geographic_risk(species_matches: list[dict], seller_country: str | None, db: AsyncSession) -> dict:
    if not seller_country or not species_matches:
        return {"score": 0, "reasoning": "Unknown seller location", "legal_trade_possible": False, "supporting_seizures": 0}

    top_species = species_matches[0]
    row = await db.execute(
        text("SELECT range_countries, legal_trade_countries, trade_suspension_active, trade_suspension_countries FROM species_ref WHERE scientific_name = :name"),
        {"name": top_species["scientific_name"]},
    )
    species = row.mappings().first()
    if not species:
        return {"score": 0, "reasoning": "Species not in database", "legal_trade_possible": False, "supporting_seizures": 0}

    range_countries = species["range_countries"] or []
    legal_trade = species["legal_trade_countries"] or {}
    suspension_countries = species["trade_suspension_countries"] or []

    seizure_row = await db.execute(
        text("SELECT COUNT(*) as cnt FROM seizure_records sr JOIN species_ref sp ON sr.species_id = sp.id WHERE sp.scientific_name = :name AND sr.seizure_country = :country"),
        {"name": top_species["scientific_name"], "country": seller_country},
    )
    seizure_count = seizure_row.scalar() or 0

    if seller_country in suspension_countries:
        return {"score": 1.0, "reasoning": f"Active trade suspension in {seller_country}", "legal_trade_possible": False, "supporting_seizures": seizure_count}
    if seller_country in range_countries and top_species.get("cites_appendix") == "I":
        return {"score": 0.8, "reasoning": f"CITES I species in source/range country {seller_country}", "legal_trade_possible": False, "supporting_seizures": seizure_count}
    if seizure_count >= 5:
        return {"score": 0.7, "reasoning": f"{seizure_count} prior seizures in {seller_country}", "legal_trade_possible": False, "supporting_seizures": seizure_count}
    if seller_country in range_countries:
        return {"score": 0.5, "reasoning": f"Species found in {seller_country}, moderate risk", "legal_trade_possible": seller_country in list(legal_trade.keys()), "supporting_seizures": seizure_count}
    return {"score": 0.2, "reasoning": f"No specific risk indicators for {seller_country}", "legal_trade_possible": True, "supporting_seizures": seizure_count}


async def _find_seizure_correlations(species_matches: list[dict], seller_country: str | None, db: AsyncSession) -> list[dict]:
    if not species_matches:
        return []
    names = [sm["scientific_name"] for sm in species_matches]
    placeholders = ", ".join(f":name_{i}" for i in range(len(names)))
    params = {f"name_{i}": name for i, name in enumerate(names)}

    query = f"""
        SELECT sr.id, sr.seizure_country, sr.seizure_date, sp.scientific_name, sr.product_type, sr.quantity, sr.quantity_unit, sr.seizure_value_usd
        FROM seizure_records sr JOIN species_ref sp ON sr.species_id = sp.id
        WHERE sp.scientific_name IN ({placeholders})
        ORDER BY sr.seizure_date DESC LIMIT 10
    """
    if seller_country:
        query = f"""
            SELECT sr.id, sr.seizure_country, sr.seizure_date, sp.scientific_name, sr.product_type, sr.quantity, sr.quantity_unit, sr.seizure_value_usd
            FROM seizure_records sr JOIN species_ref sp ON sr.species_id = sp.id
            WHERE sp.scientific_name IN ({placeholders})
            ORDER BY CASE WHEN sr.seizure_country = :seller_country THEN 0 ELSE 1 END, sr.seizure_date DESC LIMIT 10
        """
        params["seller_country"] = seller_country

    rows = await db.execute(text(query), params)
    return [{"seizure_id": str(row["id"]), "country": row["seizure_country"], "date": str(row["seizure_date"]) if row["seizure_date"] else None, "species": row["scientific_name"], "product_type": row["product_type"], "quantity": row["quantity"], "quantity_unit": row["quantity_unit"]} for row in rows.mappings()]


def _extract_country(listing: dict) -> str | None:
    platform = listing.get("platform", "")
    return {"olx.th": "TH", "chotot.com": "VN", "facebook_th": "TH", "facebook_vn": "VN"}.get(platform)
