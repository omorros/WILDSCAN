def score_listing(signals: dict) -> dict:
    breakdown = {}

    code_word_scores = {"exact": 15, "fuzzy": 11, "llm_novel": 7, "obfuscation": 11, "none": 0}
    code_word_score = code_word_scores.get(signals.get("code_word_confidence", "none"), 0)
    breakdown["code_word"] = {"score": code_word_score, "max": 15}

    cites_scores = {"I": 25, "II": 15, "III": 8}
    cites_score = cites_scores.get(signals.get("cites_appendix"), 0)
    breakdown["cites"] = {"score": cites_score, "max": 25}

    iucn_scores = {"CR": 12, "EN": 10, "VU": 7, "NT": 3, "LC": 0}
    iucn_score = iucn_scores.get(signals.get("iucn_status"), 0)
    breakdown["iucn"] = {"score": iucn_score, "max": 12}

    seizure_scores = {"high": 13, "medium": 8, "low": 4, "none": 0}
    seizure_score = seizure_scores.get(signals.get("seizure_correlation", "none"), 0)
    breakdown["seizure"] = {"score": seizure_score, "max": 13}

    geo_scores = {"high": 10, "medium": 6, "low": 2, "legal_trade": 0}
    geo_score = geo_scores.get(signals.get("geographic_risk", "low"), 0)
    breakdown["geographic"] = {"score": geo_score, "max": 10}

    seller_scores = {"multiple_wildlife": 10, "cross_platform": 8, "new_account": 5, "established": 0}
    seller_score = seller_scores.get(signals.get("seller_behavior", "established"), 0)
    breakdown["seller"] = {"score": seller_score, "max": 10}

    price_scores = {"within_range": 3, "anomalous": 1, "unknown": 0}
    price_score = price_scores.get(signals.get("price_signal", "unknown"), 0)
    breakdown["price"] = {"score": price_score, "max": 3}

    image_scores = {"high": 12, "medium": 8, "low": 3, "none": 0}
    image_score = image_scores.get(signals.get("image_evidence", "none"), 0)
    breakdown["image"] = {"score": image_score, "max": 12}

    total = (code_word_score + cites_score + iucn_score + seizure_score +
             geo_score + seller_score + price_score + image_score)

    agreement_bonus = 0
    if signals.get("text_image_agreement") and code_word_score > 0 and image_score > 0:
        agreement_bonus = 5

    total = min(total + agreement_bonus, 100)

    hard_override_applied = False
    hard_override_reason = None

    if signals.get("trade_suspension_active"):
        if total < 80:
            total = 80
            hard_override_applied = True
            hard_override_reason = "Active CITES trade suspension for species + country"

    if (signals.get("cites_appendix") == "I" and
            signals.get("geographic_risk") == "high" and
            signals.get("image_evidence") == "high"):
        if total < 65:
            total = 65
            hard_override_applied = True
            hard_override_reason = "Appendix I + source country + image evidence"

    if total >= 80:
        alert_tier = "red"
    elif total >= 60:
        alert_tier = "amber"
    elif total >= 40:
        alert_tier = "yellow"
    else:
        alert_tier = "clear"

    return {
        "risk_score": total,
        "alert_tier": alert_tier,
        "signal_breakdown": breakdown,
        "agreement_bonus": agreement_bonus,
        "hard_override_applied": hard_override_applied,
        "hard_override_reason": hard_override_reason,
    }
